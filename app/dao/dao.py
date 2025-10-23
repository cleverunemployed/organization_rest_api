import math
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from typing import List, Optional
from .. import models, schemas

def get_organization_phones(db: Session, organization_id: int) -> List[str]:
    """Get all phone numbers for an organization"""
    result = db.execute(
        models.organization_phones.select().where(
            models.organization_phones.c.organization_id == organization_id
        )
    )
    return [row.phone_number for row in result]

def add_organization_phone(db: Session, organization_id: int, phone_number: str):
    existing = db.execute(
        models.organization_phones.select().where(
            (models.organization_phones.c.organization_id == organization_id) &
            (models.organization_phones.c.phone_number == phone_number)
        )
    ).first()
    
    if not existing:
        db.execute(
            models.organization_phones.insert().values(
                organization_id=organization_id,
                phone_number=phone_number
            )
        )
        db.commit()
        return True
    return False

def remove_organization_phone(db: Session, organization_id: int, phone_number: str):
    result = db.execute(
        models.organization_phones.delete().where(
            (models.organization_phones.c.organization_id == organization_id) &
            (models.organization_phones.c.phone_number == phone_number)
        )
    )
    db.commit()
    return result.rowcount > 0

def set_organization_phones(db: Session, organization_id: int, phone_numbers: List[str]):
    db.execute(
        models.organization_phones.delete().where(
            models.organization_phones.c.organization_id == organization_id
        )
    )
    
    for phone in phone_numbers:
        db.execute(
            models.organization_phones.insert().values(
                organization_id=organization_id,
                phone_number=phone
            )
        )
    db.commit()

def _add_phone_numbers_to_organizations(db: Session, organizations: List[models.Organization]):
    for org in organizations:
        org._phone_numbers = get_organization_phones(db, org.id)
    return organizations

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
    organization = db.query(models.Organization)\
        .options(joinedload(models.Organization.building))\
        .options(joinedload(models.Organization.activities))\
        .filter(models.Organization.id == organization_id)\
        .first()
    
    if organization:
        organization._phone_numbers = get_organization_phones(db, organization_id)
    
    return organization

def get_organizations(db: Session, skip: int = 0, limit: int = 100):
    organizations = db.query(models.Organization)\
        .options(joinedload(models.Organization.building))\
        .options(joinedload(models.Organization.activities))\
        .offset(skip).limit(limit).all()
    
    return _add_phone_numbers_to_organizations(db, organizations)

def create_organization(db: Session, organization: schemas.OrganizationCreate):
    db_organization = models.Organization(
        name=organization.name,
        building_id=organization.building_id
    )
    db.add(db_organization)
    db.commit()
    db.refresh(db_organization)

    if organization.phone_numbers:
        set_organization_phones(db, db_organization.id, organization.phone_numbers)
    
    if organization.activity_ids:
        for activity_id in organization.activity_ids:
            db.execute(
                models.organization_activities.insert().values(
                    organization_id=db_organization.id,
                    activity_id=activity_id
                )
            )
        db.commit()

    db_organization = get_organization(db, db_organization.id)
    return db_organization

def update_organization(db: Session, organization_id: int, organization_update: schemas.OrganizationUpdate):
    db_organization = get_organization(db, organization_id)
    if not db_organization:
        return None
    
    update_data = organization_update.model_dump(exclude_unset=True)

    if 'name' in update_data:
        db_organization.name = update_data['name']
    if 'building_id' in update_data:
        db_organization.building_id = update_data['building_id']
    
    if 'phone_numbers' in update_data:
        set_organization_phones(db, organization_id, update_data['phone_numbers'])
    
    if 'activity_ids' in update_data:
        db.execute(
            models.organization_activities.delete().where(
                models.organization_activities.c.organization_id == organization_id
            )
        )
        for activity_id in update_data['activity_ids']:
            db.execute(
                models.organization_activities.insert().values(
                    organization_id=organization_id,
                    activity_id=activity_id
                )
            )
    
    db.commit()
    db.refresh(db_organization)

    return get_organization(db, organization_id)

def delete_organization(db: Session, organization_id: int):
    db_organization = get_organization(db, organization_id)
    if db_organization:
        db.delete(db_organization)
        db.commit()
        return True
    return False

