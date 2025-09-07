import os
from dotenv import load_dotenv
from typing import Dict, Any, List

from azure.cosmos.aio import CosmosClient

from repositories.interface_repository import DatabaseInterface

load_dotenv()

URL = os.getenv("COSMOS_ENDPOINT")
KEY = os.getenv("COSMOS_KEY")
DB_NAME = os.getenv("DATABASE_NAME")
CONTAINER_NAME = os.getenv("CONTAINER_NAME")
if not (URL or KEY or DB_NAME or CONTAINER_NAME):
    raise ValueError("Environment variables not loaded.")

class cosmosDB(DatabaseInterface):
    def __init__(self) -> None:
        self.client = CosmosClient(URL, {"masterKey": KEY})
        self.db = self.client.get_database_client(DB_NAME)
        self.container = self.db.get_container_client(CONTAINER_NAME)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.client.close()
    
    async def create_entry(self, entry_data: Dict[str, Any]) -> None:
        """Creates a new journal entry"""
        await self.container.upsert_item(entry_data)

    async def get_all_entries(self) -> List[Dict[str, Any]]:
        """Gets all entries from db"""
        raw_entries = self.container.read_all_items()
        return [entry async for entry in raw_entries]

    
    async def get_entry(self, entry_id: str) -> Dict[str, Any]:
        """Gets an entry by id"""
        return dict(await self.container.read_item(entry_id, partition_key=entry_id))
    
    async def update_entry(self, entry_id: str, updated_data: Dict[str, Any]) -> None:
        """Updates an entry"""
        await self.container.replace_item(entry_id, updated_data)

    async def delete_all_entries(self) -> None:
        pass
    
    async def delete_entry(self, entry_id: str) -> None:
        """Deletes an entry"""
        await self.container.delete_item(entry_id, partition_key=entry_id)