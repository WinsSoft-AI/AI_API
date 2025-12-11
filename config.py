import os
from dotenv import load_dotenv

load_dotenv()


DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "llama3.2:latest")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyBhfOnZvzN32Y6RR3I4HNjoEBbB02VuYiM")