from sqlmodel import SQLModel, Field, Column
from pydantic import EmailStr, BaseModel
from typing import Optional, Annotated
from pydantic.functional_validators import BeforeValidator

# For convertin the mongodb id to str
PyObjectId = Annotated[str, BeforeValidator(str)]

class MetadataDict(BaseModel):
    key:str
    value:str

class ClientBase(SQLModel):
    company_id:int = Field(default = None, index = True)
    client_name:str = Field(default= None)
    client_email:EmailStr = Field(unique=True, default=None)


class Client(ClientBase, table = True):
    __tablename__ = "clients"
    id:int = Field(default = None, primary_key = True)
    client_metadata:Optional[str] = Field(alias = "metadata", default="[]")

class ClientPublic(ClientBase):
    id:int

class ClientMongo(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    company_id:int = Field(default = None, index = True)
    client_name:str = Field(default= None)
    client_email:EmailStr = Field(unique=True, default=None)
    client_metadata_dicts:Optional[list[MetadataDict]] = Field(alias = "metadata", default = [])


class ClientCreate(ClientBase):
    client_metadata_dicts:Optional[list[MetadataDict]] = Field(alias = "metadata", default  = [])
