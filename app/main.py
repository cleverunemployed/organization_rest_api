from fastapi import FastAPI

from .database import engine
from . import models
from .api import organizations, buildings


models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Organization Directory API",
    description="REST API для справочника Организаций, Зданий и Деятельности",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.include_router(
    organizations.router,
    prefix="/api/organizations",
    tags=["organizations"]
)

app.include_router(
    buildings.router,
    prefix="/api/buildings",
    tags=["buildings"]
)

@app.get("/")
def read_root():
    return {
        "message": "Organization Directory API",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}