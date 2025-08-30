import os
from dotenv import load_dotenv
from typing import Dict, Any, List

from azure.cosmos import CosmosClient

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

    def create_entry(self, entry_data: Dict[str, Any]) -> None:
        """Creates a new journal entry"""
        self.container.upsert_item(entry_data)

    def get_all_entries(self) -> List[Dict[str, Any]]:
        """Gets all entries from db"""
        return list(self.container.read_all_items())
    
    def get_entry(self, entry_id: str) -> Dict[str, Any]:
        """Gets an entry by id"""
        return dict(self.container.read_item(entry_id, partition_key=entry_id))
    
    def update_entry(self, entry_id: str, updated_data: Dict[str, Any]) -> None:
        """Updates an entry"""
        self.container.replace_item(entry_id, updated_data)

    def delete_all_entries(self) -> None:
        pass
    
    def delete_entry(self, entry_id: str) -> None:
        """Deletes an entry"""
        self.container.delete_item(entry_id, partition_key=entry_id)