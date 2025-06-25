from typing import Dict, Any, Optional
from pydantic import BaseModel

class FinancingMix(BaseModel):
    equity_percent: float
    debt_percent: float

class Synergies(BaseModel):
    annual_savings: float
    duration_years: int

class DealTerms(BaseModel):
    deal_value: float
    financing_mix: FinancingMix
    synergies: Synergies
    premium: float

class AcquisitionRequest(BaseModel):
    acquirer_data: Dict[str, Any]
    target_data: Dict[str, Any]
    deal_terms: DealTerms

class KeyMetrics(BaseModel):
    eps_accretion: str
    debt_added: float
    new_shares_issued: float
    ev_ebitda_multiple: Optional[float] = None
    pe_multiple: Optional[float] = None

class AcquisitionResponse(BaseModel):
    pro_forma_financials: Dict[str, Any]
    key_metrics: KeyMetrics
