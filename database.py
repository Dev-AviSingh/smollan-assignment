from sqlmodel import Field, Session, SQLModel, create_engine
from typing import Annotated
from fastapi import Depends
from models import *
from config import *
from logger import logger
import motor.motor_asyncio




logger.info("Creating mongodb connection.")

mongo_client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI)
mongo_db = mongo_client.smollan
clients_collection = mongo_db.get_collection("clients")

logger.info("Created mongodb connection successfully.")

engine = create_engine(SQL_URI)
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    print("SQL database created successfully.")


def get_session():
    logger.info("Creating SQL connection.")
    with Session(engine) as session:
        yield session
    logger.info("SQL connection closed.")
    
def close_connections():
    mongo_client.close()
    logger.info("Mongo DB connection closed.")

SessionDep = Annotated[Session, Depends(get_session)]