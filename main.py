from fastapi import FastAPI
from routers.user_routes import client_router
from database import create_db_and_tables # Importing this will create all the models in memory before the app starts.

app = FastAPI(
    title="Client Database",
    summary="A simple client database that stores client data in a MySQL Server, and fetches the client data from MongoDB Server.",
    debug=True,
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()



app.include_router(client_router)
