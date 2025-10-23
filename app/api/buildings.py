from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..dao import dao
from .. import schemas, dependencies
from ..database import get_db

router = APIRouter()

@router.get("/", response_model=List[schemas.Building])
def read_buildings(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    api_key: str = Depends(dependencies.verify_api_key)
):
    buildings = dao.get_buildings(db, skip=skip, limit=limit)
    return buildings

@router.get("/{building_id}", response_model=schemas.Building)
def read_building(
    building_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(dependencies.verify_api_key)
):
    building = dao.get_building(db, building_id=building_id)
    if building is None:
        raise HTTPException(status_code=404, detail="Building not found")
    return building

@router.post("/", response_model=schemas.Building)
def create_building(
    building: schemas.BuildingCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(dependencies.verify_api_key)
):
    return dao.create_building(db=db, building=building)