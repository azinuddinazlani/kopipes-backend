from sqlalchemy import Column, Integer, String, ForeignKey, Float, Table
from sqlalchemy.orm import relationship
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, List
from db.db_connection import Base
from db.models.employer import EmployerJobs

class UserRegister(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr

class UserSchema(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    about: Optional[str] = None
    resume: Optional[str] = None
    skills: Optional[Dict[str, str]] = None
    position: Optional[str] = None
    location: Optional[str] = None
    experience: Optional[str] = None
    education: Optional[str] = None
    jobs: Optional[str] = None

class ResumeReport(BaseModel):
    name: str = Field(description="Name of the employee")
    address: str = Field(description="Address of the employee")
    skills: List[str] = Field(description="List of skills")
    education: List[str] = Field(description="Education details of the employee")
    experience: List[str] = Field(description="Experience details of the employee")

class JobReport(BaseModel):
    title: str
    description: str
    location: str
    experience: str
    education: str
    skills: str

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    password = Column(String, nullable=True)
    type = Column(String, default="Pending")
    about = Column(String, nullable=True)
    resume = Column(String, nullable=True)
    resume_base64 = Column(String, nullable=True)
    position = Column(String, nullable=True)
    location = Column(String, nullable=True)
    experience = Column(String, nullable=True)
    education = Column(String, nullable=True)
    jobs = Column(String, nullable=True)

    skills = relationship('UserSkills', back_populates='user', lazy="joined")
    skill_assess = relationship('UserSkillAssess', back_populates='user', lazy="joined")
    employer_jobs = relationship('UserEmployerJobs', back_populates='user', lazy='joined')


class UserSkills(Base):
    __tablename__ = "users_skills"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    name = Column(String, nullable=True)
    level = Column(String, nullable=True)

    user = relationship('User', back_populates='skills')

class UserSkillAssessSchema(BaseModel):
    user_id: int
    version: Optional[str] = "0"
    qs_type: str
    question: str
    option: str
    answer_given: Optional[str] = None
    answer_real: str
    qs_level: str
    user_level: str

class UserSkillAssess(Base):
    __tablename__ = "users_skill_assess"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    version = Column(Integer, default="0")
    qs_type = Column(String, default="")
    question = Column(String, nullable=True, default="")
    option = Column(String, nullable=True, default="")
    answer_given = Column(String, nullable=True, default="")
    answer_real = Column(String, nullable=True, default="")
    qs_level = Column(String, default="0")
    user_level = Column(String, default="0")

    user = relationship('User', back_populates='skill_assess')

class UserEmployerJobs(Base):
    __tablename__ = "user_employer_jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    employer_jobs_id = Column(Integer, ForeignKey('employer_jobs.id'), nullable=True)
    match_json = Column(String, default="")

    user = relationship('User', back_populates="employer_jobs")
    jobs = relationship('EmployerJobs', back_populates='user_employer_jobs', lazy='joined')