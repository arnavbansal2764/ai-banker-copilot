import logging
from typing import Dict, Any
from models.deal_models import AcquisitionRequest, AcquisitionResponse, KeyMetrics

logger = logging.getLogger(__name__)

class AcquisitionAnalyzer:
    def __init__(self):
        self.logger = logger

    def analyze_acquisition(self, request: AcquisitionRequest) -> AcquisitionResponse:
        """Analyze acquisition and generate pro-forma financials"""
        try:
            # Extract latest year data for both companies
            acquirer_latest = self._get_latest_year_data(request.acquirer_data)
            target_latest = self._get_latest_year_data(request.target_data)
            
            # Calculate financing breakdown
            debt_financing = request.deal_terms.deal_value * (request.deal_terms.financing_mix.debt_percent / 100)
            equity_financing = request.deal_terms.deal_value * (request.deal_terms.financing_mix.equity_percent / 100)
            
            # Generate pro-forma financials
            pro_forma = self._generate_pro_forma(
                acquirer_latest, 
                target_latest, 
                request.deal_terms,
                debt_financing
            )
            
            # Calculate key metrics
            key_metrics = self._calculate_key_metrics(
                acquirer_latest,
                target_latest,
                request.deal_terms,
                debt_financing,
                equity_financing
            )
            
            return AcquisitionResponse(
                pro_forma_financials=pro_forma,
                key_metrics=key_metrics
            )
            
        except Exception as e:
            self.logger.error(f"Acquisition analysis error: {str(e)}")
            raise

    def _get_latest_year_data(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract the most recent year's financial data"""
        income_statement = company_data.get("income_statement", {})
        if not income_statement:
            return {}
        
        # Get the latest year (assuming sorted or get max year)
        latest_year = max(income_statement.keys()) if income_statement else "2023"
        return income_statement.get(latest_year, {})

    def _generate_pro_forma(self, acquirer: Dict[str, Any], target: Dict[str, Any], 
                           deal_terms, debt_financing: float) -> Dict[str, Any]:
        """Generate combined pro-forma financial statements"""
        
        # Combined revenue
        combined_revenue = acquirer.get("revenue", 0) + target.get("revenue", 0)
        
        # Combined EBITDA with synergies
        combined_ebitda = (
            acquirer.get("ebitda", 0) + 
            target.get("ebitda", 0) + 
            deal_terms.synergies.annual_savings
        )
        
        # Estimate interest expense on new debt (assuming 5% rate)
        new_interest_expense = debt_financing * 0.05
        
        # Combined net income (simplified calculation)
        combined_net_income = (
            acquirer.get("net_income", 0) + 
            target.get("net_income", 0) + 
            deal_terms.synergies.annual_savings - 
            new_interest_expense
        )
        
        return {
            "2024_pro_forma": {
                "revenue": combined_revenue,
                "ebitda": combined_ebitda,
                "net_income": combined_net_income,
                "interest_expense": new_interest_expense,
                "synergies_realized": deal_terms.synergies.annual_savings
            }
        }

    def _calculate_key_metrics(self, acquirer: Dict[str, Any], target: Dict[str, Any],
                              deal_terms, debt_financing: float, equity_financing: float) -> KeyMetrics:
        """Calculate key deal metrics"""
        
        # Estimate shares outstanding (simplified - assume $50 per share)
        assumed_share_price = 50.0
        new_shares_issued = equity_financing / assumed_share_price
        
        # Estimate existing shares (simplified)
        existing_shares = 100_000_000  # Placeholder
        
        # Calculate EPS impact (simplified)
        acquirer_net_income = acquirer.get("net_income", 0)
        target_net_income = target.get("net_income", 0)
        synergies = deal_terms.synergies.annual_savings
        interest_cost = debt_financing * 0.05
        
        # Pro-forma net income
        pro_forma_ni = acquirer_net_income + target_net_income + synergies - interest_cost
        
        # Pro-forma EPS
        total_shares = existing_shares + new_shares_issued
        pro_forma_eps = pro_forma_ni / total_shares
        
        # Standalone EPS
        standalone_eps = acquirer_net_income / existing_shares
        
        # EPS accretion/dilution
        eps_impact = ((pro_forma_eps - standalone_eps) / standalone_eps) * 100
        eps_accretion = f"{eps_impact:.1f}%"
        
        # Calculate multiples
        target_ebitda = target.get("ebitda", 1)  # Avoid division by zero
        ev_ebitda = deal_terms.deal_value / target_ebitda if target_ebitda > 0 else None
        
        target_ni = target.get("net_income", 1)
        pe_multiple = deal_terms.deal_value / target_ni if target_ni > 0 else None
        
        return KeyMetrics(
            eps_accretion=eps_accretion,
            debt_added=debt_financing,
            new_shares_issued=new_shares_issued,
            ev_ebitda_multiple=ev_ebitda,
            pe_multiple=pe_multiple
        )
