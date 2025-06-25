from typing import Dict, Any
from pydantic import BaseModel

class FinancialData(BaseModel):
    income_statement: Dict[str, Any] = {}
    balance_sheet: Dict[str, Any] = {}
    cash_flow: Dict[str, Any] = {}

class CompanyFinancials(BaseModel):
    company: str
    income_statement: Dict[str, Any] = {}
    balance_sheet: Dict[str, Any] = {}
    cash_flow: Dict[str, Any] = {}
