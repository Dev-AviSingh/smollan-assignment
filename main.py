from fastapi import FastAPI
from routers.user_routes import client_router
from database import create_db_and_tables, close_connections # Importing this will create all the models in memory before the app starts.
from logger import logger

tags_metadata = [
    {
        "name":"client",
        "description":"Operations with client. Creating and fetching clients. For Client model data, refer to the model Client."
    }
]

logger.info("Creating app.")
app = FastAPI(
    title="Client Database",
    summary="A simple client database that stores client data in a MySQL Server, and fetches the client data from MongoDB Server.",
    debug=True,
    openapi_tags=tags_metadata
)
logger.info("Created app")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.on_event("shutdown")
def on_shutdown():
    close_connections()
    logger.info("App closing down.")

app.include_router(client_router)
logger.info("Routers included.")
