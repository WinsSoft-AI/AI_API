from pydantic import BaseModel
from typing import Dict, List, Any, Optional, Union

class SQLRequest(BaseModel):
    # user_api_key: str
    user_query: str
    # table_schema removed; will be loaded internally based on intent
    model_id: str = "phi3:mini"

class SQLResponse(BaseModel):
    sql_query: str
    # confidence: float
    module: str  # Added module to response to show what was detected
    tokens_sent: int
    tokens_generated: int
    tokens_generated: int
    latency_ms: float

class ExecuteSQLRequest(BaseModel):
    sql_query: str

class ExecuteSQLResponse(BaseModel):
    data: List[Dict[str, Any]]
    row_count: int
    is_truncated: bool
    truncated_reason: Optional[str] = None
    error: Optional[str] = None

class TEXTRequest(BaseModel):
    # user_api_key: str
    user_query: str
    retrieved_data: Union[Dict[str, Any], List[Dict[str, Any]]]
    is_truncated: bool = False
    model_id: str = "llama3.2:latest"

class TEXTResponse(BaseModel):
    insight: str
    greeting: str
    suggestions: List[str]
    evidence: List[str]
    confidence: float
    sent_tokens: int
    generaed_tokens: int
