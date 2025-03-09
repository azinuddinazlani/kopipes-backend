from sqlalchemy import Column, Integer, String, ForeignKey, Float, Table
from sqlalchemy.orm import relationship
from pydantic import BaseModel, EmailStr
from typing import Optional
from db.db_connection import Base
# from db.models.user import UserEmployerJobs

class EmployerSchema(BaseModel):
    name: Optional[str] = None
    info: Optional[str] = None
    logo: Optional[str] = None

class Employer(Base):
    __tablename__ = "employers"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
    info = Column(String, nullable=True)
    logo = Column(String, nullable=True)
    
    jobs = relationship('EmployerJobs', back_populates='employer', lazy="joined")


class EmployerJobs(Base):
    __tablename__ = "employer_jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employer_id = Column(Integer, ForeignKey('employers.id', ondelete='CASCADE'), nullable=True)
    name = Column(String, nullable=True)
    description = Column(String, nullable=True)
    desc_json = Column(String, nullable=True)

    employer = relationship('Employer', back_populates='jobs', lazy='joined')
    user_employer_jobs = relationship('UserEmployerJobs', back_populates='jobs', lazy='joined', uselist=True)
