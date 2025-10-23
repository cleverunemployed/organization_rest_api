from sqlalchemy import Column, Integer, String, Float, ForeignKey, Table, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

organization_phones = Table(
    'organization_phones',
    Base.metadata,
    Column('organization_id', Integer, ForeignKey('organizations.id')),
    Column('phone_number', String(20))
)

organization_activities = Table(
    'organization_activities',
    Base.metadata,
    Column('organization_id', Integer, ForeignKey('organizations.id')),
    Column('activity_id', Integer, ForeignKey('activities.id'))
)

class Building(Base):
    __tablename__ = "buildings"
    
    id = Column(Integer, primary_key=True, index=True)
    address = Column(String(255), nullable=False, unique=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    organizations = relationship("Organization", back_populates="building")

class Activity(Base):
    __tablename__ = "activities"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    parent_id = Column(Integer, ForeignKey('activities.id'), nullable=True)
    
    parent = relationship("Activity", remote_side=[id], back_populates="children")
    children = relationship("Activity", back_populates="parent")
    
    organizations = relationship("Organization", secondary=organization_activities, back_populates="activities")

class Organization(Base):
    __tablename__ = "organizations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    building_id = Column(Integer, ForeignKey('buildings.id'), nullable=False)
    
    building = relationship("Building", back_populates="organizations")
    activities = relationship("Activity", secondary=organization_activities, back_populates="organizations")
    
    @property
    def phone_numbers(self):
        return []