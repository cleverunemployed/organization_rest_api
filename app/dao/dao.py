from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_

import math
from ..models import models, schemas


def get_building(db: Session, building_id: int):
    return db.query(models.Building).filter(models.Building.id == building_id).first()

def get_buildings(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Building).offset(skip).limit(limit).all()

def create_building(db: Session, building: schemas.BuildingCreate):
    db_building = models.Building(
        address=building.address,
        latitude=building.latitude,
        longitude=building.longitude
    )
    db.add(db_building)
    db.commit()
    db.refresh(db_building)
    return db_building



def get_activity(db: Session, activity_id: int):
    return db.query(models.Activity).filter(models.Activity.id == activity_id).first()

def get_activities(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Activity).offset(skip).limit(limit).all()

def create_activity(db: Session, activity: schemas.ActivityCreate):
    db_activity = models.Activity(
        name=activity.name,
        parent_id=activity.parent_id
    )
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity

def get_activities_tree(db: Session, max_level: int = 3):
    def build_tree(parent_id=None, level=0):
        if level >= max_level:
            return []
        
        query = db.query(models.Activity)
        if parent_id is None:
            query = query.filter(models.Activity.parent_id.is_(None))
        else:
            query = query.filter(models.Activity.parent_id == parent_id)
        
        activities = query.all()
        result = []
        for activity in activities:
            activity_data = schemas.ActivityWithLevel(
                id=activity.id,
                name=activity.name,
                parent_id=activity.parent_id,
                level=level,
                children=build_tree(activity.id, level + 1)
            )
            result.append(activity_data)
        return result
    
    return build_tree()

def get_activity_descendants(db: Session, activity_id: int):
    def get_descendants_ids(parent_id, descendants=None):
        if descendants is None:
            descendants = set()
        
        activities = db.query(models.Activity).filter(models.Activity.parent_id == parent_id).all()
        for activity in activities:
            descendants.add(activity.id)
            get_descendants_ids(activity.id, descendants)
        
        return descendants
    
    descendants = get_descendants_ids(activity_id)
    descendants.add(activity_id) 
    return descendants



def get_organization(db: Session, organization_id: int):
    return db.query(models.Organization)\
        .options(joinedload(models.Organization.building))\
        .options(joinedload(models.Organization.activities))\
        .filter(models.Organization.id == organization_id)\
        .first()

def get_organizations(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Organization)\
        .options(joinedload(models.Organization.building))\
        .options(joinedload(models.Organization.activities))\
        .offset(skip).limit(limit).all()

def create_organization(db: Session, organization: schemas.OrganizationCreate):
    db_organization = models.Organization(
        name=organization.name,
        building_id=organization.building_id
    )
    db.add(db_organization)
    db.commit()
    db.refresh(db_organization)

    return db_organization


def get_organizations_by_building(db: Session, building_id: int):
    return db.query(models.Organization)\
        .options(joinedload(models.Organization.building))\
        .options(joinedload(models.Organization.activities))\
        .filter(models.Organization.building_id == building_id)\
        .all()

def get_organizations_by_activity(db: Session, activity_id: int):
    activity_descendants = get_activity_descendants(db, activity_id)
    
    return db.query(models.Organization)\
        .options(joinedload(models.Organization.building))\
        .options(joinedload(models.Organization.activities))\
        .join(models.organization_activities)\
        .filter(models.organization_activities.c.activity_id.in_(activity_descendants))\
        .all()

def search_organizations_by_name(db: Session, name: str):
    return db.query(models.Organization)\
        .options(joinedload(models.Organization.building))\
        .options(joinedload(models.Organization.activities))\
        .filter(models.Organization.name.ilike(f"%{name}%"))\
        .all()

def search_organizations_by_activity_tree(db: Session, activity_name: str):
    matching_activities = db.query(models.Activity)\
        .filter(models.Activity.name.ilike(f"%{activity_name}%"))\
        .all()
    
    if not matching_activities:
        return []
    
    all_activity_ids = set()
    for activity in matching_activities:
        descendants = get_activity_descendants(db, activity.id)
        all_activity_ids.update(descendants)
    
    return db.query(models.Organization)\
        .options(joinedload(models.Organization.building))\
        .options(joinedload(models.Organization.activities))\
        .join(models.organization_activities)\
        .filter(models.organization_activities.c.activity_id.in_(all_activity_ids))\
        .all()




def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = (math.sin(delta_lat / 2) ** 2 + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

def get_organizations_in_radius(db: Session, center: schemas.Coordinate, radius_km: float):
    all_organizations = db.query(models.Organization)\
        .options(joinedload(models.Organization.building))\
        .options(joinedload(models.Organization.activities))\
        .all()
    
    organizations_in_radius = []
    for org in all_organizations:
        distance = haversine_distance(
            center.latitude, center.longitude,
            org.building.latitude, org.building.longitude
        )
        if distance <= radius_km:
            organizations_in_radius.append(org)
    
    return organizations_in_radius

def get_organizations_in_rectangle(db: Session, north_east: schemas.Coordinate, south_west: schemas.Coordinate):
    return db.query(models.Organization)\
        .options(joinedload(models.Organization.building))\
        .options(joinedload(models.Organization.activities))\
        .join(models.Building)\
        .filter(and_(
            models.Building.latitude.between(south_west.latitude, north_east.latitude),
            models.Building.longitude.between(south_west.longitude, north_east.longitude)
        ))\
        .all()