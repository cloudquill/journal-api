import inspect
from functools import wraps
import logging
from typing import Any, Dict, List
from datetime import datetime

from azure.cosmos.exceptions import (
    CosmosHttpResponseError, 
    CosmosResourceNotFoundError
)

from models.entry import InputEntry, EnrichedEntry
from repositories.cosmos_repository import CosmosDB
from exceptions import EntryNotFoundError

logger = logging.getLogger("journal")


class EntryService:
    def __init__(self, db: CosmosDB):
        self.db = db
        logger.debug("EntryService initialized with CosmosDB.")

    def log_service_call(error_msg: str):
        """
        Logs results and errors of methods in EntryService.
        """
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                log_extra = {}
                
                # Trying to remove guesswork by binding argument names to their values
                # and accessing them.
                sig = inspect.signature(func)

                # Bind the arguments to the parameters
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()

                log_extra = {
                    name: value
                    for name, value in bound_args.arguments.items()
                    if name != 'self'
                }
                
                try:
                    return await func(*args, **kwargs)
                except (CosmosHttpResponseError, CosmosResourceNotFoundError) as e:
                    if e.status_code == 404:
                        logger.warning("Couldn't %s. Details: %s", error_msg, log_extra)
                        raise EntryNotFoundError(f"Entry not found.") from e
                    else:
                        logger.exception(
                            "Couldnt %s: %s", 
                            error_msg, 
                            str(e)
                        )
                        raise e
            return wrapper
        return decorator

    @log_service_call("create entry")
    async def create_entry(self, entry_data: InputEntry, user_id: str) -> None:
        enriched_entry = EnrichedEntry(**entry_data.model_dump())
        enriched_entry_dict = enriched_entry.model_dump()
        enriched_entry_dict['username'] = user_id
        
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
    async def update_entry(self, entry_id: str, updated_data: InputEntry, user_id: str) -> None:
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