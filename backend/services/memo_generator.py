import logging
import os
from groq import Groq
import markdown
from typing import Optional
from models.memo_models import MemoRequest, MemoResponse, MemoFormat
from dotenv import load_dotenv
load_dotenv()
logger = logging.getLogger(__name__)

class MemoGenerator:
    def __init__(self):
        self.logger = logger
        # Initialize Groq client
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is required")
        self.client = Groq(api_key=api_key)

    async def generate_memo(self, request: MemoRequest) -> MemoResponse:
        """Generate a professional deal memo using Groq API"""
        try:
            # Construct the prompt
            prompt = self._build_prompt(request)
            
            # Call Groq API
            memo_content = await self._call_groq_api(prompt)
            
            # Format the response based on requested format
            formatted_memo = self._format_memo(memo_content, request.format)
            
            # Count words
            word_count = len(memo_content.split())
            
            return MemoResponse(
                memo=formatted_memo,
                format=request.format,
                word_count=word_count
            )
            
        except Exception as e:
            self.logger.error(f"Memo generation error: {str(e)}")
            raise

    def _build_prompt(self, request: MemoRequest) -> str:
        """Build a comprehensive prompt for the AI model"""
        
        # Format financial data
        financials_summary = self._format_financials(request.financials)
        synergies_summary = self._format_synergies(request.synergies)
        risks_list = ", ".join(request.risks)
        
        prompt = f"""
You are a senior investment banker at a top-tier investment bank. Write a comprehensive, professional deal memo for the following M&A transaction. The memo should follow standard investment banking formatting and language.

**DEAL DETAILS:**
- Acquirer: {request.deal_summary.acquirer}
- Target: {request.deal_summary.target}
- Deal Value: ${request.deal_summary.deal_value:,.0f}
- Structure: {request.deal_summary.structure}
- Strategic Rationale: {request.strategic_rationale}

**FINANCIAL SUMMARY:**
{financials_summary}

**SYNERGIES:**
{synergies_summary}

**KEY RISKS:**
{risks_list}

Please structure the memo with the following sections:
1. **Executive Summary** - High-level overview of the transaction
2. **Strategic Rationale** - Why this deal makes strategic sense
3. **Financial Analysis & Valuation** - Key financial metrics and valuation methodology
4. **Synergies Analysis** - Expected cost and revenue synergies
5. **Risk Assessment** - Key risks and mitigation strategies
6. **Recommendation** - Final recommendation with supporting rationale

Write in a professional, concise manner typical of investment banking deal memos. Use financial terminology appropriately and include specific metrics where relevant.
"""
        return prompt

    def _format_financials(self, financials: dict) -> str:
        """Format financial data for the prompt"""
        if not financials:
            return "Financial data not provided"
        
        # Extract pro-forma data if available
        pro_forma = financials.get("pro_forma_financials", {})
        if pro_forma:
            pf_data = pro_forma.get("2024_pro_forma", {})
            return f"""
- Combined Revenue: ${pf_data.get('revenue', 0):,.0f}
- Combined EBITDA: ${pf_data.get('ebitda', 0):,.0f}
- Combined Net Income: ${pf_data.get('net_income', 0):,.0f}
- Synergies Realized: ${pf_data.get('synergies_realized', 0):,.0f}
"""
        
        return "Pro-forma financials to be calculated"

    def _format_synergies(self, synergies: dict) -> str:
        """Format synergies data for the prompt"""
        if not synergies:
            return "Synergies analysis pending"
        
        annual_savings = synergies.get("annual_savings", 0)
        duration = synergies.get("duration_years", 0)
        
        return f"""
- Annual Cost Savings: ${annual_savings:,.0f}
- Synergies Duration: {duration} years
- Total Synergies Value: ${annual_savings * duration:,.0f}
"""

    async def _call_groq_api(self, prompt: str) -> str:
        """Call Groq API to generate the memo"""
        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-70b-versatile",  # Use Groq's recommended model
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a senior investment banker with 15+ years of experience writing deal memos for Fortune 500 M&A transactions."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Lower temperature for more consistent professional output
                max_tokens=4000,
                top_p=0.9
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"Groq API error: {str(e)}")
            raise Exception(f"Failed to generate memo: {str(e)}")

    def _format_memo(self, memo_content: str, format_type: MemoFormat) -> str:
        """Format the memo according to the requested format"""
        if format_type == MemoFormat.MARKDOWN:
            return memo_content
        elif format_type == MemoFormat.HTML:
            return markdown.markdown(memo_content)
        elif format_type == MemoFormat.JSON:
            # Parse sections and return as structured JSON
            return self._parse_memo_to_json(memo_content)
        else:
            return memo_content

    def _parse_memo_to_json(self, memo_content: str) -> str:
        """Parse memo into structured JSON format"""
        import json
        
        # Simple parsing - split by headers (##)
        sections = {}
        current_section = "introduction"
        current_content = []
        
        for line in memo_content.split('\n'):
            if line.startswith('##') or line.startswith('#'):
                # Save previous section
                if current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                
                # Start new section
                current_section = line.replace('#', '').strip().lower().replace(' ', '_')
                current_content = []
            else:
                current_content.append(line)
        
        # Save last section
        if current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return json.dumps({"sections": sections}, indent=2)
