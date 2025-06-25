import pdfplumber
import io
import re
import logging
from typing import Dict, Any
from fastapi import HTTPException

from models import FinancialData

logger = logging.getLogger(__name__)

def extract_financials_from_pdf(content: bytes) -> FinancialData:
    """Extract financial data from PDF content"""
    try:
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        
        # Basic financial data extraction (simplified example)
        # In production, you'd use more sophisticated parsing
        financials = FinancialData()
        
        # Extract revenue, EBITDA, net income using regex patterns
        revenue_pattern = r'revenue[:\s]+\$?([0-9,]+(?:\.[0-9]+)?)'
        ebitda_pattern = r'ebitda[:\s]+\$?([0-9,]+(?:\.[0-9]+)?)'
        net_income_pattern = r'net\s+income[:\s]+\$?([0-9,]+(?:\.[0-9]+)?)'
        
        revenue_matches = re.findall(revenue_pattern, text.lower())
        ebitda_matches = re.findall(ebitda_pattern, text.lower())
        net_income_matches = re.findall(net_income_pattern, text.lower())
        
        # Simplified data structure (in production, extract by year)
        if revenue_matches:
            financials.income_statement["2023"] = {
                "revenue": float(revenue_matches[0].replace(',', '')),
                "ebitda": float(ebitda_matches[0].replace(',', '')) if ebitda_matches else 0,
                "net_income": float(net_income_matches[0].replace(',', '')) if net_income_matches else 0
            }
        
        return financials
    except Exception as e:
        logger.error(f"PDF parsing error: {str(e)}")
        raise HTTPException(status_code=422, detail=f"PDF parsing failed: {str(e)}")