def get_organizations_by_building(db: Session, building_id: int):
    organizations = db.query(models.Organization)\
        .options(joinedload(models.Organization.building))\
        .options(joinedload(models.Organization.activities))\
        .filter(models.Organization.building_id == building_id)\
        .all()
    
    return _add_phone_numbers_to_organizations(db, organizations)

def get_organizations_by_activity(db: Session, activity_id: int):
    activity_descendants = get_activity_descendants(db, activity_id)
    
    organizations = db.query(models.Organization)\
        .options(joinedload(models.Organization.building))\
        .options(joinedload(models.Organization.activities))\
        .join(models.organization_activities)\
        .filter(models.organization_activities.c.activity_id.in_(activity_descendants))\
        .all()
    
    return _add_phone_numbers_to_organizations(db, organizations)

def search_organizations_by_name(db: Session, name: str):
    organizations = db.query(models.Organization)\
        .options(joinedload(models.Organization.building))\
        .options(joinedload(models.Organization.activities))\
        .filter(models.Organization.name.ilike(f"%{name}%"))\
        .all()
    
    return _add_phone_numbers_to_organizations(db, organizations)

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
    
    organizations = db.query(models.Organization)\
        .options(joinedload(models.Organization.building))\
        .options(joinedload(models.Organization.activities))\
        .join(models.organization_activities)\
        .filter(models.organization_activities.c.activity_id.in_(all_activity_ids))\
        .all()
    
    return _add_phone_numbers_to_organizations(db, organizations)

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
    
    return _add_phone_numbers_to_organizations(db, organizations_in_radius)

def get_organizations_in_rectangle(db: Session, north_east: schemas.Coordinate, south_west: schemas.Coordinate):
    organizations = db.query(models.Organization)\
        .options(joinedload(models.Organization.building))\
        .options(joinedload(models.Organization.activities))\
        .join(models.Building)\
        .filter(and_(
            models.Building.latitude.between(south_west.latitude, north_east.latitude),
            models.Building.longitude.between(south_west.longitude, north_east.longitude)
        ))\
        .all()
    
    return _add_phone_numbers_to_organizations(db, organizations)

def search_organizations_comprehensive(
    db: Session,
    name: Optional[str] = None,
    building_id: Optional[int] = None,
    activity_id: Optional[int] = None,
    activity_name: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):

    query = db.query(models.Organization)\
        .options(joinedload(models.Organization.building))\
        .options(joinedload(models.Organization.activities))
    
    if name:
        query = query.filter(models.Organization.name.ilike(f"%{name}%"))
    
    if building_id:
        query = query.filter(models.Organization.building_id == building_id)
    
    if activity_id:
        activity_descendants = get_activity_descendants(db, activity_id)
        query = query.join(models.organization_activities)\
            .filter(models.organization_activities.c.activity_id.in_(activity_descendants))
    
    if activity_name:
        matching_activities = db.query(models.Activity)\
            .filter(models.Activity.name.ilike(f"%{activity_name}%"))\
            .all()
        if matching_activities:
            all_activity_ids = set()
            for activity in matching_activities:
                descendants = get_activity_descendants(db, activity.id)
                all_activity_ids.update(descendants)
            query = query.join(models.organization_activities)\
                .filter(models.organization_activities.c.activity_id.in_(all_activity_ids))
    
    organizations = query.offset(skip).limit(limit).all()
    return _add_phone_numbers_to_organizations(db, organizations)

def get_organizations_with_phones_by_pattern(db: Session, phone_pattern: str):
    phone_matches = db.execute(
        models.organization_phones.select().where(
            models.organization_phones.c.phone_number.ilike(f"%{phone_pattern}%")
        )
    ).fetchall()
    
    if not phone_matches:
        return []
    
    organization_ids = [match.organization_id for match in phone_matches]
    
    organizations = db.query(models.Organization)\
        .options(joinedload(models.Organization.building))\
        .options(joinedload(models.Organization.activities))\
        .filter(models.Organization.id.in_(organization_ids))\
        .all()
    
    return _add_phone_numbers_to_organizations(db, organizations)