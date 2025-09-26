import logging
from typing import Any, Dict, List
from datetime import datetime

from models.entry import InputEntry, EnrichedEntry
from repositories.cosmos_repository import CosmosDB
from utils.decorator import log_service_call

logger = logging.getLogger("journal")


class EntryService:
    def __init__(self, db: CosmosDB):
        self.db = db
        logger.debug("EntryService initialized with CosmosDB.")

    @log_service_call("create entry")
    async def create_entry(self, entry_data: InputEntry, user_id: str) -> None:
        enriched_entry = EnrichedEntry(**entry_data.model_dump())
        enriched_entry_dict = enriched_entry.model_dump()
        enriched_entry_dict['user_id'] = user_id
        
        await self.db.create_entry(enriched_entry_dict)
        logger.info(
            "Successfully created entry: %s for %s", 
            enriched_entry_dict, 
            user_id
        )
    
    @log_service_call("retrieve all entries")
    async def get_all_entries(self, user_id: str) -> List[Dict[str, Any]]:
        raw_entries = await self.db.get_all_entries(user_id)
        logger.info("Successfully retrieved all entries for %s", user_id)

        return [
            EnrichedEntry(**entry).model_dump(exclude=["created_at", "updated_at"])
            for entry in raw_entries
        ]
    
    @log_service_call("retrieve entry")
    async def get_entry(self, entry_id: str, user_id: str) -> Dict[str, Any]:
        entry = dict(await self.db.get_entry(entry_id, user_id))
        logger.info("Successfully retrieved entry %s for %s", entry_id, user_id)
        return EnrichedEntry(**entry).model_dump()

    @log_service_call("update entry")
    async def update_entry(
        self, 
        entry_id: str, 
        updated_data: InputEntry, 
        user_id: str
    ) -> None:
        entry = await self.db.get_entry(entry_id, user_id)
        updated_data_dict = updated_data.model_dump()
        
        for field in ["work", "struggle", "intention"]:
            if updated_data_dict[field].strip():
                entry[field] = updated_data_dict[field]
        
        entry["updated_at"] = datetime.now().isoformat("#", "seconds")
        await self.db.update_entry(entry_id, entry)
        logger.info("Successfully updated entry %s for %s", entry_id, user_id)
    
    @log_service_call("delete entry")
    async def delete_entry(self, entry_id: str, user_id: str) -> None:
        await self.db.delete_entry(entry_id, user_id)
        logger.info("Successfully deleted entry %s for %s", entry_id, user_id)