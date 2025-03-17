from fastapi import APIRouter, HTTPException, File, UploadFile, Depends
from sqlalchemy.orm import Session
from db.db_connection import get_db
from db.crud import *
from db.models.employer import Employer, EmployerSchema, EmployerJobs
from typing import List, Optional
import json

router = APIRouter()

@router.post("/")
def employer_list(db: Session = Depends(get_db)):
    result = get_data(db, Employer)
    if not result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.post("/{name}")
def employer_search(name: str, db: Session = Depends(get_db), hide_empty: bool = False):
    result = get_data(db, Employer, {"name": name})

    if not result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    employer_data = result[0]

    if employer_data.jobs:
        jobs_to_remove = []  # Keep track of jobs to remove
        try:
            for jobs in employer_data.jobs:
                # jobs["match_json"] = json.loads(jobs["match_json"]) if jobs["match_json"] else {}
                jobs.desc_json = json.loads(jobs.desc_json) if jobs.desc_json else {}
                jobs.responsibilities = json.loads(jobs.responsibilities) if jobs.responsibilities else []
                jobs.skills = json.loads(jobs.skills) if jobs.skills else []

                # Check if user_employer_jobs is empty
                if not jobs.user_employer_jobs:
                    jobs_to_remove.append(jobs)

                for applied in jobs.user_employer_jobs:
                    applied.match_json = json.loads(applied.match_json) if applied.match_json else {}
                    applied.user.about = json.loads(applied.user.about) if applied.user.about else {}
            
            for job in jobs_to_remove:
                employer_data.jobs.remove(job)
        except json.JSONDecodeError:
            print(f"Warning: Could not decode 'education' as JSON for user ")

    return employer_data