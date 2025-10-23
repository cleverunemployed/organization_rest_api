from typing import List
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
    def phone_numbers(self) -> List[str]:
        from .database import SessionLocal
        db = SessionLocal()
        try:
            result = db.execute(
                organization_phones.select().where(
                    organization_phones.c.organization_id == self.id
                )
            )
            phones = [row.phone_number for row in result]
            return phones
        finally:
            db.close()
    
    def add_phone_number(self, phone_number: str) -> None:
        from .database import SessionLocal
        db = SessionLocal()
        try:
            existing = db.execute(
                organization_phones.select().where(
                    (organization_phones.c.organization_id == self.id) &
                    (organization_phones.c.phone_number == phone_number)
                )
            ).first()
            
            if not existing:
                db.execute(
                    organization_phones.insert().values(
                        organization_id=self.id,
                        phone_number=phone_number
                    )
                )
                db.commit()
        finally:
            db.close()
    
    def remove_phone_number(self, phone_number: str) -> None:
        from .database import SessionLocal
        db = SessionLocal()
        try:
            db.execute(
                organization_phones.delete().where(
                    (organization_phones.c.organization_id == self.id) &
                    (organization_phones.c.phone_number == phone_number)
                )
            )
            db.commit()
        finally:
            db.close()
    
    def set_phone_numbers(self, phone_numbers: List[str]) -> None:
        from .database import SessionLocal
        db = SessionLocal()
        try:
            db.execute(
                organization_phones.delete().where(
                    organization_phones.c.organization_id == self.id
                )
            )

            for phone in phone_numbers:
                db.execute(
                    organization_phones.insert().values(
                        organization_id=self.id,
                        phone_number=phone
                    )
                )
            db.commit()
        finally:
            db.close()