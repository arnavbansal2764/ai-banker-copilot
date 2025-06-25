import pandas as pd
import io
import logging
from typing import Dict, Any
from fastapi import HTTPException

from models import FinancialData

logger = logging.getLogger(__name__)

def extract_financials_from_excel(content: bytes) -> FinancialData:
    """Extract financial data from Excel content"""
    try:
        df = pd.read_excel(io.BytesIO(content))
        
        # Standardize column names
        df.columns = df.columns.str.lower().str.strip()
        
        financials = FinancialData()
        
        # Similar logic to CSV parsing
        for index, row in df.iterrows():
            year = None
            if 'year' in df.columns:
                year = str(int(row['year']))
            elif any(str(col).isdigit() for col in df.columns):
                year_cols = [col for col in df.columns if str(col).isdigit()]
                if year_cols:
                    year = str(year_cols[0])
            
            if year:
                income_data = {}
                if 'revenue' in df.columns:
                    income_data['revenue'] = float(row.get('revenue', 0))
                if 'ebitda' in df.columns:
                    income_data['ebitda'] = float(row.get('ebitda', 0))
                if 'net_income' in df.columns or 'net income' in df.columns:
                    income_data['net_income'] = float(row.get('net_income', row.get('net income', 0)))
                
                if income_data:
                    financials.income_statement[year] = income_data
                    break
        
        return financials
    except Exception as e:
        logger.error(f"Excel parsing error: {str(e)}")
        raise HTTPException(status_code=422, detail=f"Excel parsing failed: {str(e)}")
