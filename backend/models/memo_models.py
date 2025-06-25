from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from enum import Enum

class MemoFormat(str, Enum):
    MARKDOWN = "markdown"
    HTML = "html"
    JSON = "json"

class DealSummary(BaseModel):
    acquirer: str
    target: str
    deal_value: float
    structure: str

class MemoRequest(BaseModel):
    deal_summary: DealSummary
    strategic_rationale: str
    financials: Dict[str, Any]
    synergies: Dict[str, Any]
    risks: List[str]
    format: Optional[MemoFormat] = MemoFormat.MARKDOWN

class MemoResponse(BaseModel):
    memo: str
    format: MemoFormat
    word_count: Optional[int] = None
