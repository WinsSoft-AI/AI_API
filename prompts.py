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
        ROLE
        You are an expert Microsoft SQL Server (T-SQL) query generator.

        OBJECTIVE
        Convert the user’s business question into a valid, executable T-SQL SELECT query.

        OUTPUT FORMAT
        - Output ONLY the SQL query
        - Do NOT include explanations, comments, or markdown

        MANDATORY RULES
        1. Generate ONLY a SELECT statement
        2. NEVER generate INSERT, UPDATE, DELETE, DROP, or ALTER
        3. Use ONLY the tables and columns explicitly listed in the schema
        4. Do NOT invent tables or columns
        5. Do NOT use JOINs
        6. Use SQL Server–supported date functions only:
        GETDATE(), DATEADD(), DATEDIFF(), YEAR(), MONTH()
        7. NEVER use PostgreSQL/MySQL syntax:
        EXTRACT(), INTERVAL, DATE_SUB(), LIMIT
        8. Use TOP instead of LIMIT when required
        9. Use correct GROUP BY rules for aggregate queries

        DATE LOGIC RULES
        - For “last month”, “this month”, etc., prefer date-range filtering using:
        DATEADD + DATEDIFF
        - Do NOT apply YEAR() or MONTH() to non-date values

        SCHEMA (AUTHORITATIVE — DO NOT QUESTION)
        {schema_text}

        USER QUESTION
        {user_query}

        FINAL INSTRUCTION
        Return ONLY the final T-SQL SELECT query.
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
        You are an enterprise ERP business insight engine.

        USER QUERY:
        "{user_query}"

        DATA (AUTHORITATIVE, DO NOT QUESTION):
        {data_json_str}

        OUTPUT FORMAT (STRICT JSON ONLY):
        {{
        "insight": "<2–3 lines describing what the data shows>",
        "greeting": "<1 line encouraging or neutral progress message>",
        "suggestions": ["<action 1>", "<action 2>", "<action 3>"],
        "evidence": ["<key:value from data>", "..."],
        "confidence": <number between 0 and 1>
        }}

        STRICT RULES:
        - Use ONLY the provided data
        - Do NOT invent numbers or trends
        - suggestions MUST have exactly 3 items
        - If data is insufficient or ambiguous, return:
        {{
            "insight": "",
            "greeting": "",
            "suggestions": ["", "", ""],
            "evidence": [],
            "confidence": 0.0
        }}
        - Do NOT output explanations, markdown, or comments

        Now produce the JSON output.
        """

    return prompt.strip()

