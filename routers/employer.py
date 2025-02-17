from fastapi import APIRouter, HTTPException, File, UploadFile, Depends
from sqlalchemy.orm import Session
from db.db_connection import get_db
from db.crud import *
from db.models.employer import Employer, EmployerSchema, EmployerJobs

router = APIRouter()

@router.post("/")
def employer_list(db: Session = Depends(get_db)):
    result = get_data(db, Employer)
    if not result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.post("/{name}")
def employer_search(name: str, db: Session = Depends(get_db)):
    result = get_data(db, Employer, {"name": name})
    if not result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result