from fastapi import APIRouter, HTTPException, File, UploadFile, Depends
from sqlalchemy.orm import Session
from db.db_connection import get_db
from db.crud import *
from db.models.user import User, UserRegister, UserLogin, UserSchema, UserSkillAssess, UserSkillAssessSchema, UserEmployerJobs
from typing import List
import shutil, os, base64

router = APIRouter()

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
    result = update_data(db, User, {"email": email}, user_data.dict())
    if result:
        print(f"User with email {email} updated successfully.")
    else:
        # print(f"User with email {email} not found.")
        raise HTTPException(status_code=400, detail={result["error"]})
    
    return result

@router.post("/{email}/upload")
async def user_upload(email: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    UPLOAD_DIR = "uploads"
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    file_location = os.path.join(UPLOAD_DIR, file.filename)
    
    # Save file locally
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Convert PDF to Base64
    base64_string = "-"
    # with open(file_location, "rb") as pdf_file:
    #     base64_string = base64.b64encode(pdf_file.read()).decode("utf-8")

    result = update_data(db, User, {"email": email}, {
        "resume": file.filename,
        "resume_base64": base64_string
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