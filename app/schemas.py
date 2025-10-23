from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class PhoneNumber(BaseModel):
    number: str

class ActivityBase(BaseModel):
    name: str

class ActivityCreate(ActivityBase):
    parent_id: Optional[int] = None

class Activity(ActivityBase):
    id: int
    parent_id: Optional[int] = None
    children: List['Activity'] = []
    
    model_config = ConfigDict(from_attributes=True)

class ActivityWithLevel(Activity):
    level: int

class BuildingBase(BaseModel):
    address: str
    latitude: float
    longitude: float

class BuildingCreate(BuildingBase):
    pass

class Building(BuildingBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)

class OrganizationBase(BaseModel):
    name: str
    building_id: int

class OrganizationCreate(OrganizationBase):
    phone_numbers: List[str] = []
    activity_ids: List[int] = []

class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    building_id: Optional[int] = None
    phone_numbers: Optional[List[str]] = None
    activity_ids: Optional[List[int]] = None

class Organization(OrganizationBase):
    id: int
    phone_numbers: List[str] = []
    activities: List[Activity] = []
    building: Building
    
    model_config = ConfigDict(from_attributes=True)

class OrganizationSimple(BaseModel):
    id: int
    name: str
    building: Building
    activities: List[Activity] = []
    
    model_config = ConfigDict(from_attributes=True)

class Coordinate(BaseModel):
    latitude: float
    longitude: float

class RadiusSearch(BaseModel):
    center: Coordinate
    radius_km: float

class RectangleSearch(BaseModel):
    north_east: Coordinate
    south_west: Coordinate

class PaginatedResponse(BaseModel):
    items: List
    total: int
    page: int
    size: int
    pages: int

Activity.model_rebuild()
ActivityWithLevel.model_rebuild()