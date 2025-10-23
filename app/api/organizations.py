from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from .. import schemas, dependencies
from ..database import get_db
from ..dao import dao



router = APIRouter()

@router.get("/", response_model=List[schemas.Organization])
def read_organizations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    api_key: str = Depends(dependencies.verify_api_key)
):
    organizations = dao.get_organizations(db, skip=skip, limit=limit)
    return organizations

@router.get("/{organization_id}", response_model=schemas.Organization)
def read_organization(
    organization_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(dependencies.verify_api_key)
):
    organization = dao.get_organization(db, organization_id=organization_id)
    if organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    return organization

@router.post("/", response_model=schemas.Organization)
def create_organization(
    organization: schemas.OrganizationCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(dependencies.verify_api_key)
):
    return dao.create_organization(db=db, organization=organization)

@router.put("/{organization_id}", response_model=schemas.Organization)
def update_organization(
    organization_id: int,
    organization_update: schemas.OrganizationUpdate,
    db: Session = Depends(get_db),
    api_key: str = Depends(dependencies.verify_api_key)
):
    organization = dao.update_organization(db, organization_id=organization_id, organization_update=organization_update)
    if organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    return organization

@router.delete("/{organization_id}")
def delete_organization(
    organization_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(dependencies.verify_api_key)
):
    success = dao.delete_organization(db, organization_id=organization_id)
    if not success:
        raise HTTPException(status_code=404, detail="Organization not found")
    return {"message": "Organization deleted successfully"}

@router.get("/building/{building_id}", response_model=List[schemas.Organization])
def get_organizations_by_building(
    building_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(dependencies.verify_api_key)
):
    organizations = dao.get_organizations_by_building(db, building_id=building_id)
    return organizations

@router.get("/activity/{activity_id}", response_model=List[schemas.Organization])
def get_organizations_by_activity(
    activity_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(dependencies.verify_api_key)
):
    organizations = dao.get_organizations_by_activity(db, activity_id=activity_id)
    return organizations

@router.post("/search/radius", response_model=List[schemas.Organization])
def search_organizations_in_radius(
    search: schemas.RadiusSearch,
    db: Session = Depends(get_db),
    api_key: str = Depends(dependencies.verify_api_key)
):
    organizations = dao.get_organizations_in_radius(db, center=search.center, radius_km=search.radius_km)
    return organizations

@router.post("/search/rectangle", response_model=List[schemas.Organization])
def search_organizations_in_rectangle(
    search: schemas.RectangleSearch,
    db: Session = Depends(get_db),
    api_key: str = Depends(dependencies.verify_api_key)
):
    organizations = dao.get_organizations_in_rectangle(db, north_east=search.north_east, south_west=search.south_west)
    return organizations

@router.get("/search/name/{name}", response_model=List[schemas.Organization])
def search_organizations_by_name(
    name: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(dependencies.verify_api_key)
):
    organizations = dao.search_organizations_by_name(db, name=name)
    return organizations

@router.get("/search/activity/{activity_name}", response_model=List[schemas.Organization])
def search_organizations_by_activity_tree(
    activity_name: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(dependencies.verify_api_key)
):
    organizations = dao.search_organizations_by_activity_tree(db, activity_name=activity_name)
    return organizations

@router.get("/search/phone/{phone_pattern}", response_model=List[schemas.Organization])
def search_organizations_by_phone(
    phone_pattern: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(dependencies.verify_api_key)
):
    organizations = dao.get_organizations_with_phones_by_pattern(db, phone_pattern=phone_pattern)
    return organizations

@router.get("/search/comprehensive/", response_model=List[schemas.Organization])
def search_organizations_comprehensive(
    name: Optional[str] = Query(None),
    building_id: Optional[int] = Query(None),
    activity_id: Optional[int] = Query(None),
    activity_name: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    api_key: str = Depends(dependencies.verify_api_key)
):
    organizations = dao.search_organizations_comprehensive(
        db,
        name=name,
        building_id=building_id,
        activity_id=activity_id,
        activity_name=activity_name,
        skip=skip,
        limit=limit
    )
    return organizations