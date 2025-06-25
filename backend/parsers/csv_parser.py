import pandas as pd
import io
import logging
from typing import Dict, Any
from fastapi import HTTPException

from models import FinancialData

logger = logging.getLogger(__name__)

def extract_financials_from_csv(content: bytes) -> FinancialData:
    """Extract financial data from CSV content"""
    try:
        df = pd.read_csv(io.BytesIO(content))
        
        # Standardize column names
        df.columns = df.columns.str.lower().str.strip()
        
        financials = FinancialData()
        
        # Look for common financial statement columns
        for index, row in df.iterrows():
            year = None
            # Try to find year in first column or row
            if 'year' in df.columns:
                year = str(int(row['year']))
            elif any(col for col in df.columns if str(col).isdigit()):
                year = str(df.columns[1])  # Assume second column is year
            
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
        logger.error(f"CSV parsing error: {str(e)}")
        raise HTTPException(status_code=422, detail=f"CSV parsing failed: {str(e)}")
