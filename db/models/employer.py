from sqlalchemy import Column, Integer, String, ForeignKey, Float, Table, Text
from sqlalchemy.orm import relationship
from pydantic import BaseModel, EmailStr
from typing import Optional
from db.db_connection import Base
# from db.models.user import UserEmployerJobs

class EmployerSchema(BaseModel):
    name: Optional[str] = None
    info: Optional[str] = None
    logo: Optional[str] = None
    location: Optional[str] = None
    businessnature: Optional[str] = None

class Employer(Base):
    __tablename__ = "employers"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
    info = Column(String, nullable=True)
    logo = Column(String, nullable=True)
    location = Column(String, nullable=True)
    businessnature = Column(String, nullable=True)
    
    jobs = relationship('EmployerJobs', back_populates='employer', lazy="joined")


class EmployerJobs(Base):
    __tablename__ = "employer_jobs"

    id = Column(Integer, primary_key=True, index=True)
    employer_id = Column(Integer, ForeignKey("employers.id", ondelete="CASCADE"))
    name = Column(String)
    description = Column(Text)
    desc_json = Column(Text)
    summary = Column(Text)
    responsibilities = Column(Text)
    qualifications = Column(Text)
    skills = Column(Text)
    experience = Column(Text)
    experienceyear = Column(String)
    postedtime = Column(String)
    jobtype = Column(String)
    workmode = Column(String)
    level = Column(String)
    location = Column(String)

    employer = relationship("Employer", back_populates="jobs", lazy='joined')
    user_employer_jobs = relationship('UserEmployerJobs', back_populates='jobs', lazy='joined', uselist=True)
