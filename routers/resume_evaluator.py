from fastapi import HTTPException
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import GoogleGenerativeAI
from db.models.user import ResumeReport
from pypdf import PdfReader
from io import BytesIO
import json, os

def replace_nulls(obj):
    """Recursively replace None values with an empty string in a dictionary or list."""
    if isinstance(obj, dict):
        return {k: replace_nulls(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [replace_nulls(v) for v in obj]
    elif obj is None:
        return ""
    return obj

class ResumeEvaluator:
    def __init__(self):
        self.llm = GoogleGenerativeAI(
            model='gemini-1.5-flash',
            temperature=0,
            api_key=os.getenv("GOOGLE_API_KEY")
        )
        
        self.evaluation_prompt = PromptTemplate(
            template="""
            Extract information from the resume delimited by triple backquotes and return it as JSON with the following fields:
            - name: The full name of the person
            - job position: Last job position
            - address: Their current address. 'State, City'
            - email: Email Address
            - experience: A list of their work experiences or internship and include all details without changing the original contexts.
            - education: A list of their educational qualifications
            - skills: A list of their technical and professional skills
            - jobs: List of job experience

            ```{text}```
            """,
            input_variables=["text"]
        )

    def read_pdf_file(self, file_contents: BytesIO) -> str:
        """Extract text content from a PDF file."""
        try:
            pdf_reader = PdfReader(file_contents)
            text = ''
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error reading PDF: {str(e)}")

    async def evaluate_resume(self, file_contents: BytesIO) -> dict:
        """Evaluate a resume and extract structured information."""
        try:
            # Extract text from PDF
            text = self.read_pdf_file(file_contents)

            # Create the chain correctly
            chain = (
                self.evaluation_prompt 
                | self.llm 
                | JsonOutputParser(pydantic_object=ResumeReport)
            )
            
            # Invoke chain with the text
            response = await chain.ainvoke({"text": text})
            
            # Process the response
            processed_response = replace_nulls(response)
            
            return {
                "base64_string": json.dumps(processed_response, indent=2),
                "name": response.get('name', '-'),
                "position": response.get('job_position', '-'),
                "location": response.get('address', '-'),
                "experience": json.dumps(response.get('experience', '-')),
                "education": json.dumps(response.get('education', '-')),
                "jobs": json.dumps(response.get('jobs', '-')),
                "skills": response.get('skills', [])
            }
            
        except Exception as e:
            print(f"Error in evaluate_resume: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}") 