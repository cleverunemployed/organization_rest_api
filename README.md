# organization_rest_api

##### Собрать docker

1. docker-compose up --build -d
2. миграцию docker-compose exec web alembic revision --autogenerate -m "Initial migration"
3. Заполнить данными docker-compose exec web python scripts/seed_data.py
