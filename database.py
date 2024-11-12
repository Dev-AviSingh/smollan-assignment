from sqlmodel import Field, Session, SQLModel, create_engine
from typing import Annotated
from fastapi import Depends
from models import *
from config import *

from bson import ObjectId
import motor.motor_asyncio
from pymongo import ReturnDocument



engine = create_engine(SQL_URI)


mongo_client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI)
mongo_db = mongo_client.smollan
clients_collection = mongo_db.get_collection("clients")

def create_db_and_tables():
    print("Created database")
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
    
SessionDep = Annotated[Session, Depends(get_session)]