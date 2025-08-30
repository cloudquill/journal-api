from typing import Any, Dict, List
from datetime import datetime

from models.entry import inputEntry, enrichedEntry
from repositories.cosmos_repository import cosmosDB

class EntryService:
    def __init__(self, db: cosmosDB):
        self.db = db

    def create_entry(self, entry_data: inputEntry) -> None:
        enriched_entry = enrichedEntry(**entry_data.model_dump())
        self.db.create_entry(enriched_entry.model_dump())
    
    def get_all_entries(self) -> List[Dict[str, Any]]:
        raw_entries = self.db.get_all_entries()
        journal = []

        for entry in raw_entries:
            enriched_entry = enrichedEntry(**entry)
            journal.append(enriched_entry.model_dump(exclude=["created_at", "updated_at"]))
        
        return journal
    
    def get_entry(self, entry_id: str) -> Dict[str, Any]:
        entry = self.db.get_entry(entry_id)
        enriched_entry = enrichedEntry(**entry)
        return enriched_entry.model_dump()

    def update_entry(self, entry_id: str, updated_data: inputEntry) -> None:
        entry = self.db.get_entry(entry_id)
        updated_data_dict = updated_data.model_dump()
        
        for i in ["work", "struggle", "intention"]:
            if updated_data_dict[i].strip():
                entry[i] = updated_data_dict[i]
        
        entry["updated_at"] = datetime.now().isoformat("#", "seconds")
        self.db.update_entry(entry_id, entry)
    
    def delete_entry(self, entry_id: str) -> None:
        self.db.delete_entry(entry_id)