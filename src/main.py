from fastapi import FastAPI
from loguru import logger

from src.database import engine
from src.models import Base

app = FastAPI(
    title="BeanTotal Accounting Automation Platform",
    description="An online platform for automating business processes at accounting firms.",
    version="0.0.1",
)


@app.on_event("startup")
async def startup():
    # On startup, ensure that all database tables exist
    Base.metadata.drop_all(bind=engine)
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)


@app.get("/")
async def root():
    return {"message": "Hello, Accountant!"}
