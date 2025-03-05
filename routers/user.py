from fastapi import APIRouter, HTTPException, File, UploadFile, Depends
from sqlalchemy.orm import Session
from db.db_connection import get_db
from db.crud import *
from sqlalchemy.dialects.postgresql import insert  # Required for ON CONFLICT
from db.models.user import User, UserRegister, UserLogin, UserSchema, UserSkills, UserSkillAssess, UserSkillAssessSchema, UserEmployerJobs, ResumeReport
from typing import List
import shutil, os, base64, json
from io import BytesIO

from dotenv import load_dotenv
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI
from pypdf import PdfReader

router = APIRouter()
load_dotenv()
llm = GoogleGenerativeAI(
    model='gemini-1.5-flash',
    temperature=0,
    # api_key=os.getenv('GEMINI_API_KEY')
    api_key='AIzaSyCqcRw49l81hOkG6khQifY4otkxU9Vwk3s'
)

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
    return result

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
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    '''
    UPLOAD_DIR = "uploads"
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    file_location = os.path.join(UPLOAD_DIR, file.filename)
    
    # Save file locally
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    '''

    # Convert PDF to Base64
    base64_string = "-"
    name = "-"
    position = "-"
    location = "-"
    experience = "-"
    education = "-"
    jobs = "-"
    skills_data = None
    # with open(file_location, "rb") as pdf_file:
    #     base64_string = base64.b64encode(pdf_file.read()).decode("utf-8")
    try:
        contents = await file.read()
        file_contents = BytesIO(contents)
        text = read_pdf_file(file_contents)

        prompt = """
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
        """

        prompt_template = PromptTemplate(template=prompt, input_variables=["text"])
        output_parser = JsonOutputParser(pydantic_object=ResumeReport)
        
        # Create the chain correctly
        chain = (
            prompt_template 
            | llm 
            | output_parser
        )
        
        # Invoke chain with the text
        response = chain.invoke({"text": text})
        base64_string = json.dumps(response)

        name = response['name']
        position = response['job_position']
        location = response['address']
        experience = json.dumps(response['experience'])
        education = json.dumps(response['education'])
        jobs = json.dumps(response['jobs'])
        skills_data = dict.fromkeys(response['skills'], 0)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")
    
    update_user_skills(db, email, skills_data)

    result = update_data(db, User, {"email": email}, {
        "name": name,
        "resume": file.filename,
        "resume_base64": base64_string,
        "position": position,
        "location": location,
        "experience": experience,
        "education": education,
        "jobs": jobs
    })
    if result:
        print(f"User with email {email} updated successfully.")
    else:
        # print(f"User with email {email} not found.")
        raise HTTPException(status_code=400, detail={result["error"]})
    
    return f"User with email {email} updated successfully."

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

@router.post("/{email}/apply/{job}")
def user_apply_job(email: str, job: str, db: Session = Depends(get_db)):
    user_id = get_data(db, User, {"email": email})[0].id

    result = insert_data(db, UserEmployerJobs, {
        "user_id": user_id,
        "employer_jobs_id": job
    })
    if not result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result