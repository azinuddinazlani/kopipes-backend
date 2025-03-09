from pydantic import BaseModel, validator, Field
from typing import List
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings
from pymongo import MongoClient
from fastapi import HTTPException
import os
import json
import re

# Pydantic Models
class CandidateResponse(BaseModel):
    question: str = Field(
        ...,
        description="The behavioral question to evaluate",
        example="Tell me about yourself?"
    )
    response: str = Field(
        ...,
        description="The candidate's response to the question"
    )
    
    @validator('response')
    def response_must_not_be_placeholder(cls, v):
        if v == "string" or not v.strip():
            raise ValueError('Please provide an actual response, not the placeholder "string" or an empty response')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "question": "Tell me about yourself?",
                "response": "I am a software developer with 5 years of experience..."
            }
        }

class BatchRequest(BaseModel):
    responses: List[CandidateResponse] = Field(
        ...,
        description="List of questions and responses to evaluate",
        example=[
            {
                "question": "Tell me about yourself?",
                "response": "I am a software developer with 5 years of experience..."
            },
            {
                "question": "Describe a project where you had to be particularly detail-oriented and organized. What specific steps did you take to ensure everything was completed correctly and on time?",
                "response": "In my previous role, I led a critical project..."
            },
            {
                "question": "How do you typically build relationships with new team members when joining a project? Can you share an example of how you've done this successfully?",
                "response": "When joining a new project, I make it a priority to schedule one-on-one meetings..."
            },
            {
                "question": "Tell me about a situation where you disagreed with a team decision. How did you handle it, and what was the outcome?",
                "response": "In a recent project, there was a disagreement about the technical approach..."
            },
            {
                "question": "We all face stressful situations at work. Could you describe a particularly challenging work situation you've encountered and how you managed your emotions and reactions during that time?",
                "response": "During a critical project deadline, we faced unexpected technical challenges..."
            }
        ]
    )

class AIAnalysis(BaseModel):
    ai_probability: float
    confidence_level: float
    reasoning: str
    ai_indicators: List[str]
    human_indicators: List[str]
    recommendation: str

class ScoreBreakdown(BaseModel):
    relevance: float
    clarity: float
    specificity: float
    professional_tone: float
    completeness: float

class Citation(BaseModel):
    text: str
    source: str
    page_number: int = Field(
        default=1, # Default to page 1 if not provided
        description="Page number where the citation can be found",
        example=1
    )

class EvaluationResponse(BaseModel):
    question: str
    answer: str
    score: float
    score_breakdown: ScoreBreakdown
    feedback: str
    citations: List[Citation]
    strengths: List[str]
    areas_for_improvement: List[str]
    personality_traits: List[str]
    ai_analysis: AIAnalysis

class BatchEvaluationResponse(BaseModel):
    evaluations: List[EvaluationResponse]

