import time
from fastapi import APIRouter, Request
from models import VectorRequest, VectorResponse,  TEXTRequest, TEXTResponse, SQLRequest, SQLResponse, RefineSQLRequest
from prompts import build_sql_prompt, build_text_prompt, build_refine_sql_prompt
from ollama_client import sql_query_ollama_with_client, text_query_ollama_with_client, extract_json
from logger import log_request, log_response
from Gemini_client import sql_query_gemini, text_query_gemini
from config import DEFAULT_MODEL
from vector_store import vector_store

router = APIRouter()
@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.post("/vector_search", response_model=VectorResponse)
async def vector_search(req: VectorRequest, request: Request):

    # -------------------------
    # Log incoming request
    # -------------------------
    log_request({
        "event": "request_received",
        "path": request.url.path,
        "user_query": req.user_query
    })

    start_time = time.time()

    # Perform Vector Search
    try:
        results = vector_store.search(req.user_query)
    except Exception as e:
        # Fallback or error handling
        print(f"Vector search failed: {e}")
        results = []

    latency_ms = round((time.time() - start_time) * 1000, 2)

    # -------------------------
    # Log outgoing response
    # -------------------------
    log_response({
        "event": "response_sent",
        "selected_tables": results,
        "latency_ms": latency_ms
    })

    return VectorResponse(
        selected_tables=results
    )


@router.post("/generate_sql", response_model=SQLResponse)
async def generate_sql(req: SQLRequest, request: Request):

    # -------------------------
    # Log incoming request
    # -------------------------
    log_request({
        "event": "request_received",
        "path": request.url.path,
        "user_api_key": req.user_api_key,
        "user_query": req.user_query,
        "table_schema": req.table_schema
    })

    start_time = time.time()

    prompt = build_sql_prompt(req.user_query, req.table_schema)

    model = req.model_id or DEFAULT_MODEL
   
    result = sql_query_ollama_with_client(prompt, model)
    print("Using Ollama model:", model)
    # result = query_gemini(prompt)  # Use Gemini client
    # print("Using Gemini client")


    sql = result["query"]
    conf = result["confidence"]
    ip_tokens = result["Sent_tokens"]
    op_tokens = result["Generated_tokens"]
    # raw_op = result["raw_output"]

    latency_ms = round((time.time() - start_time) * 1000, 2)

    # -------------------------
    # Log outgoing response
    # -------------------------
    log_response({
        "event": "response_sent",
        "sql_query": sql,
        "confidence": conf,
        "tokens_sent": ip_tokens,
        "tokens_generated": op_tokens,
        "latency_ms": latency_ms
    })

    return SQLResponse(
        sql_query=sql,
        confidence=conf,
        tokens_sent=ip_tokens,
        tokens_generated=op_tokens,
        latency_ms=latency_ms,
        # model_prompt=raw_op
    )



@router.post("/generate_insight", response_model=TEXTResponse)
async def generate_insight(req: TEXTRequest, request: Request):

    # -------------------------
    # Log incoming request
    # -------------------------
    log_request({
        "event": "request_received",
        "path": request.url.path,
        "user_api_key": req.user_api_key,
        "user_query": req.user_query,
        "retreived_data": req.retrieved_data
    })

    start_time = time.time()

    prompt = build_text_prompt(req.user_query, req.retrieved_data)

    model = req.model_id or DEFAULT_MODEL
   
    result = text_query_ollama_with_client(prompt, model)
    print("Using Ollama model:", model)
    # result = query_gemini(prompt)  # Use Gemini client
    # print("Using Gemini client")
    print("Result:", result)

    insight = result["insight"]
    implication = result["implication"]
    suggestions = result["suggestions"]
    evidence = result["evidence"]
    conf = result["confidence"]
    ip_tokens = result["sent_tokens"]
    op_tokens = result["generated_tokens"]
    # raw_op = result["raw_output"]

    latency_ms = round((time.time() - start_time) * 1000, 2)

    # -------------------------
    # Log outgoing response
    # -------------------------
    log_response({
        "event": "response_sent",
        "insight": insight,
        "implication": implication,
        "suggestions": suggestions,
        "evidence": evidence,
        "confidence": conf,
        "tokens_sent": ip_tokens,
        "tokens_generated": op_tokens,
        "latency_ms": latency_ms
    })

    return TEXTResponse(
        insight=insight,
        implication=implication,
        suggestions=suggestions,
        evidence=evidence,
        confidence=conf,
        sent_tokens=ip_tokens,
        generaed_tokens=op_tokens,
        latency_ms=latency_ms,
        # model_prompt=raw_op
    )


@router.post("/Refine_SQL", response_model=SQLResponse)
async def refine_sql(req: RefineSQLRequest, request: Request):

    # -------------------------
    # Log incoming request
    # -------------------------
    log_request({
        "event": "request_received",
        "path": request.url.path,
        "failed_sql": req.generated_sql,
        "error_msg": req.error_message
    })

    start_time = time.time()

    prompt = build_refine_sql_prompt(req.generated_sql, req.error_message, req.table_schema)

    model = req.model_id or "deepseekcoder"
   
    result = sql_query_ollama_with_client(prompt, model)
    print("Using Ollama model (Refine):", model)

    sql = result["query"]
    conf = result["confidence"]
    ip_tokens = result["Sent_tokens"]
    op_tokens = result["Generated_tokens"]

    latency_ms = round((time.time() - start_time) * 1000, 2)

    # -------------------------
    # Log outgoing response
    # -------------------------
    log_response({
        "event": "response_sent",
        "sql_query": sql,
        "confidence": conf,
        "tokens_sent": ip_tokens,
        "tokens_generated": op_tokens,
        "latency_ms": latency_ms
    })

    return SQLResponse(
        sql_query=sql,
        confidence=conf,
        tokens_sent=ip_tokens,
        tokens_generated=op_tokens,
        latency_ms=latency_ms
    )
