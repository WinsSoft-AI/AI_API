import os
from dotenv import load_dotenv

load_dotenv()


DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-oss:20b")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyBhfOnZvzN32Y6RR3I4HNjoEBbB02VuYiM")
DB_CONN_STR = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=WSCRSERVER\WINSSOFTSQL2022;"
    "DATABASE=WSHTERPSDB2021;"
    "UID=winssofterp;"
    "PWD=WsUser!@#37;"
)