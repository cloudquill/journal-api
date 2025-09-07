from typing import Any, Dict, List
from datetime import datetime

from models.entry import inputEntry, enrichedEntry
from repositories.cosmos_repository import cosmosDB

class EntryService:
    def __init__(self, db: cosmosDB):
        self.db = db

    async def create_entry(self, entry_data: inputEntry) -> None:
        enriched_entry = enrichedEntry(**entry_data.model_dump())
        await self.db.create_entry(enriched_entry.model_dump())
    
    async def get_all_entries(self) -> List[Dict[str, Any]]:
        raw_entries = await self.db.get_all_entries()
        
        return [
            enrichedEntry(**entry).model_dump(exclude=["created_at", "updated_at"])
            for entry in raw_entries
        ]
    
    async def get_entry(self, entry_id: str) -> Dict[str, Any]:
        entry = await self.db.get_entry(entry_id)
        return enrichedEntry(**entry).model_dump()

    async def update_entry(self, entry_id: str, updated_data: inputEntry) -> None:
        entry = await self.db.get_entry(entry_id)
        updated_data_dict = updated_data.model_dump()
        
        for field in ["work", "struggle", "intention"]:
            if updated_data_dict[field].strip():
                entry[field] = updated_data_dict[field]
        
        entry["updated_at"] = datetime.now().isoformat("#", "seconds")
        await self.db.update_entry(entry_id, entry)
    
    async def delete_entry(self, entry_id: str) -> None:
        await self.db.delete_entry(entry_id)