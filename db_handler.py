import os
import pyodbc 
import json
from typing import List, Dict, Any, Tuple
from config import DB_CONN_STR
# Load from Env or Config
DB_CONNECTION_STRING = DB_CONN_STR

class DBHandler:
    def __init__(self, connection_string: str = None):
        self.conn_str = connection_string or DB_CONNECTION_STRING
        self.max_rows = 10
        self.char_limit = 12000 # Approx 3000-4000 tokens

    def _get_connection(self):
        if not self.conn_str:
            raise ValueError("Database Connection String is missing. set DB_CONNECTION_STRING env var.")
        return pyodbc.connect(self.conn_str)

    def is_read_only(self, sql: str) -> bool:
        """Simple guardrail to prevent obvious write operations."""
        forbidden = ["INSERT ", "UPDATE ", "DELETE ", "DROP ", "ALTER ", "TRUNCATE ", "CREATE "]
        sql_upper = sql.upper().strip()
        for word in forbidden:
            if sql_upper.startswith(word):
                return False
        return True

    def execute_query(self, sql: str) -> Dict[str, Any]:
        """
        Executes SQL and returns results.
        Applies truncation if rows > 10 or content > char_limit.
        """
        if not self.is_read_only(sql):
            return {"error": "Write operations are not allowed.", "data": []}

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql)
                
                columns = [column[0] for column in cursor.description]
                rows = []
                
                row_count = 0
                is_truncated = False
                
                # Fetch only up to limit + 1 to detect truncation
                # We fetch one extra to know if we need to mark as truncated
                while row_count <= self.max_rows:
                    row = cursor.fetchone()
                    if not row:
                        break
                    
                    # Convert row to dict
                    row_dict = dict(zip(columns, row))
                    
                    # Basic type conversion for JSON serialization (datetime, decimal)
                    for k, v in row_dict.items():
                        if hasattr(v, 'isoformat'): # Dates
                            row_dict[k] = v.isoformat()
                        elif hasattr(v, 'to_eng_string'): # Decimals
                            row_dict[k] = float(v)
                            
                    rows.append(row_dict)
                    row_count += 1
                
                # Check truncation
                if len(rows) > self.max_rows:
                    rows.pop() # Remove the 11th row
                    is_truncated = True
                
                # Check token limit (rough char count)
                json_str = json.dumps(rows, default=str)
                if len(json_str) > self.char_limit:
                    is_truncated = True
                    # If char limit exceeded, we might strictly truncate list further
                    # For now just marking flag, as LLM prompt logic relies on row count mostly
                
                # for row in rows:
                #     print(row)
                    
                return {
                    "data": rows,
                    "row_count": len(rows),
                    "is_truncated": is_truncated,
                    "truncated_reason": "Row limit (10) or Size limit" if is_truncated else None
                }

        except Exception as e:
            return {"error": str(e), "data": []}
