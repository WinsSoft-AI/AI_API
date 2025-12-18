from fastapi import FastAPI
from routes.sql_generator import router

from contextlib import asynccontextmanager
import ollama_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Warmup: Trigger a small request to load the model into memory
    print("Warming up LLM model...")
    try:
        # Use a dummy prompt with the default model
        ollama_client.sql_query_ollama_with_client("SELECT 1", "llama3.2:latest")
        print("LLM Model Warmup Complete.")
    except Exception as e:
        print(f"Warning: Model warmup failed: {e}")
    yield

app = FastAPI(
    title="SQL and Text Generator Backend",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(router)

@app.get("/")
def root():
    return {"message": "SQL and Text Generator Backend Running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=9000
    )   
