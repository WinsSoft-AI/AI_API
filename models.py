from pydantic import BaseModel
from typing import Dict, List, Any, Optional

class SQLRequest(BaseModel):
    # user_api_key: str
    user_query: str
    # table_schema removed; will be loaded internally based on intent
    model_id: str = "llama3.2:latest"

class SQLResponse(BaseModel):
    sql_query: str
    # confidence: float
    module: str  # Added module to response to show what was detected
    tokens_sent: int
    tokens_generated: int
    latency_ms: float

class TEXTRequest(BaseModel):
    # user_api_key: str
    user_query: str
    retrieved_data: Dict[str, Any]
    model_id: str = "llama3.2:latest"

class TEXTResponse(BaseModel):
    insight: str
    greeting: str
    suggestions: List[str]
    evidence: List[str]
    confidence: float
    sent_tokens: int
    generaed_tokens: int
