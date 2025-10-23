import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal
from app import schemas
from app.dao import dao

def seed_data():
    db = SessionLocal()
    
    try:
        # Create buildings
        buildings_data = [
            {"address": "г. Москва, ул. Ленина 1, офис 3", "latitude": 55.7558, "longitude": 37.6173},
            {"address": "г. Москва, ул. Тверская 10", "latitude": 55.7602, "longitude": 37.6085},
            {"address": "г. Москва, пр. Мира 25", "latitude": 55.7818, "longitude": 37.6339},
            {"address": "г. Москва, ул. Блюхера 32/1", "latitude": 55.7912, "longitude": 37.6618},
        ]
        
        buildings = []
        for building_data in buildings_data:
            building = dao.create_building(db, schemas.BuildingCreate(**building_data))
            buildings.append(building)
            print(f"Created building: {building.address}")
        
        # Create activities tree
        activities_data = [
            {"name": "Еда", "parent_id": None},
            {"name": "Мясная продукция", "parent_id": 1},
            {"name": "Молочная продукция", "parent_id": 1},
            {"name": "Автомобили", "parent_id": None},
            {"name": "Грузовые", "parent_id": 4},
            {"name": "Легковые", "parent_id": 4},
            {"name": "Запчасти", "parent_id": 6},
            {"name": "Аксессуары", "parent_id": 6},
            {"name": "IT услуги", "parent_id": None},
            {"name": "Разработка ПО", "parent_id": 9},
            {"name": "Техподдержка", "parent_id": 9},
        ]
        
        activities = []
        for activity_data in activities_data:
            activity = dao.create_activity(db, schemas.ActivityCreate(**activity_data))
            activities.append(activity)
            print(f"Created activity: {activity.name}")
        
        # Create organizations
        organizations_data = [
            {
                "name": 'ООО "Рога и Копыта"',
                "building_id": buildings[0].id,
                "phone_numbers": ["2-222-222", "3-333-333"],
                "activity_ids": [activities[1].id, activities[2].id]  # Мясная и молочная продукция
            },
            {
                "name": 'ЗАО "АвтоМир"',
                "building_id": buildings[1].id,
                "phone_numbers": ["4-444-444"],
                "activity_ids": [activities[4].id, activities[5].id]  # Грузовые и легковые
            },
            {
                "name": 'ИП "Молочные реки"',
                "building_id": buildings[2].id,
                "phone_numbers": ["5-555-555", "6-666-666"],
                "activity_ids": [activities[2].id]  # Молочная продукция
            },
            {
                "name": 'ООО "ТехноСервис"',
                "building_id": buildings[3].id,
                "phone_numbers": ["7-777-777"],
                "activity_ids": [activities[9].id, activities[10].id]  # Разработка ПО и техподдержка
            },
        ]
        
        for org_data in organizations_data:
            organization = dao.create_organization(db, schemas.OrganizationCreate(**org_data))
            print(f"Created organization: {organization.name}")
        
        print("Database seeded successfully!")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()