from fastapi import APIRouter, Query, HTTPException
from typing import Annotated, Union, Optional

from models import *
from database import SessionDep, clients_collection
from sqlmodel import select
import json
from bson import ObjectId

client_router = APIRouter(prefix="/client", tags = ["client"])


@client_router.post("/", response_model=ClientPublic)
async def create_client(
    session:SessionDep,
    client:ClientCreate
):
    print(client)
    
    db_client = ClientCreate.model_validate(client)
    mongodb_client = await clients_collection.insert_one(
        db_client.model_dump(by_alias = True, exclude=["id"])
    )
    
    print(db_client)
    
    # Converting the metadata into string to store into the sql database.
    meta = json.dumps({
        "metadata":[x.model_dump() for x in db_client.client_metadata_dicts]
    })
    db_client = Client(**db_client.model_dump(), client_metadata = meta)
    print(db_client.metadata)
    
    session.add(db_client)
    session.commit()
    session.refresh(db_client)
    
    print(db_client)

    return db_client


@client_router.get("/clients", 
                 response_model=Union[list[ClientMongo], list[Client]], 
                 response_model_by_alias=True)
async def get_clients(
        session: SessionDep,
        metadata_key: Optional[str] = None,
        metadata_value: Optional[str] = None,
        offset: Annotated[int, Query(ge=0, title = "The number of clients you want to skip in the search.")] = 0,
        limit: Annotated[int, Query(le=100, title = "The max number of clients you want.")] = 100,
        use_sql_database: Annotated[bool, Query(title = "Set this to on, if you want to receive data from the sql database.")] = False
    ):
    

    if use_sql_database:
        clients = session.exec(
            select(Client).offset(offset).limit(limit)
        ).all()
    else:
        if metadata_key and metadata_value:
            clients:list[ClientMongo] = await clients_collection.find(
                {
                    "client_metadata_dicts":{
                        "$elemMatch":{
                            "key": metadata_key,
                            "value": metadata_value
                        }
                    }
                }
            ).skip(offset).limit(limit).to_list(limit)
        else:
            clients:list[ClientMongo] = await clients_collection.find().skip(offset).limit(limit).to_list(limit)
    
        for client in clients:
            client["id"] = client.pop("_id")
    print(clients)
    return clients



@client_router.get("/{client_id}", 
                 response_model=Client | ClientMongo, 
                 response_model_by_alias=True
)
async def get_client(
        session:SessionDep,
        client_id:Annotated[str, "The id of the client"],
        use_sql_database: Annotated[bool, Query(title = "Set this to on, if you want to receive data from the sql database.")] = False
    ):
    client:Client = None
    
    if use_sql_database:
        client:Client = session.get(Client, client_id)
    else:
        client:Client = await clients_collection.find_one({
            "_id": ObjectId(client_id)
        })

        client["id"] = client_id
    
    if not client:
        raise HTTPException(status_code = 404, detail="Client not found.")

    return client

