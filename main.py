from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base, Session, relationship
from pydantic import BaseModel, constr
from typing import List, Optional
import requests

# Initialize FastAPI app
app = FastAPI()

# TheCatAPI URL for breed validation
CAT_API_URL = "https://api.thecatapi.com/v1/breeds"

# Database setup
DATABASE_URL = "sqlite:///./spy_cat_agency.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper function to get Mission by ID
def get_mission_by_id(mission_id: int, db: Session):
    mission = db.query(Mission).filter(Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    return mission

# Helper function to validate cat breed
def validate_cat_breed(breed: str):
    try:
        response = requests.get(CAT_API_URL)
        response.raise_for_status()
        breeds = [b["name"].lower() for b in response.json()]
        if breed.lower() not in breeds:
            raise HTTPException(status_code=400, detail=f"Breed '{breed}' is not recognized.")
    except requests.RequestException as e:
        raise HTTPException(status_code=503, detail="Unable to validate breed due to external API error.")

# Spy Cat, Mission and Target Database Models
class SpyCat(Base):
    __tablename__ = "spy_cats"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    experience_years = Column(Integer, nullable=False)
    breed = Column(String, nullable=False)
    salary = Column(Float, nullable=False)
    current_mission_id = Column(Integer, ForeignKey("missions.id"), nullable=True)
    current_mission = relationship("Mission", back_populates="assigned_cats")

class Mission(Base):
    __tablename__ = "missions"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=False)
    is_completed = Column(Boolean, default=False)
    assigned_cats = relationship("SpyCat", back_populates="current_mission")
    targets = relationship("Target", back_populates="mission", cascade="all, delete-orphan")

class Target(Base):
    __tablename__ = "targets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    country = Column(String, nullable=False)
    notes = Column(String, nullable=True)
    is_completed = Column(Boolean, default=False)
    mission_id = Column(Integer, ForeignKey("missions.id"), nullable=False)
    mission = relationship("Mission", back_populates="targets")

# Spy Cat, Mission and Target Pydantic Schema
class SpyCatBase(BaseModel):
    name: str
    experience_years: int
    breed: str
    salary: float

class SpyCatCreate(SpyCatBase):
    pass

class SpyCatRead(SpyCatBase):
    id: int
    current_mission_id: Optional[int]

    class Config:
        from_attributes = True

class TargetBase(BaseModel):
    name: str
    country: str
    notes: Optional[str]
    is_completed: Optional[bool] = False

class TargetCreate(TargetBase):
    pass

class TargetRead(TargetBase):
    id: int

    class Config:
        from_attributes = True

class MissionBase(BaseModel):
    description: str
    is_completed: Optional[bool] = False

class MissionCreate(MissionBase):
    targets: List[TargetCreate]

class MissionRead(MissionBase):
    id: int
    targets: List[TargetRead]
    assigned_cats: List[SpyCatRead]

    class Config:
        from_attributes = True

# Create Database Tables
Base.metadata.create_all(bind=engine)

# API Endpoints for Spy Cats Management
@app.post("/spy_cats/", response_model=SpyCatRead)
def create_spy_cat(spy_cat: SpyCatCreate, db: Session = Depends(get_db)):
    validate_cat_breed(spy_cat.breed)
    db_spy_cat = SpyCat(**spy_cat.model_dump())
    db.add(db_spy_cat)
    db.commit()
    db.refresh(db_spy_cat)
    return db_spy_cat

@app.get("/spy_cats/", response_model=List[SpyCatRead])
def list_spy_cats(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(SpyCat).offset(skip).limit(limit).all()

@app.get("/spy_cats/{spy_cat_id}", response_model=SpyCatRead)
def read_spy_cat(spy_cat_id: int, db: Session = Depends(get_db)):
    spy_cat = db.query(SpyCat).filter(SpyCat.id == spy_cat_id).first()
    if not spy_cat:
        raise HTTPException(status_code=404, detail="Spy Cat not found")
    return spy_cat

@app.put("/spy_cats/{spy_cat_id}", response_model=SpyCatRead)
def update_spy_cat(spy_cat_id: int, spy_cat: SpyCatCreate, db: Session = Depends(get_db)):
    validate_cat_breed(spy_cat.breed)
    db_spy_cat = db.query(SpyCat).filter(SpyCat.id == spy_cat_id).first()
    if not db_spy_cat:
        raise HTTPException(status_code=404, detail="Spy Cat not found")
    for key, value in spy_cat.model_dump().items():
        setattr(db_spy_cat, key, value)
    db.commit()
    db.refresh(db_spy_cat)
    return db_spy_cat

@app.post("/spy_cats/{spy_cat_id}/assign_mission/", response_model=SpyCatRead)
def assign_mission_to_cat(spy_cat_id: int, mission_id: int, db: Session = Depends(get_db)):
    spy_cat = db.query(SpyCat).filter(SpyCat.id == spy_cat_id).first()
    if not spy_cat:
        raise HTTPException(status_code=404, detail="Spy Cat not found")

    if spy_cat.current_mission_id:
        raise HTTPException(status_code=400, detail="Spy Cat already has an active mission")

    mission = get_mission_by_id(mission_id, db)

    if mission.is_completed:
        raise HTTPException(status_code=400, detail="Cannot assign a completed mission")

    spy_cat.current_mission_id = mission_id
    db.commit()
    db.refresh(spy_cat)
    return spy_cat

@app.delete("/spy_cats/{spy_cat_id}", response_model=dict)
def delete_spy_cat(spy_cat_id: int, db: Session = Depends(get_db)):
    db_spy_cat = db.query(SpyCat).filter(SpyCat.id == spy_cat_id).first()
    if not db_spy_cat:
        raise HTTPException(status_code=404, detail="Spy Cat not found")
    db.delete(db_spy_cat)
    db.commit()
    return {"detail": "Spy Cat deleted"}

@app.post("/missions/", response_model=MissionRead)
def create_mission(mission: MissionCreate, db: Session = Depends(get_db)):
    db_mission = Mission(description=mission.description, is_completed=mission.is_completed)
    db.add(db_mission)
    db.commit()
    db.refresh(db_mission)
    for target in mission.targets:
        db_target = Target(**target.model_dump(), mission_id=db_mission.id)
        db.add(db_target)
    db.commit()
    db.refresh(db_mission)
    return db_mission

@app.get("/missions/", response_model=List[MissionRead])
def list_missions(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(Mission).offset(skip).limit(limit).all()

@app.get("/missions/{mission_id}", response_model=MissionRead)
def read_mission(mission_id: int, db: Session = Depends(get_db)):
    mission = get_mission_by_id(mission_id, db)
    mission.assigned_cats = db.query(SpyCat).filter(SpyCat.current_mission_id == mission_id).all()
    return mission

@app.put("/missions/{mission_id}", response_model=MissionRead)
def update_mission(mission_id: int, mission: MissionBase, db: Session = Depends(get_db)):
    db_mission = get_mission_by_id(mission_id, db)
    if db_mission.is_completed:
        raise HTTPException(status_code=400, detail="Cannot update a completed mission")
    for key, value in mission.model_dump().items():
        setattr(db_mission, key, value)
    db.commit()
    db.refresh(db_mission)
    return db_mission

@app.delete("/missions/{mission_id}", response_model=dict)
def delete_mission(mission_id: int, db: Session = Depends(get_db)):
    db_mission = get_mission_by_id(mission_id, db)
    if db_mission.assigned_cats:
        raise HTTPException(status_code=400, detail="Cannot delete a mission assigned to a cat")
    db.delete(db_mission)
    db.commit()
    return {"detail": "Mission deleted"}