# Evaluator Class
class BehaviorEvaluator:
    def __init__(self):
        # Get API key from environment variable
        api_key = os.getenv("GOOGLE_API_KEY")
        
        # Initialize LLM with Vertex AI key
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            temperature=0.3,
            google_api_key=api_key
        )

        # Initialize embeddings with Vertex AI key
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=api_key
        )

        # MongoDB setup
        self.client = MongoClient(os.getenv("MONGODB_ATLAS_CLUSTER_URI"))
        self.collection = self.client.behavioral_db.behavioral_collection

        # Initialize vector store
        self.vector_store = MongoDBAtlasVectorSearch(
            collection=self.collection,
            embedding=self.embeddings,
            index_name="behavioral-vector-index",
            relevance_score_fn="cosine",
        )

        # Evaluation prompt
        self.evaluation_prompt = PromptTemplate(
            input_variables=["question", "response", "criteria"],
            template="""
            You are an expert in evaluating behavioral responses based on company-provided interview guidelines and detecting AI-generated text.
            Analyze the following candidate response from a job interview and determine the likelihood it was written by an AI rather than a human.

            Question: {question}
            Candidate Response: {response}
            Evaluation Criteria from Company Guidelines: {criteria}

            Provide a structured evaluation including:
            - A score from 0 to 100, broken down as follows:
              * Relevance to Question (0-30 points): How well does the response address the specific question?
              * Clarity and Structure (0-20 points): Is the response well-organized and easy to follow?
              * Specificity and Detail (0-20 points): Does the response include concrete examples and specific details?
              * Professional Tone (0-15 points): Is the language appropriate and professional?
              * Completeness (0-15 points): Does the response fully answer all aspects of the question?
            - Feedback on strengths and weaknesses, with specific citations from the evaluation criteria
            - Key strengths demonstrated
            - Areas for improvement
            - Personality traits observed

            Additionally, analyze whether the response was AI-generated based on:
            1. Natural language patterns and irregularities
            2. Personal storytelling elements and specificity
            3. Emotional authenticity and personal voice
            4. Presence of concrete, specific details vs. generic statements
            5. Linguistic patterns typical of AI-generated text

            IMPORTANT: Your entire response must be a valid JSON object with the following structure and nothing else:
            {{
                "score": <number>,
                "score_breakdown": {{
                    "relevance": <number>,
                    "clarity": <number>,
                    "specificity": <number>,
                    "professional_tone": <number>,
                    "completeness": <number>
                }},
                "feedback": "<detailed_feedback>",
                "citations": [
                    {{
                        "text": "<exact text from evaluation criteria>",
                        "source": "<source of the criteria>",
                        "page_number": <page_number>
                    }},
                    ...
                ],
                "strengths": ["<strength_1>", "<strength_2>", ...],
                "areas_for_improvement": ["<improvement_1>", "<improvement_2>", ...],
                "personality_traits": ["<trait_1>", "<trait_2>", ...],
                "ai_analysis": {{
                    "ai_probability": <number_between_0_and_1>,
                    "confidence_level": <number_between_0_and_1>,
                    "reasoning": "<detailed_explanation>",
                    "ai_indicators": ["<indicator_1>", "<indicator_2>", ...],
                    "human_indicators": ["<indicator_1>", "<indicator_2>", ...],
                    "recommendation": "<clear_recommendation>"
                }}
            }}

            Where:
            - score is the total score (0-100) based on the breakdown above
            - score_breakdown shows the individual scores for each component
            - citations should include specific quotes from the evaluation criteria that support your feedback, including the page number where each citation can be found
            - ai_probability is your assessment of how likely this text was AI-generated (0 = definitely human, 1 = definitely AI)
            - confidence_level indicates how confident you are in your assessment
            - reasoning explains your analysis
            - ai_indicators lists specific elements suggesting AI generation
            - human_indicators lists specific elements suggesting human authorship
            - recommendation provides a clear statement about whether this appears to be AI-generated

            Do not include any explanations, markdown formatting, or additional text outside the JSON structure.
            """
        )

    async def evaluate_response(self, question: str, response: str) -> dict:
        try:
            # Additional validation to prevent processing placeholder or empty responses
            if response == "string" or not response.strip():
                raise HTTPException(
                    status_code=400,
                    detail="Please provide an actual response, not the placeholder 'string' or an empty response"
                )
                
            # Retrieve relevant interview guidelines from MongoDB
            similar_docs = self.vector_store.similarity_search(
                query=question + " " + response,
                k=3  # Retrieve top 3 relevant documents
            )
            
            # Combine relevant guidelines
            criteria = "\n".join([doc.page_content for doc in similar_docs])

            # Use the new recommended approach with RunnableSequence
            chain = self.evaluation_prompt | self.llm
            result = await chain.ainvoke({
                "question": question,
                "response": response,
                "criteria": criteria
            })
            
            # Extract content from the response
            content = result.content if hasattr(result, 'content') else str(result)
            # print(f"Raw LLM response type: {type(result)}")
            # print(f"Raw LLM response: {content}")
            
            # Check if content is empty
            if not content or content.isspace():
                raise HTTPException(
                    status_code=500, 
                    detail="Received empty response from LLM"
                )
            
            # Try to find JSON in the response (sometimes LLMs add explanatory text)
            json_match = re.search(r'({[\s\S]*})', content)
            if json_match:
                json_str = json_match.group(1)
                # print(f"Extracted JSON: {json_str}")
                try:
                    parsed_result = json.loads(json_str)
                except json.JSONDecodeError:
                    # If that fails, try a more aggressive approach
                    json_str = re.search(r'({[\s\S]*})', content.replace('\n', ' ')).group(1)
                    parsed_result = json.loads(json_str)
            else:
                # If no JSON-like structure is found, try to parse the whole response
                try:
                    parsed_result = json.loads(content)
                except json.JSONDecodeError as json_err:
                    print(f"JSON parsing error: {str(json_err)}")
                    print(f"Content that failed to parse: {content}")
                    
                    parsed_result = {
                        "score": 50,  # Default middle score
                        "score_breakdown": {
                            "relevance": 0,
                            "clarity": 0,
                            "specificity": 0,
                            "professional_tone": 0,
                            "completeness": 0
                        },
                        "feedback": f"Failed to parse response. Raw content: {content[:200]}...",
                        "citations": [
                            {
                                "text": "Unable to determine citations due to parsing error",
                                "source": "Error",
                                "page_number": 1  # Changed from 0 to 1
                            }
                        ],
                        "strengths": ["Unable to determine strengths due to parsing error"],
                        "areas_for_improvement": ["Unable to determine areas for improvement due to parsing error"],
                        "personality_traits": ["Unable to determine personality traits due to parsing error"],
                        "ai_analysis": {
                            "ai_probability": 0.5,  # Default middle probability
                            "confidence_level": 0.5,  # Default confidence level
                            "reasoning": "Failed to parse response, unable to determine AI-generated probability.",
                            "ai_indicators": ["Unable to determine due to parsing error"],
                            "human_indicators": ["Unable to determine due to parsing error"],
                            "recommendation": "Uncertain due to parsing error"
                        }
                    }
                    print(f"Using fallback response: {parsed_result}")
            
            # Validate the structure of the parsed result
            required_keys = ["score", "score_breakdown", "feedback", "strengths", "areas_for_improvement", "personality_traits", "ai_analysis"]
            for key in required_keys:
                if key not in parsed_result:
                    parsed_result[key] = f"Missing {key} in response"
                    print(f"Added missing key: {key}")
            
            # Ensure score is a float
            if not isinstance(parsed_result["score"], (int, float)):
                try:
                    parsed_result["score"] = float(parsed_result["score"])
                except (ValueError, TypeError):
                    parsed_result["score"] = 50.0  # Default score
            
            # Ensure lists are actually lists
            for key in ["strengths", "areas_for_improvement", "personality_traits"]:
                if not isinstance(parsed_result[key], list):
                    parsed_result[key] = [parsed_result[key]]
            
            # Ensure all citation page numbers are valid integers
            if "citations" in parsed_result:
                for i in range(len(parsed_result["citations"])):
                    if "page_number" not in parsed_result["citations"][i] or parsed_result["citations"][i]["page_number"] is None:
                        parsed_result["citations"][i]["page_number"] = 1
            
            # Add the question to the response
            parsed_result["question"] = question
            parsed_result["answer"] = response
            
            return parsed_result
            
        except HTTPException as http_ex:
            raise http_ex
        except Exception as e:
            print(f"Error in evaluate_response: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))