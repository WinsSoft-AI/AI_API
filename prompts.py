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
        10. Use only the column names provided in the schema
        11. For time-based queries, ALWAYS use date-range filtering with DATEADD + DATEDIFF and NEVER use YEAR() or MONTH() comparisons.


        DATE LOGIC RULES
        - For “last month”, “this month”, etc., prefer date-range filtering using DATEADD + DATEDIFF
        - Do NOT apply YEAR() or MONTH() to non-date values

        SCHEMA (AUTHORITATIVE — DO NOT QUESTION)
        {schema_text}

        USER QUESTION
        {user_query}

        FINAL INSTRUCTION
        Return ONLY the final T-SQL SELECT query.
        """


    return prompt.strip()




def build_text_prompt(user_query: str, retrieved_data: Dict[str, Any], is_truncated: bool = False) -> str:
    """
    Builds a strict-schema insight engine prompt.
    
    user_query: str
    retrieved_data: dict
    is_truncated: bool (If true, warn LLM that data is partial)
    """

    # Convert dict to pretty JSON (no extra quotes)
    data_json_str = json.dumps(retrieved_data, indent=2)
    
    # Check for Empty Data
    is_empty = False
    if not retrieved_data:
        is_empty = True
    elif isinstance(retrieved_data, list) and not retrieved_data:
        is_empty = True
    elif isinstance(retrieved_data, dict):
        # If specific "results" key exists, check if THAT is empty
        if "results" in retrieved_data:
             if not retrieved_data["results"]:
                 is_empty = True
        # If just a plain dict with keys, it's NOT empty (handled by first 'if not retrieved_data')
    
    # Debug print to confirm status
    # print(f"DEBUG: Data Valid? {not is_empty} (Input: {str(retrieved_data)[:50]}...)")

    truncation_note = ""
    if is_truncated:
        truncation_note = "(NOTE: This data is TRUNCATED. It only shows the top rows.)"

    empty_instruction = ""
    if is_empty:
        empty_instruction = """
        CRITICAL: The dataset is EMPTY. 
        - State clearly that "No detailed records were found for this specific query."
        - Provide a generalized explanation or context about what this data usually represents.
        - Do NOT make up specific numbers.
        """

    prompt = f"""
        You are an enterprise ERP business insight engine.

        USER QUERY:
        "{user_query}"

        DATA STATUS:
        {'[EMPTY DATASET]' if is_empty else '[DATA VALID]'}
        {truncation_note}

        DATA (AUTHORITATIVE):
        {data_json_str}

        {empty_instruction}

        OUTPUT FORMAT (STRICT JSON ONLY):
        {{
        "insight": "<Multiple key points each in 2–3 lines well explained and analyzed but keep the context in the ERP and the user query in mind. If empty, explain why/generic context. If valid, analyze data.>",
        "greeting": "<Polite message. If empty, explain why/generic context. If valid, analyze data and greet for his success and motivate for his next steps. >",
        "confidence": <number between 0 and 1>
        }}

        STRICT RULES:
        - Use ONLY the provided data
        - Do NOT invent numbers or trends
        - Do NOT output explanations, markdown, or comments

        Now produce the JSON output.
        """

    return prompt.strip()

