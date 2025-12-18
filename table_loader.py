import json
import os
from typing import Dict, List, Any

def load_tables(directory: str) -> Dict[str, List[Dict[str, Any]]]:
    tables_by_module = {}
    if not os.path.exists(directory):
        print(f"Warning: Directory {directory} not found.")
        return tables_by_module

    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            filepath = os.path.join(directory, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    table_meta = json.load(f)
                module = table_meta.get("module")
                if module:
                    if module not in tables_by_module:
                        tables_by_module[module] = []
                    tables_by_module[module].append(table_meta)
            except Exception as e:
                print(f"Error reading {filename}: {e}")
    return tables_by_module
