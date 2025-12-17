from pydantic import BaseModel
from typing import Dict, List, Union, Any, Optional


class VectorRequest(BaseModel):
    user_query: str

class VectorResponse(BaseModel):
    selected_tables: List[str]


class SQLRequest(BaseModel):
    user_api_key: str
    user_query: str
    table_schema: dict[str, list[str] | dict]
    model_id: str = "deepseek-coder-v2:16b"


class RefineSQLRequest(BaseModel):
    generated_sql: str
    error_message: str
    table_schema: Union[Dict[str, List[str]], Dict[str, Any], List[str], str]
    model_id: str = "deepseek-coder-v2:16b"


class SQLResponse(BaseModel):
    sql_query: str
    confidence: float
    tokens_sent: int
    tokens_generated: int
    latency_ms: float
    # model_prompt:str



class TEXTRequest(BaseModel):
    user_api_key: str
    user_query: str
    retrieved_data: Dict[str, Any]
    model_id: str


class TEXTResponse(BaseModel):
    insight: str
    implication: str
    suggestions: List[str]
    evidence: List[str]
    confidence: float
    sent_tokens: int
    generaed_tokens: int
    # model_prompt:str

