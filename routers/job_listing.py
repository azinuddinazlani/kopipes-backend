from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from db.db_connection import get_db
from db.crud import *
from db.models.employer import Employer, EmployerJobs
from db.models.user import User, UserEmployerJobs
from typing import List, Optional
import json

router = APIRouter()

@router.post("/")
def get_all_jobs(
    email: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get all job listings with employer details.
    If email is provided, shows if the user has applied.
    """
    # Base query with employer join
    query = db.query(EmployerJobs).join(Employer)
    jobs = query.all()
    
    # Get user_id if email provided
    user_id = None
    if email:
        user = db.query(User).filter(User.email == email).first()
        if user:
            user_id = user.id
    
    # Convert SQLAlchemy objects to dictionaries for modification
    jobs_data = []
    for job in jobs:
        # Check if current user has applied
        user_application = None
        if user_id:
            application = db.query(UserEmployerJobs).filter(
                UserEmployerJobs.employer_jobs_id == job.id,
                UserEmployerJobs.user_id == user_id
            ).first()
            
            if application:
                user_application = {
                    "id": application.id or 0,
                    "user_id": application.user_id or 0,
                    "employer_jobs_id": application.employer_jobs_id or 0,
                    "match_json": application.match_json or ""
                }
        
        job_dict = {
            "id": job.id or 0,
            "employer_id": job.employer_id or 0,
            "name": job.name or "",
            "description": job.description or "",
            "desc_json": job.desc_json or "",
            "summary": job.summary or "",
            "responsibilities": job.responsibilities or "",
            "qualifications": job.qualifications or "",
            "skills": job.skills or "",
            "experience": job.experience or "",
            "experienceyear": job.experienceyear or "",
            "postedtime": job.postedtime or "",
            "jobtype": job.jobtype or "",
            "workmode": job.workmode or "",
            "level": job.level or "",
            "location": job.location or "",
            "employer": {
                "id": job.employer.id or 0,
                "name": job.employer.name or "",
                "info": job.employer.info or "",
                "logo": job.employer.logo or "",
                "location": job.employer.location or "",
                "businessnature": job.employer.businessnature or ""
            },
            "user_application": user_application or ""
        }
        
        jobs_data.append(job_dict)
    
    return jobs_data

'''


@router.get("/{job_id}")
def get_job_by_id(job_id: int, db: Session = Depends(get_db)):
    """
    Get a specific job listing by ID
    """
    job = db.query(EmployerJobs).join(Employer).filter(EmployerJobs.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Convert to dictionary and handle None values
    job_dict = {
        "id": job.id or 0,
        "employer_id": job.employer_id or 0,
        "name": job.name or "",
        "description": job.description or "",
        "desc_json": job.desc_json or "",
        "summary": job.summary or "",
        "responsibilities": job.responsibilities or "",
        "qualifications": job.qualifications or "",
        "skills": job.skills or "",
        "experience": job.experience or "",
        "experienceyear": job.experienceyear or "",
        "postedtime": job.postedtime or "",
        "jobtype": job.jobtype or "",
        "workmode": job.workmode or "",
        "level": job.level or "",
        "location": job.location or "",
        "employer": {
            "id": job.employer.id or 0,
            "name": job.employer.name or "",
            "info": job.employer.info or "",
            "logo": job.employer.logo or "",
            "location": job.employer.location or "",
            "businessnature": job.employer.businessnature or ""
        }
    }
    return job_dict

@router.get("/employer/{employer_id}")
def get_jobs_by_employer(employer_id: int, db: Session = Depends(get_db)):
    """
    Get all job listings for a specific employer
    """
    employer = db.query(Employer).filter(Employer.id == employer_id).first()
    if not employer:
        raise HTTPException(status_code=404, detail="Employer not found")
    
    jobs = db.query(EmployerJobs).filter(EmployerJobs.employer_id == employer_id).all()
    
    # Convert jobs to dictionaries and handle None values
    jobs_data = []
    for job in jobs:
        job_dict = {
            "id": job.id or 0,
            "employer_id": job.employer_id or 0,
            "name": job.name or "",
            "description": job.description or "",
            "desc_json": job.desc_json or "",
            "summary": job.summary or "",
            "responsibilities": job.responsibilities or "",
            "qualifications": job.qualifications or "",
            "skills": job.skills or "",
            "experience": job.experience or "",
            "experienceyear": job.experienceyear or "",
            "postedtime": job.postedtime or "",
            "jobtype": job.jobtype or "",
            "workmode": job.workmode or "",
            "level": job.level or "",
            "location": job.location or ""
        }
        jobs_data.append(job_dict)
    
    employer_dict = {
        "id": employer.id or 0,
        "name": employer.name or "",
        "info": employer.info or "",
        "logo": employer.logo or ""
    }
    
    return {
        "employer": employer_dict,
        "jobs": jobs_data
    }

@router.post("/search")
def search_jobs(
    search_term: str = "",
    jobtype: Optional[str] = None,
    workmode: Optional[str] = None,
    level: Optional[str] = None,
    location: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Search job listings with various filters
    """
    query = db.query(EmployerJobs).join(Employer)  # Join with Employer table
    
    if search_term:
        search = f"%{search_term}%"
        query = query.filter(
            (EmployerJobs.name.ilike(search)) |
            (EmployerJobs.description.ilike(search)) |
            (EmployerJobs.summary.ilike(search))
        )
    
    if jobtype:
        query = query.filter(EmployerJobs.jobtype == jobtype)
    
    if workmode:
        query = query.filter(EmployerJobs.workmode == workmode)
    
    if level:
        query = query.filter(EmployerJobs.level == level)
    
    if location:
        query = query.filter(EmployerJobs.location.ilike(f"%{location}%"))
    
    jobs = query.all()
    
    # Convert to dictionaries and handle None values
    jobs_data = []
    for job in jobs:
        job_dict = {
            "id": job.id or 0,
            "employer_id": job.employer_id or 0,
            "name": job.name or "",
            "description": job.description or "",
            "desc_json": job.desc_json or "",
            "summary": job.summary or "",
            "responsibilities": job.responsibilities or "",
            "qualifications": job.qualifications or "",
            "skills": job.skills or "",
            "experience": job.experience or "",
            "experienceyear": job.experienceyear or "",
            "postedtime": job.postedtime or "",
            "jobtype": job.jobtype or "",
            "workmode": job.workmode or "",
            "level": job.level or "",
            "location": job.location or "",
            "employer": {
                "id": job.employer.id or 0,
                "name": job.employer.name or "",
                "info": job.employer.info or "",
                "logo": job.employer.logo or "",
                "location": job.employer.location or "",
                "businessnature": job.employer.businessnature or ""
            }
        }
        jobs_data.append(job_dict)
    
    return jobs_data

@router.post("/")
def create_job(
    employer_id: int,
    name: str,
    description: str,
    summary: str,
    responsibilities: List[str],
    qualifications: str,
    skills: List[str],
    experience: str,
    experienceyear: str,
    postedtime: str,
    jobtype: str,
    workmode: str,
    level: str,
    location: str,
    db: Session = Depends(get_db)
):
    """
    Create a new job listing
    """
    # Check if employer exists
    employer = db.query(Employer).filter(Employer.id == employer_id).first()
    if not employer:
        raise HTTPException(status_code=404, detail="Employer not found")
    
    job_data = {
        "employer_id": employer_id,
        "name": name,
        "description": description,
        "summary": summary,
        "responsibilities": json.dumps(responsibilities),
        "qualifications": qualifications,
        "skills": json.dumps(skills),
        "experience": experience,
        "experienceyear": experienceyear,
        "postedtime": postedtime,
        "jobtype": jobtype,
        "workmode": workmode,
        "level": level,
        "location": location
    }
    
    result = insert_data(db, EmployerJobs, job_data)
    if not result:
        raise HTTPException(status_code=400, detail="Failed to create job listing")
    
    return result

@router.put("/{job_id}")
def update_job(
    job_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    summary: Optional[str] = None,
    responsibilities: Optional[List[str]] = None,
    qualifications: Optional[str] = None,
    skills: Optional[List[str]] = None,
    experience: Optional[str] = None,
    experienceyear: Optional[str] = None,
    postedtime: Optional[str] = None,
    jobtype: Optional[str] = None,
    workmode: Optional[str] = None,
    level: Optional[str] = None,
    location: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Update a job listing
    """
    job = db.query(EmployerJobs).filter(EmployerJobs.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    update_data = {}
    if name is not None:
        update_data["name"] = name
    if description is not None:
        update_data["description"] = description
    if summary is not None:
        update_data["summary"] = summary
    if responsibilities is not None:
        update_data["responsibilities"] = json.dumps(responsibilities)
    if qualifications is not None:
        update_data["qualifications"] = qualifications
    if skills is not None:
        update_data["skills"] = json.dumps(skills)
    if experience is not None:
        update_data["experience"] = experience
    if experienceyear is not None:
        update_data["experienceyear"] = experienceyear
    if postedtime is not None:
        update_data["postedtime"] = postedtime
    if jobtype is not None:
        update_data["jobtype"] = jobtype
    if workmode is not None:
        update_data["workmode"] = workmode
    if level is not None:
        update_data["level"] = level
    if location is not None:
        update_data["location"] = location
    
    result = update_data(db, EmployerJobs, {"id": job_id}, update_data)
    if not result:
        raise HTTPException(status_code=400, detail="Failed to update job listing")
    
    return result

@router.delete("/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db)):
    """
    Delete a job listing
    """
    job = db.query(EmployerJobs).filter(EmployerJobs.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    result = delete_data(db, EmployerJobs, {"id": job_id})
    if not result:
        raise HTTPException(status_code=400, detail="Failed to delete job listing")
    
    return {"message": "Job listing deleted successfully"} 

'''