from fastapi import APIRouter, HTTPException
import time
import os
import sys
from datetime import datetime
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import SQLRequest, SQLResponse
import ollama_client
import prompts
import intent
import table_loader

router = APIRouter()

# ---------------- CONFIG ----------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "Table_data")

TABLES_CACHE = table_loader.load_tables(DATA_DIR)
INTENT_PARSER = intent.IntentParser()

MAIN_TABLE_PRIORITY = [
    "T_Ord_Main",
    "T_Invoice_Main",
    "Purchase_Yarn_Bill_Receipt_Main_New",
    "Accessories_Pur_Bill",
    "T_M_Party"
]

DETAIL_KEYWORDS = [
    "detail", "details", "line item", "breakup", "item wise", "item-wise"
]
SQL_KEYWORDS = {
    "select", "from", "where", "and", "or", "group", "by", "order",
    "count", "sum", "avg", "min", "max", "top", "distinct",
    "dateadd", "datediff", "getdate", "year", "month",
    "as", "on", "inner", "left", "right"
}
def get_allowed_columns(table_meta: dict) -> set:
    """
    Build allowed column set from Table_data metadata.
    """
    return {col["name"].lower() for col in table_meta.get("columns", [])}





def extract_column_names_from_sql(sql: str, table_name: str) -> set:
    sql = sql.lower()

    # 1. Keep only SQL part (strip echoed prompt)
    idx = sql.find("select")
    if idx != -1:
        sql = sql[idx:]

    # 2. Remove string literals
    sql = re.sub(r"'[^']*'", "", sql)

    # 3. Remove aliases:  AS alias_name
    sql = re.sub(r"\bas\s+[a-z_][a-z0-9_]*", "", sql)

    # 4. Remove schema and table names
    sql = re.sub(r"\bdbo\.", "", sql)
    sql = re.sub(rf"\b{table_name.lower()}\b", "", sql)

    # 5. Remove numbers
    sql = re.sub(r"\b\d+\b", "", sql)

    # 6. Tokenize
    tokens = re.findall(r"[a-z_][a-z0-9_]*", sql)

    columns = set()
    for token in tokens:
        if token in SQL_KEYWORDS:
            continue
        columns.add(token)

    return columns


print(f"[INIT] Loaded {sum(len(v) for v in TABLES_CACHE.values())} tables.")

# ---------------- HELPERS ----------------
def select_main_table(tables):
    for name in MAIN_TABLE_PRIORITY:
        for t in tables:
            if t["table_name"] == name:
                return t
    return tables[0]


def needs_detail_table(query: str) -> bool:
    q = query.lower()
    return any(k in q for k in DETAIL_KEYWORDS)




# ---------------- ENDPOINT ----------------
@router.post("/generate-sql", response_model=SQLResponse)
async def generate_sql_endpoint(request: SQLRequest):
    start_time = time.time()

    # 1. Detect Module
    module = INTENT_PARSER.get_intent(request.user_query)
    if not module:
        raise HTTPException(400, "Could not detect business module")

    tables = TABLES_CACHE.get(module, [])
    if not tables:
        raise HTTPException(404, f"No tables found for module: {module}")

    # 2. Select Tables
    main_table = select_main_table(tables)
    selected_tables = [main_table]

    if needs_detail_table(request.user_query):
        for t in tables:
            if t != main_table and "detail" in t["table_name"].lower():
                selected_tables.append(t)
                break  # demo-safe: only one detail table

    # 3. Build MINIMAL schema text
    schema_lines = []
    for t in selected_tables:
        cols = ", ".join(c["name"] for c in t.get("columns", []))
        schema_lines.append(f"{t['schema']}.{t['table_name']} ({cols})")

    schema_text = "\n".join(schema_lines)

    # 4. Prepare user query (NO SQL LOGIC LEAK)
    final_query = request.user_query
    current_time = datetime.now().strftime("%Y-%m-%d")
    final_query += f" [Current date: {current_time}]"

    # 5. Build SQL Prompt
    prompt = prompts.build_sql_prompt(final_query, schema_text)

    # (Optional debug)
    with open("prompt.txt", "w", encoding="utf-8") as f:
        f.write(prompt)

    # 6. Call Ollama
    resp = ollama_client.sql_query_ollama_with_client(
        prompt,
        model=request.model_id
    )

    sql = resp.get("query", "").strip()

    # 7. Apply Role Filter AFTER SQL generation
    role_filter = INTENT_PARSER.detect_role_filter(request.user_query)
    if role_filter and "T_M_Party" in sql:
        if "where" in sql.lower():
            sql += f" AND {role_filter}"
        else:
            sql += f" WHERE {role_filter}"

    # 8. SQL SAFETY GUARD
    if not sql.lower().startswith("select"):
        sql = f"SELECT TOP 100 * FROM {main_table['schema']}.{main_table['table_name']}"
    

    print(sql)

    

    # 9. Column Validation (Schema Guard)
    # allowed_columns = get_allowed_columns(main_table)

    # used_columns = extract_column_names_from_sql(
    #     sql,
    #     main_table["table_name"]
    # )

    # invalid_columns = used_columns - allowed_columns

    # if invalid_columns:
    #     raise HTTPException(
    #         status_code=400,
    #         detail=f"Invalid column(s) detected in SQL: {', '.join(invalid_columns)}"
    #     )

    latency_ms = (time.time() - start_time) * 1000


    return SQLResponse(
        sql_query=sql,
        module=module,
        tokens_sent=resp.get("Sent_tokens", 0),
        tokens_generated=resp.get("Generated_tokens", 0),
        latency_ms=latency_ms
    )
