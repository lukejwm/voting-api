import datetime

from fastapi import FastAPI, Depends
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy import Boolean, Column, String, Integer, DateTime, Table

app = FastAPI()

# SqlAlchemy Setup
load_dotenv()
DB_URL = os.getenv('DB_URL')
engine = create_engine(DB_URL, echo=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Database schema
class ProjectVotesDB(Base):
    __tablename__ = "project_votes"

    ProjectID = Column(Integer, primary_key=True)
    ProjectName = Column(String, unique=True)
    ProjectCountry = Column(String)
    IconCode = Column(String)
    GraphColour = Column(String)
    VoteCount = Column(Integer)


class VoucherCodesDB(Base):
    __tablename__ = "voucher_codes"

    VoucherID = Column(Integer, primary_key=True, index=True)
    Voucher = Column(Integer, unique=True)
    ExpiryDate = Column(DateTime)
    Used = Column(Boolean, default=False)
    ProjectID = Column(Integer, nullable=True)


# API response schema
class ProjectVotes(BaseModel):
    ProjectName: str
    ProjectCountry: str
    IconCode: str
    GraphColour: str
    VoteCount: int

    class Config:
        orm_mode = True


class VoucherCodes(BaseModel):
    VoucherID: int
    Voucher: int
    ExpiryDate: datetime.datetime
    Used: bool
    ProjectID: Optional[int] = None

    class Config:
        orm_mode = True


def get_all_project_votes(db: Session):
    return db.query(ProjectVotesDB).all()


def get_voucher(db: Session, code: int):
    return db.query(VoucherCodesDB).where(VoucherCodesDB.Voucher == code).first()


# Select * from project_votes;
@app.get("/projects/votes-summary/", response_model=List[ProjectVotes])
async def get_all_project_votes_view(db: Session = Depends(get_db)):
    return get_all_project_votes(db)


@app.get("/voucher/{code}", response_model=VoucherCodes)
async def get_voucher_code_view(code: int, db: Session = Depends(get_db)):
    return get_voucher(db, code)


@app.post("/voucher/vote/{code}")
async def post_voucher_vote_view(code: int, proj_id: int, de: Session = Depends(get_db)):
    return {"VoucherCode": code, "ProjectId": proj_id}


#
# @app.post("/vote/")
# async def vote_for_project(voucher_code: int, project_id: int):
#     # Algorithm
#     # Search the database for the given voucher code - if not found, return an error
#     # Check that the expiry is still within date or that the voucher has not already been used
#     #   - if not, return message saying that the voucher has expired or that it has already been used
#     # Update the column with the voucher code:
#     #   - mark "used" column as true and update the project id column with the id that the user has voted for
#     # Update the vote counts:
#     #  - for each project id, execute a count query that will return how many times a project has been voted for
#     #  - update the project table with the new count
#
#     return voucher_code, project_id
