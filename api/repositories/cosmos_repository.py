import os
import logging
from typing import Dict, Any, List

from azure.cosmos.partition_key import PartitionKey
from dotenv import load_dotenv
from azure.cosmos.aio import CosmosClient

from models.user import UserInDB
from utils.decorator import handle_cosmos_exception
from repositories.interface_repository import DatabaseInterface

load_dotenv()
logger = logging.getLogger("journal")

URL = os.getenv("COSMOS_ENDPOINT")
KEY = os.getenv("COSMOS_KEY")
ENTRY_DB = os.getenv("ENTRY_DB")
ENTRY_CONTAINER = os.getenv("ENTRY_CONTAINER")
USER_DB = os.getenv("USER_DB")
USER_CONTAINER = os.getenv("USER_CONTAINER")
if not (URL and KEY and ENTRY_DB and ENTRY_CONTAINER and USER_DB and USER_CONTAINER):
    logger.critical("Environment variables not loaded.")
    raise ValueError("Environment variables not loaded.")

class CosmosDB(DatabaseInterface):
    def __init__(self) -> None:
        self.client = CosmosClient(URL, {"masterKey": KEY})
        self.db = None
        self.container = None

    @handle_cosmos_exception("establish connection to database")
    async def __aenter__(self):
        self.db = await self.client.create_database_if_not_exists(ENTRY_DB)
        self.container = await self.db.create_container_if_not_exists(
            ENTRY_CONTAINER,
            partition_key=PartitionKey(path=["/user_id"])
        )
        logger.debug("Established connection to database.")
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.client.close()
    
    @handle_cosmos_exception(error_msg="create entry")
    async def create_entry(self, entry_data: Dict[str, Any]) -> None:
        """Creates a new journal entry"""
        await self.container.upsert_item(entry_data)
        
    @handle_cosmos_exception(error_msg="retrieve all entries")
    async def get_all_entries(self, user_id: str) -> List[Dict[str, Any]]:
        """Gets all entries for a specific user"""
        raw_entries = self.container.query_items(
            query='SELECT * FROM c WHERE c.user_id = @user_id',
            parameters=[{"name": "@user_id", "value": user_id}],
            partition_key=user_id
        )
        
        return [entry async for entry in raw_entries]
        
    @handle_cosmos_exception(error_msg="retrieve entry")
    async def get_entry(self, entry_id: str, user_id: str) -> Dict[str, Any]:
        """Gets an entry by id"""
        return await self.container.read_item(entry_id, partition_key=user_id)
    
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
    async def delete_entry(self, entry_id: str, user_id: str) -> None:
        """Deletes an entry"""
        await self.container.delete_item(entry_id, partition_key=user_id)


class UserDB(CosmosDB):
    def __init__(self):
        super().__init__()

    @handle_cosmos_exception("establish connection to user database")
    async def __aenter__(self):
        self.db = await self.client.create_database_if_not_exists(USER_DB)
        self.container = await self.db.create_container_if_not_exists(
            USER_CONTAINER,
            partition_key=PartitionKey(path=["/id"])
        )
        logger.debug("Established connection to user database.")
        return self
        
    @handle_cosmos_exception(error_msg="register user")
    async def register_user(self, user_data: UserInDB) -> None:
        await self.container.create_item(user_data.model_dump())
    
    async def get_user(self, username: str) -> List[Dict[str, Any]]:
        user = self.container.query_items(
            query='SELECT * FROM c WHERE c.username = @username', 
            parameters=[{"name": "@username", "value": username}]
        )
            
        return [user_detail async for user_detail in user]
