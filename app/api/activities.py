from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..dao import dao
from .. import schemas, dependencies
from ..database import get_db

router = APIRouter()

@router.get("/", response_model=List[schemas.Activity])
def read_activities(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    api_key: str = Depends(dependencies.verify_api_key)
):
    activities = dao.get_activities(db, skip=skip, limit=limit)
    return activities

@router.get("/tree", response_model=List[schemas.ActivityWithLevel])
def read_activities_tree(
    max_level: int = 3,
    db: Session = Depends(get_db),
    api_key: str = Depends(dependencies.verify_api_key)
):
    activities = dao.get_activities_tree(db, max_level=max_level)
    return activities

@router.get("/{activity_id}", response_model=schemas.Activity)
def read_activity(
    activity_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(dependencies.verify_api_key)
):
    activity = dao.get_activity(db, activity_id=activity_id)
    if activity is None:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activity

@router.post("/", response_model=schemas.Activity)
def create_activity(
    activity: schemas.ActivityCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(dependencies.verify_api_key)
):
    return dao.create_activity(db=db, activity=activity)