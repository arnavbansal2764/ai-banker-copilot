from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
import logging

from parsers import extract_financials_from_pdf, extract_financials_from_csv, extract_financials_from_excel
from models import CompanyFinancials, AcquisitionRequest, AcquisitionResponse, MemoRequest, MemoResponse
from services import AcquisitionAnalyzer, MemoGenerator

app = FastAPI(title="AI Banker Copilot", version="1.0.0")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize services
acquisition_analyzer = AcquisitionAnalyzer()
memo_generator = MemoGenerator()

@app.post("/upload_financials")
async def upload_financials(
    file: UploadFile = File(...),
    company_name: str = Form(...)
):
    """
    Upload and parse financial documents (PDF, CSV, Excel) for companies.
    
    Returns structured financial data including income statement, balance sheet, and cash flow.
    """
    try:
        # Read file content
        content = await file.read()
        
        # Determine file format and parse accordingly
        file_extension = file.filename.lower().split('.')[-1] if file.filename else ''
        
        if file_extension == 'pdf':
            financials = extract_financials_from_pdf(content)
        elif file_extension == 'csv':
            financials = extract_financials_from_csv(content)
        elif file_extension in ['xlsx', 'xls']:
            financials = extract_financials_from_excel(content)
        else:
            raise HTTPException(
                status_code=422, 
                detail=f"Unsupported file format: {file_extension}. Supported formats: PDF, CSV, XLSX, XLS"
            )
        
        # Structure response
        response_data = CompanyFinancials(
            company=company_name,
            income_statement=financials.income_statement,
            balance_sheet=financials.balance_sheet,
            cash_flow=financials.cash_flow
        )
        
        logger.info(f"Successfully parsed financials for {company_name}")
        return JSONResponse(content=response_data.dict(), status_code=200)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing file: {str(e)}")
        raise HTTPException(status_code=422, detail=f"File processing failed: {str(e)}")

@app.post("/model_acquisition", response_model=AcquisitionResponse)
async def model_acquisition(request: AcquisitionRequest):
    """
    Model acquisition scenarios with pro-forma financials and deal metrics.
    
    Takes parsed financials for acquirer and target companies along with deal terms,
    returns combined projections and key deal metrics.
    """
    try:
        result = acquisition_analyzer.analyze_acquisition(request)
        logger.info(f"Successfully modeled acquisition for deal value: ${request.deal_terms.deal_value:,.0f}")
        return result
        
    except Exception as e:
        logger.error(f"Acquisition modeling error: {str(e)}")
        raise HTTPException(status_code=422, detail=f"Acquisition modeling failed: {str(e)}")

@app.post("/generate_memo", response_model=MemoResponse)
async def generate_memo(request: MemoRequest):
    """
    Generate a professional investment banking deal memo.
    
    Takes deal summary, rationale, financials, synergies, and risks to create
    a structured banker-style memo using AI.
    """
    try:
        result = await memo_generator.generate_memo(request)
        logger.info(f"Successfully generated memo for {request.deal_summary.acquirer} acquiring {request.deal_summary.target}")
        return result
        
    except Exception as e:
        logger.error(f"Memo generation error: {str(e)}")
        raise HTTPException(status_code=422, detail=f"Memo generation failed: {str(e)}")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "AI Banker Copilot API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
