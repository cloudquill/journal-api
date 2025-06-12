import logging
from dotenv import dotenv_values

from fastapi import FastAPI, status
from azure.core.exceptions import ServiceRequestError, ResourceNotFoundError
from azure.cosmos.aio import CosmosClient
from azure.cosmos import PartitionKey
from fastapi.exceptions import HTTPException

from controllers.journal_router import router as entry_router

logger = logging.getLogger("journal_api")

formatter = logging.Formatter('%(levelname)s - %(asctime)s - %(message)s')

handler = logging.FileHandler("app.log")
handler.setFormatter(formatter)
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)

logger.setLevel(logging.INFO)

config = dotenv_values(".env")
app = FastAPI()
db_name = "journal"
container_name = "entries"

app.include_router(entry_router, tags=["entries"], prefix="/entries")

@app.on_event("startup")
async def startup_db_client():
    app.cosmos_client = CosmosClient(config["COSMOS_DB_URL"], credential=config["COSMOS_DB_KEY"])
    
    try:
        await get_or_create_db(db_name)
        await get_or_create_container(container_name)
    except ServiceRequestError as e:
        logger.critical(f"Couldn't reach Cosmos DB account: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Couldn't reach Cosmos DB."
        )

async def get_or_create_db(db_name):
    try:
        app.database  = app.cosmos_client.get_database_client(db_name)
        return await app.database.read()
    except ResourceNotFoundError:
        logger.info("Creating database")
        return await app.cosmos_client.create_database(db_name)
     
async def get_or_create_container(container_name):
    try:        
        app.entry_container = app.database.get_container_client(container_name)
        return await app.entry_container.read()   
    except ResourceNotFoundError:
        logger.info("Creating container with id as partition key")
        return await app.database.create_container(id=container_name, partition_key=PartitionKey(path="/id"))

@app.get("/")
def home():
    return("Hello, Journal API!!")