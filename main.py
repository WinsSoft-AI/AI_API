from fastapi import FastAPI
from routes.sql_generator import router
import prompts # Lazy import or top level
import ollama_client
from db_handler import DBHandler
from models import ExecuteSQLRequest, ExecuteSQLResponse, TEXTRequest, TEXTResponse
from contextlib import asynccontextmanager

# Initialize DB Handler
DB_EXEC = DBHandler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Warmup: Trigger a small request to load the model into memory
    print("Warming up LLM model...")
    try:
        # Use a dummy prompt with the default model
        print("loading llama3.2")
        ollama_client.sql_query_ollama_with_client("Convert this to caps and only return this - hi", "llama3.2:latest")
        print("loading gpt-oss")
        ollama_client.sql_query_ollama_with_client("Convert this to caps and only return this - hi", "gpt-oss:20b")
        print("loading mistral")
        ollama_client.sql_query_ollama_with_client("Convert this to caps and only return this - hi", "mistral:7b")
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

@app.post("/execute-sql", response_model=ExecuteSQLResponse)
def execute_sql_endpoint(request: ExecuteSQLRequest):
    """
    Executes the SQL query and returns raw data (truncated if necessary).
    """
    result = DB_EXEC.execute_query(request.sql_query)
    
    # DBHandler returns dict with data/error. Map to Pydantic.
    return ExecuteSQLResponse(
        data=result.get("data", []),
        row_count=result.get("row_count", 0),
        is_truncated=result.get("is_truncated", False),
        truncated_reason=result.get("truncated_reason"),
        error=result.get("error")
    )

@app.post("/generate-text", response_model=TEXTResponse)
def generate_text_endpoint(request: TEXTRequest):
    """
    Generates insights from the provided (raw/truncated) data.
    """
    print(request)

    
    # 1. Build Prompt with Truncation Check
    full_prompt = prompts.build_text_prompt(
        request.user_query, 
        request.retrieved_data, 
        is_truncated=request.is_truncated
    )
    
    # 2. Generate
    response = ollama_client.text_query_ollama_with_client(full_prompt, model=request.model_id)
    print(response)
    
    # 3. Handle Fallback/Error
    if not response:
        return TEXTResponse(
            insight="Could not generate insights.",
            greeting="System Error",
            confidence=0.0,
            sent_tokens=0,
            generated_tokens=0
        )
        
    return TEXTResponse(
        insight=response.get("insight", ""),
        greeting=response.get("greeting", ""),
        confidence=float(response.get("confidence", 0.0)),
        sent_tokens=response.get("sent_tokens", 0),
        generated_tokens=response.get("generated_tokens", 0)
    )

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
