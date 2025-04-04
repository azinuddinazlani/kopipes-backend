from fastapi import HTTPException
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import GoogleGenerativeAI
from db.models.user import JobReport
import json, os

class JobEvaluator:
    def __init__(self):
        self.llm = GoogleGenerativeAI(
            model='gemini-1.5-flash',
            temperature=0,
            api_key=os.getenv("GOOGLE_API_KEY")
        )
        
        self.evaluation_prompt = PromptTemplate(
            input_variables=["job_description", "resume"],
            template="""
            You are an expert HR analyst. Compare the candidate's resume with the job requirements and provide a detailed analysis.

            JOB DESCRIPTION:
            {job_description}

            CANDIDATE'S RESUME:
            {resume}

            Analyze and provide a JSON response with the following structure:
            {{
                "match_analysis": {{
                    "overall_match_score": <0-100>,
                    "score_breakdown": {{
                        "education_weight": <0-1>,
                        "experience_weight": <0-1>,
                        "skills_weight": <0-1>,
                        "calculation": "explanation of how overall score was calculated"
                    }},
                    "education_match": {{
                        "score": <0-100>,
                        "matched_requirements": [],
                        "gaps": []
                    }},
                    "experience_match": {{
                        "score": <0-100>,
                        "years_of_experience": <number>,
                        "relevant_experience": [],
                        "missing_experience": []
                    }},
                    "skills_match": {{
                        "score": <0-100>,
                        "matched_skills": [],
                        "missing_skills": []
                    }}
                }},
                "detailed_feedback": {{
                    "strengths": [],
                    "areas_for_improvement": [],
                    "recommendation": "string"
                }}
            }}

            Consider:
            1. Education alignment with requirements (weight: 0.25)
            2. Years and relevance of experience (weight: 0.40)
            3. Skills match and proficiency level (weight: 0.35)
            4. Overall suitability for the role

            The overall_match_score should be calculated using the weighted scores:
            - Education score × 0.25
            - Experience score × 0.40
            - Skills score × 0.35

            Provide specific examples from the resume that match or don't match the job requirements.
            Return only the JSON object, no other text."""
        )

    async def evaluate_job_match(self, job_description: str, resume: str) -> dict:
        try:
            # Create the chain correctly
            chain = (
                self.evaluation_prompt 
                | self.llm 
                | JsonOutputParser(pydantic_object=JobReport)
            )
            
            # Invoke chain with the text
            response = await chain.ainvoke({
                "job_description": json.dumps(job_description),
                "resume": json.dumps(resume)
            })
            
            return response
            
        except Exception as e:
            print(f"Error in evaluate_job_match: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e)) 