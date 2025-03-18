from fastapi import APIRouter, HTTPException, File, UploadFile, Depends
from sqlalchemy.orm import Session
from db.db_connection import get_db
from db.crud import *
from sqlalchemy.dialects.postgresql import insert  # Required for ON CONFLICT
from db.models.user import User, UserRegister, UserLogin, UserSchema, UserSkills, UserSkillAssess, UserSkillAssessSchema, UserEmployerJobs, ResumeReport, JobReport
from db.models.employer import Employer, EmployerJobs
from typing import List, Dict
import shutil, os, base64, json
from io import BytesIO
from .evaluator import BatchRequest, BatchEvaluationResponse, BehaviorEvaluator
from .job_evaluator import JobEvaluator
from .resume_evaluator import ResumeEvaluator
from .skillset_generator import SkillsetGenerator

from dotenv import load_dotenv
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI
from pypdf import PdfReader

router = APIRouter()
load_dotenv()
llm = GoogleGenerativeAI(
    model='gemini-1.5-pro',
    temperature=0,
    api_key=os.getenv('GOOGLE_API_KEY')
)
def replace_nulls(obj):
    """Recursively replace None values with an empty string in a dictionary or list."""
    if isinstance(obj, dict):
        return {k: replace_nulls(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [replace_nulls(v) for v in obj]
    elif obj is None:
        return ""
    return obj

def update_user_skills(db, email, skills_data):
    if not skills_data:
        return  # No skills to update
    

    user_id = get_data(db, User, {"email": email})[0].id

    # Fetch existing skills for the user
    existing_skills = {
        skill.name: skill for skill in db.query(UserSkills).filter(UserSkills.user_id == user_id).all()
    }

    for skill_name, skill_level in skills_data.items():
        if skill_name in existing_skills:
            existing_skills[skill_name].level = skill_level  # Update skill level
        else:
            new_skill = UserSkills(user_id=user_id, name=skill_name, level=skill_level)
            db.add(new_skill)  # Add new skill

    db.commit()



def read_pdf_file(file_contents: BytesIO):
    try:
        pdf_reader = PdfReader(file_contents)
        text = ''
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading PDF: {str(e)}")

@router.post("/")
def user_list(db: Session = Depends(get_db)):
    result = get_data(db, User)
    if not result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

# register new user
@router.post("/register")
def user_register(user_data: UserRegister, db: Session = Depends(get_db)):
    result = insert_data(db, User, user_data.dict())
    if not result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

# login
@router.post("/login")
def user_login(user_data: UserLogin, db: Session = Depends(get_db)):
    result = get_data(db, User, user_data.dict())
    if not result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.post("/{email}", summary="Get user details")
def user_get(email: str, db: Session = Depends(get_db)):
    result = get_data(db, User, {"email": email})
    if not result:
        raise HTTPException(status_code=400, detail=result["error"])
    # Return only the first result
    # return result[0]
    user_data = result[0]
    if user_data.about:
        try:
            user_data.about = json.loads(user_data.about)
        except json.JSONDecodeError:
            print(f"Warning: Could not decode 'about' as JSON for user {email}")
            user_data.about = {}
    else:
        user_data.about = {}

    if user_data.jobs:
        try:
            user_data.jobs = json.loads(user_data.jobs)
        except json.JSONDecodeError:
            print(f"Warning: Could not decode 'jobs' as JSON for user {email}")
            user_data.jobs = []

    if user_data.resume_base64:
        try:
            user_data.resume_base64 = json.loads(user_data.resume_base64)
        except json.JSONDecodeError:
            print(f"Warning: Could not decode 'resume_base64' as JSON for user {email}")
            user_data.resume_base64 = []

    if user_data.experience:
      try:
        user_data.experience = json.loads(user_data.experience)
      except json.JSONDecodeError:
          print(f"Warning: Could not decode 'experience' as JSON for user {email}")
          user_data.experience = []

    if user_data.education:
      try:
        user_data.education = json.loads(user_data.education)
      except json.JSONDecodeError:
          print(f"Warning: Could not decode 'education' as JSON for user {email}")
          user_data.education = []

    if user_data.employer_jobs:
        try:
            for jobs in user_data.employer_jobs:
                # jobs["match_json"] = json.loads(jobs["match_json"]) if jobs["match_json"] else {}
                jobs.match_json = json.loads(jobs.match_json) if jobs.match_json else {}
                jobs.jobs.desc_json = json.loads(jobs.jobs.desc_json) if jobs.jobs.desc_json else {}
                jobs.jobs.responsibilities = json.loads(jobs.jobs.responsibilities) if jobs.jobs.responsibilities else []
                jobs.jobs.skills = json.loads(jobs.jobs.skills) if jobs.jobs.skills else []
        except json.JSONDecodeError:
            print(f"Warning: Could not decode 'education' as JSON for user {email}")
            user_data.education = []

    return user_data

# update user details using their email
@router.post("/{email}/update")
def user_update(user_data: UserSchema, email: str, db: Session = Depends(get_db)):
#     result = update_data(db, User, {"email": email}, user_data.dict())
#     if result:
#         return ({"ok": f"User with email {email} updated successfully."})
#     else:
#         # print(f"User with email {email} not found.")
#         raise HTTPException(status_code=400, detail={result["error"]})

    skills_data = getattr(user_data, "skills", None)
    user_dict = user_data.dict(exclude={"skills"})
    result = update_data(db, User, {"email": email}, user_dict)
    if result:
        update_user_skills(db, email, skills_data)

        return ({"ok": f"User with email {email} updated successfully."})
    
    raise HTTPException(status_code=400, detail={result["error"]})

@router.post("/{email}/upload")
async def user_upload(email: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload and process a resume PDF file.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    try:
        # Read file contents
        contents = await file.read()
        file_contents = BytesIO(contents)

        # Create evaluator and process resume
        evaluator = ResumeEvaluator()
        result = await evaluator.evaluate_resume(file_contents)

        # Update user skills
        skills_data = dict.fromkeys(result["skills"], 0)
        update_user_skills(db, email, skills_data)

        # Update user information
        update_result = update_data(db, User, {"email": email}, {
            "name": result["name"],
            "resume": file.filename,
            "resume_base64": result["base64_string"],
            "position": result["position"],
            "location": result["location"],
            "experience": result["experience"],
            "education": result["education"],
            "jobs": result["jobs"]
        })

        if not update_result:
            raise HTTPException(status_code=400, detail="Failed to update user information")

        # Get and return the updated user data
        updated_user = get_data(db, User, {"email": email})[0]
        return updated_user

    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        print(f"Error in user_upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")


@router.post("/{email}/evaluate", response_model=BatchEvaluationResponse)
async def evaluate_responses(email: str, request: BatchRequest, db: Session = Depends(get_db)):
    """
    Evaluate multiple behavioral questions and responses in a single request.
    """
    evaluator = BehaviorEvaluator()
    try:
        evaluations = []
        for qr in request.responses:
            result = await evaluator.evaluate_response(
                question=qr.question,
                response=qr.response
            )
            evaluations.append(result)

        update_data(db, User, {"email": email}, {"about": json.dumps(evaluations)})

        return {"evaluations": evaluations}
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        print(f"Unexpected error in batch evaluation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.post("/{email}/apply/{job}")
async def user_apply_job(
    email: str, 
    job: str, 
    force_evaluate: bool = False,
    db: Session = Depends(get_db)
):
    """
    Evaluate a job application by comparing the user's resume with job requirements.
    Only performs evaluation if:
    - No previous evaluation exists
    - Previous evaluation is empty
    - force_evaluate is True
    
    Args:
        email: User's email
        job: Job ID to apply for
        force_evaluate: If True, forces re-evaluation even if previous evaluation exists
        db: Database session
    """
    try:
        # Get user and job data
        user_id = get_data(db, User, {"email": email})[0].id
        job_description = db.query(EmployerJobs.desc_json).filter(EmployerJobs.id == int(job)).first()
        if not job_description:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Check for existing application
        existing_application = db.query(UserEmployerJobs).filter(
            UserEmployerJobs.user_id == user_id,
            UserEmployerJobs.employer_jobs_id == int(job)
        ).first()

        # If there's an existing application with non-empty match_json and not forcing re-evaluation
        if not force_evaluate and existing_application and existing_application.match_json and existing_application.match_json.strip():
            return json.loads(existing_application.match_json)

        # If we need to evaluate, get the resume
        job_description = json.loads(job_description[0])
        resume = get_data(db, User, {"email": email})[0].resume_base64
        if not resume:
            raise HTTPException(status_code=400, detail="User resume not found")

        # Create evaluator and get analysis
        evaluator = JobEvaluator()
        result = await evaluator.evaluate_job_match(
            job_description=job_description,
            resume=resume
        )

        # Delete any existing application
        if existing_application:
            delete_data(db, UserEmployerJobs, {"id": existing_application.id})

        # Store the new application
        db_result = insert_data(db, UserEmployerJobs, {
            "user_id": user_id,
            "employer_jobs_id": int(job),
            "match_json": json.dumps(result, indent=2)
        })
        if not db_result:
            raise HTTPException(status_code=400, detail="Failed to store job application")

        return result
        
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        print(f"Unexpected error in job application: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    

@router.post("/{email}/skill-assess")
def user_skill_assess(email: str, db: Session = Depends(get_db)):
    user_id = get_data(db, User, {"email": email})[0].id

    skill_qs = get_data(db, UserSkillAssess, {"user_id": user_id})
    total_qs = len(skill_qs)
    if (isinstance(skill_qs, dict) and 'error' in skill_qs):
        total_qs = 0
    
    if total_qs < 5 or (isinstance(skill_qs, dict) and 'error' in skill_qs):
        user_skill = get_data(db, UserSkills, {"user_id": user_id})
        topics = [
            {
                "topic": skill.name,
                "level_min": max(1, skill.level - 1),
                "level_max": min(5, skill.level + 1)
            } for skill in user_skill
        ]

        generator = SkillsetGenerator()
        result = generator.generate(topics, 5-total_qs)
        for qs in result['questions']:
            insert_data(db, UserSkillAssess, {
                "user_id": user_id,
                "qs_type": qs['topic'],
                "question": qs['question'],
                "option": qs['options'],
                "answer_real": qs['answer'],
                "qs_level": qs['level']
            })

        skill_qs = get_data(db, UserSkillAssess, {"user_id": user_id})

    return skill_qs

@router.post("/{email}/skill-assess/save")
def user_skill_assess_save(email: str, answers: Dict[int, str], db: Session = Depends(get_db)):
    user_id = get_data(db, User, {"email": email})[0].id

    # Update the UserSkillAssess table with the provided answers
    for skill_id, answer_given in answers.items():
        result = update_data(db, UserSkillAssess, {"id": skill_id, "user_id": user_id}, {"answer_given": answer_given})
        if not result:
            raise HTTPException(status_code=400, detail=f"Failed to update skill assessment with id {skill_id}")
        
    skill_qs = get_data(db, UserSkillAssess, {"user_id": user_id})
    return skill_qs


'''
# update user details using their email
@router.post("/{email}/skill-assess")
def user_skill_assess_new(skills: List[UserSkillAssessSchema], email: str, db: Session = Depends(get_db)):
    user_id = get_data(db, User, {"email": email})[0].id
    for skill in skills:
        skill.user_id = user_id
        result = insert_data(db, UserSkillAssess, skill.dict())

        if result:
            print(f"User with email {email} updated successfully.")
        else:
            # print(f"User with email {email} not found.")
            raise HTTPException(status_code=400, detail={result["error"]})
    return True


@router.post("/{email}/skill-assess/{version}")
def user_skill_assess_get(email: str, version: str, db: Session = Depends(get_db)):
    user_id = get_data(db, User, {"email": email})[0].id

    result = get_data(db, UserSkillAssess, {
        "user_id": user_id,
        "version": version
    })
    if not result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.post("/{email}/skill-assess/{version}/update")
def user_skill_assess_set(skills: List[UserSkillAssessSchema], email: str, version: str, db: Session = Depends(get_db)):
    user_id = get_data(db, User, {"email": email})[0].id
    
    for skill in skills:
        skill.user_id = user_id
        skill.version = version
        result = update_data(db, UserSkillAssess, skill.dict())

        if result:
            print(f"User with email {email} updated successfully.")
        else:
            # print(f"User with email {email} not found.")
            raise HTTPException(status_code=400, detail={result["error"]})
    return True

'''