import json
import logging
from typing import Dict, Any
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

logger = logging.getLogger(__name__)

class ResumeParserService:
    def __init__(self):
        pass

    async def parse_resume(self, resume_text: str, api_key: str) -> Dict[str, Any]:
        """
        Extracts structured data (Skills, Projects, Experience) from raw resume text.
        """
        llm = ChatGroq(
            temperature=0.0, # Strict extraction
            groq_api_key=api_key,
            model_name="llama-3.3-70b-versatile",
            max_tokens=4000
        )
        
        prompt_template = """
        You are an expert Technical Recruiter.
        Extract the following details from the Candidate's Resume text below.
        
        RESUME TEXT:
        {resume_text}
        
        Output strictly in JSON format:
        {{
            "skills": ["List of technical skills mentioned"],
            "projects": [
                {{ "name": "Project Name", "tech_stack": ["Stack used"], "description": "Brief summary" }}
            ],
            "experience": [
                {{ "role": "Job Title", "company": "Company Name", "description": "Key achievements" }}
            ]
        }}
        """
        
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["resume_text"]
        )
        
        chain = prompt | llm
        
        try:
            response = await chain.ainvoke({"resume_text": resume_text})
            return self._clean_json(response.content)
        except Exception as e:
            logger.error(f"Failed to parse resume: {e}")
            raise e

    def extract_text_from_pdf(self, file_stream) -> str:
        """
        Extracts raw text from a PDF file stream using pypdf.
        """
        from pypdf import PdfReader
        try:
            reader = PdfReader(file_stream)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Failed to read PDF: {e}")
            raise ValueError("Invalid PDF file")

    def _clean_json(self, content: str) -> Dict[str, Any]:
        import re
        # Find JSON object using regex (starts with {, ends with }, includes newlines)
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if match:
            content = match.group(0)
        return json.loads(content)

resume_parser_service = ResumeParserService()
