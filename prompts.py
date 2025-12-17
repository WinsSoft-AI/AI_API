import json
from typing import List, Dict, Any

def build_sql_prompt(user_query: str, table_schema):
    """
    Build a clean, structured SQL generation prompt for LLMs.
    Supports dict-structured schemas and plain text schemas.
    """

    # -------------------------
    # Format table schema
    # -------------------------
    schema_text = ""

    # Case 1: schema = dict { "table": [cols...] }
    if isinstance(table_schema, dict):
        schema_lines = ["Database Schema:"]
        for table_name, columns in table_schema.items():
            col_list = ", ".join(columns)
            schema_lines.append(f"- {table_name}({col_list})")
        schema_text = "\n".join(schema_lines)

    # Case 2: schema is already a string
    elif isinstance(table_schema, str):
        schema_text = f"Database Schema:\n{table_schema}"

    # -------------------------
    # Build final prompt
    # -------------------------
    prompt = f"""
You are an enterprise-grade SQL generation engine specialized in Microsoft SQL Server (T-SQL).
Your task is to produce correct, schema-faithful, and executable SQL queries based strictly
on the user question and the provided schema.

OUTPUT RULES:
1. Your ENTIRE output must be a valid JSON object with EXACTLY:
      "query": <SQL string>,
      "confidence": <0–1>

2. SQL REQUIREMENTS (T-SQL ONLY):
   - Use ONLY tables and columns that exist in the schema.
   - ALWAYS infer correct JOIN conditions using matching key names.
       Example: orders.customer_id = customers.customer_id
   - ALWAYS use SQL Server date functions:
       - GETDATE()
       - DATEADD(unit, value, date)
       - DATEDIFF(unit, start, end)
   - NEVER use MySQL or PostgreSQL syntax:
       - NO DATE_SUB
       - NO INTERVAL '6 months'
       - NO LIMIT (use TOP or OFFSET/FETCH)
   - Use explicit table aliases (t1, t2, t3)
   - Ensure all non-aggregated columns appear in GROUP BY.
   - Ensure final SQL is full T-SQL compliant.

3. When multiple tables are needed,
   AUTOMATICALLY determine JOINs based on shared key names.

4. If the question cannot be answered from the schema:
      return:
      {{
        "query": "",
        "confidence": 0.0
      }}

5. DO NOT:
   - Output explanations
   - Output comments
   - Output Markdown
   - Output anything except the JSON object

CONFIDENCE RULES:
- 1.0 = SQL is complete and correct.
- 0.5–0.9 = Partial confidence.
- 0.0 = Insufficient schema or ambiguous.

SCHEMA:
{schema_text}

QUESTION:
{user_query}

Return ONLY the JSON object.
"""

    return prompt.strip()



def build_text_prompt(user_query: str, retrieved_data: Dict[str, Any]) -> str:
    """
    Builds a strict-schema insight engine prompt.
    
    user_query: str
       The natural-language business question.
    
    retrieved_data: dict
       The JSON dictionary returned by your backend (query results).
    """

    # Convert dict to pretty JSON (no extra quotes)
    data_json_str = json.dumps(retrieved_data, indent=2)

    prompt = f"""
You are an enterprise-grade business insight engine with strict schema validation.
Your task is to generate concise insights strictly from the provided JSON payload.

USER QUERY:
"{user_query}"

DATA JSON:
{data_json_str}

OUTPUT RULES:
1. Your ENTIRE output must be a valid JSON object with EXACTLY these keys:
      "insight": <string>,
      "implication": <string>,
      "suggestions": [<string>, <string>, <string>],
      "evidence": [<string>, ...],
      "confidence": <0–1>

2. VALIDATION CONSTRAINTS:
   - If ANY required key is missing in your output, or if any additional key appears,
     you MUST instead return:
       {{
         "insight": "",
         "implication": "",
         "suggestions": ["", "", ""],
         "evidence": [],
         "confidence": 0.0
       }}
   - "suggestions" must contain exactly 3 items.
   - "confidence" must be a number from 0 to 1.
   - All content must be directly supported by the input JSON.

3. CONTENT RULES:
   - Never invent numbers, fields, or trends not present in the data.
   - Keep “insight” + “implication” under 60 words total.
   - Do not reveal chain-of-thought or internal reasoning.
   - Evidence must list only direct key/value pairs from the input JSON.

4. FAILURE CONDITIONS (return confidence = 0.0 JSON):
   - Missing data required to answer.
   - Ambiguous interpretation.
   - Any deviation from the exact schema.

5. DO NOT:
   - Output explanations.
   - Output Markdown.
   - Output comments.
   - Output anything except the JSON object.

Now produce the final JSON output strictly following the schema.
"""

    return prompt.strip()



def build_refine_sql_prompt(sql_query: str, error: str, table_schema: Any) -> str:
    """
    Builds a prompt to fix a failed SQL query based on the error message.
    """
    # Reuse schema formatting logic from build_sql_prompt (simplified duplication for now or call if refactored)
    
    schema_text = ""
    if isinstance(table_schema, dict):
        schema_lines = ["Database Schema:"]
        for table_name, columns in table_schema.items():
            if isinstance(columns, list):
                col_list = ", ".join(columns)
                schema_lines.append(f"- {table_name}({col_list})")
            else:
                 schema_lines.append(f"- {table_name}({str(columns)})")
        schema_text = "\n".join(schema_lines)
    elif isinstance(table_schema, str):
        schema_text = f"Database Schema:\n{table_schema}"

    prompt = f"""
You are an expert MS SQL Server (T-SQL) debugger. 
Your goal is to FIX a failed SQL query based on the provided error message.

DATABASE SCHEMA:
{schema_text}

INCORRECT SQL:
{sql_query}

ERROR MESSAGE:
{error}

INSTRUCTIONS:
0. You may ONLY use table names and column names explicitly present in DATABASE SCHEMA.
   - You MUST NOT invent, infer, or assume any column or table.
   - If the error cannot be fixed without guessing a column, DO NOT generate SQL.

1. Analyze the error message and the schema.
2. Fix the SQL query to resolve the error.
3. Ensure the fixed query is valid T-SQL.
4. Return the result in the EXACT same JSON format as the original generation.

5. If fixing the query requires a column that does NOT exist in the schema:
   - Do NOT guess or substitute a similar column.
   - Return an empty query string and set confidence to 0.0.

6. Confidence rules:
   - 1.0 only if the fix is fully schema-verified.
   - < 0.8 if the fix involved uncertainty or partial inference.
   - 0.0 if the query cannot be fixed safely.

OUTPUT RULES:
- Return ONLY a valid JSON object.
- Format:
  {{
    "query": <FIXED_SQL_STRING>,
    "confidence": <0.0 - 1.0>
  }}
- If no safe fix is possible, return:
  {{
    "query": "",
    "confidence": 0.0
  }}
- NO prose, NO markdown, NO comments.

"""
    return prompt.strip()