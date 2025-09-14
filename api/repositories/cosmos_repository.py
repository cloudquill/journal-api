import os
import logging
from dotenv import load_dotenv
from typing import Dict, Any, List
from functools import wraps

from azure.cosmos.aio import CosmosClient
from azure.core.exceptions import ServiceRequestError
from azure.cosmos.exceptions import CosmosHttpResponseError, CosmosResourceNotFoundError

from repositories.interface_repository import DatabaseInterface

load_dotenv()
logger = logging.getLogger("journal")

URL = os.getenv("COSMOS_ENDPOINT")
KEY = os.getenv("COSMOS_KEY")
DB_NAME = os.getenv("DATABASE_NAME")
CONTAINER_NAME = os.getenv("CONTAINER_NAME")
if not (URL and KEY and DB_NAME and CONTAINER_NAME):
    logger.critical("Environment variables not loaded.")
    raise ValueError("Environment variables not loaded.")

class CosmosDB(DatabaseInterface):
    def __init__(self) -> None:
        self.client = CosmosClient(URL, {"masterKey": KEY})
        self.db = self.client.get_database_client(DB_NAME)
        self.container = self.db.get_container_client(CONTAINER_NAME)
        logger.debug("Established connection to Database.")

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.client.close()
    
    def handle_cosmos_exception(error_msg: str):
        """
        Handles Cosmos DB exceptions with custom messages and logging.
        """
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                try:
                    return await func(*args, **kwargs)
                except (CosmosHttpResponseError, CosmosResourceNotFoundError, ServiceRequestError) as e:
                    log_extra = (args[1] if len(args) > 1 else None)

                    if log_extra:
                        logger.exception(
                            "Couldn't %s: An unexpected error occurred: %s. Details: %s", 
                            error_msg, 
                            log_extra, 
                            str(e)
                        )
                    else:
                        logger.exception(
                            "Couldn't %s: An unexpected error occurred. Details: %s", 
                            error_msg, 
                            str(e)
                        )
                    raise e
            return wrapper
        return decorator
    
    @handle_cosmos_exception(error_msg="create entry")
    async def create_entry(self, entry_data: Dict[str, Any]) -> None:
        """Creates a new journal entry"""
        await self.container.upsert_item(entry_data)
        
    @handle_cosmos_exception(error_msg="retrieve all entries")
    async def get_all_entries(self) -> List[Dict[str, Any]]:
        """Gets all entries from db"""
        raw_entries = self.container.read_all_items()
        return [entry async for entry in raw_entries]
        
    @handle_cosmos_exception(error_msg="retrieve entry")
    async def get_entry(self, entry_id: str) -> Dict[str, Any]:
        """Gets an entry by id"""
        return dict(await self.container.read_item(entry_id, partition_key=entry_id))
    
    @handle_cosmos_exception(error_msg="update entry")
    async def update_entry(
            self, 
            entry_id: str, 
            updated_data: Dict[str, Any]
    ) -> None:
        """Updates an entry"""
        await self.container.replace_item(entry_id, updated_data)

    async def delete_all_entries(self) -> None:
        pass
    
    @handle_cosmos_exception(error_msg="delete entry")
    async def delete_entry(self, entry_id: str) -> None:
        """Deletes an entry"""
        await self.container.delete_item(entry_id, partition_key=entry_id)