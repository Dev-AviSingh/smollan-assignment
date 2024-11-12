from fastapi import APIRouter, Query, HTTPException, Path
from typing import Annotated, Union, Optional

from models import *
from database import SessionDep, clients_collection
from sqlmodel import select

import json
from bson import ObjectId
from bson.errors import InvalidId
from logger import logger

client_router = APIRouter(prefix="/client", tags = ["client"])


@client_router.post("/", response_model=ClientPublic)
async def create_client(
    session:SessionDep,
    client:ClientCreate
):
    logger.debug(f"Client to create received : {Client}")
    
    db_client = ClientCreate.model_validate(client)

    mongodb_client = await clients_collection.insert_one(
        db_client.model_dump(by_alias = True, exclude=["id"])
    )
    logger.info("Client created in MongoDB")
    logger.debug(f"MongoDB client : {mongodb_client}")
    
    # Converting the metadata into string to store into the sql database.
    meta = json.dumps({
        "metadata":[x.model_dump() for x in db_client.client_metadata_dicts]
    })

    db_client = Client(**db_client.model_dump(), client_metadata = meta)
    logger.debug(f"SQL model : {db_client}")
    
    session.add(db_client)
    session.commit()
    session.refresh(db_client)
    
    logger.info(f"Model added to SQL database.")

    return db_client


@client_router.get("/clients", 
                 response_model=Union[list[ClientMongo], list[Client]], 
                 response_model_by_alias=True)
async def get_clients(
        session: SessionDep,
        metadata_key: Annotated[str, Query(description = "The key by which to search with.")] = None,
        metadata_value: Annotated[str, Query(description = "The value by which to search for.")] = None,
        offset: Annotated[int, Query(ge=0, description = "The number of clients you want to skip in the search.")] = 0,
        limit: Annotated[int, Query(le=100, description = "The max number of clients you want.")] = 100,
        use_sql_database: Annotated[bool, Query(description = "Set this to true, if you want to receive data from the sql database.")] = False
    ):
    

    if use_sql_database:
        logger.info("Using sql database. Listing clients.")
        clients = session.exec(
            select(Client).offset(offset).limit(limit)
        ).all()
        logger.info(f"Clients fetched : {len(clients)}")
    else:
        logger.info("Using MongoDB database.")
        if metadata_key and metadata_value:
            logger.info("Searching clients with metadata filters.")
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
            logger.info("Searching clients without metadata filters.")

            clients:list[ClientMongo] = await clients_collection.find().skip(offset).limit(limit).to_list(limit)
    
        for client in clients:
            client["id"] = client.pop("_id")
        
        logger.info("Client search complete.")
    
    logger.debug(f"Clients found : {clients}")
    return clients



@client_router.get("/{client_id}", 
                 response_model=ClientMongo | Client, 
                 response_model_by_alias=True
)
async def get_client(
        session:SessionDep,
        client_id:Annotated[str | int, Path(description="The id of the client. Make sure you use the correct id as per the database.")],
        use_sql_database: Annotated[bool, Query(title = "Set this to on, if you want to receive data from the sql database.")] = False
    ):
    client = None
    
    if use_sql_database:
        logger.info(f"Using SQL database. Searching for client id: {client_id}")
        try:
            client_id = int(client_id)
        except ValueError:
            logger.error("Non integer client id used for sql database.")
            raise HTTPException(status_code=406, detail = "If using the sql database, then the client_id has to be an integer")
        client:Client = session.get(Client, client_id)
        logger.info("Found client.")
        logger.debug(client)
    else:
        logger.info(f"Using MongoDB database. Searching for client id: {client_id}")
        try:
            cid = ObjectId(client_id)
        except InvalidId:
            logger.error("Non mongodb client id used for mongodb database.")
            raise HTTPException(status_code=406, detail = "If using the mongo db database, then the client_id has to be a mongodb id.")
        
        client:ClientMongo = await clients_collection.find_one({
            "_id": cid
        })
        logger.info("Found client.")
        logger.debug(client)
        
        client["id"] = client_id
    
    if not client:
        logger.info("Client not found.")
        raise HTTPException(status_code = 404, detail="Client not found.")

    return client

