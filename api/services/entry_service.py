from functools import wraps
import logging
from typing import Any, Dict, List
from datetime import datetime

from azure.core.exceptions import ServiceRequestError
from azure.cosmos.exceptions import (
    CosmosHttpResponseError, 
    CosmosResourceNotFoundError
)

from models.entry import InputEntry, EnrichedEntry
from repositories.cosmos_repository import CosmosDB
from exceptions import EntryNotFoundError, JournalError

logger = logging.getLogger("journal")


class EntryService:
    def __init__(self, db: CosmosDB):
        self.db = db
        logger.debug("EntryService initialized with CosmosDB.")

    def log_service_call(success_msg: str, error_msg: str):
        """
        Logs results and errors of methods in EntryService.
        """
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                log_extra = kwargs.get("entry_id") or kwargs.get("entry_data")
                if log_extra is None and len(args) > 1:
                    log_extra = args[1]

                try:
                    result = await func(*args, **kwargs)

                    if log_extra:
                        logger.info("Successfully %s: %s", success_msg, log_extra)
                    else:
                        logger.info("Successfully %s", success_msg)
                    
                    return result
                except (CosmosHttpResponseError, CosmosResourceNotFoundError) as e:
                    if e.status_code == 404:
                        logger.warning("Couldn't %s: No entry with ID %s", error_msg, log_extra)
                        raise EntryNotFoundError(f"Entry {log_extra} not found.") from e
                    else:
                        logger.exception(
                            "Couldnt %s: An unexpected error occurred. Details: %s", 
                            error_msg, 
                            str(e)
                        )
                        raise JournalError("An unexpected error occurred") from e
                except ServiceRequestError as e:
                    logger.exception(
                        "Couldnt %s: The connection to the database was closed. Details: %s", 
                        error_msg,
                        str(e)
                    )
                    raise JournalError("An unexpected error occurred") from e

            return wrapper
        return decorator

    @log_service_call("created entry", "create entry")
    async def create_entry(self, entry_data: InputEntry) -> None:
        enriched_entry = EnrichedEntry(**entry_data.model_dump())
        await self.db.create_entry(enriched_entry.model_dump())
    
    @log_service_call("retrieved all entries.", "retrieve all entries")
    async def get_all_entries(self) -> List[Dict[str, Any]]:
        raw_entries = await self.db.get_all_entries()
        return [
            EnrichedEntry(**entry).model_dump(exclude=["created_at", "updated_at"])
            for entry in raw_entries
        ]
    
    @log_service_call("retrieved entry", "retrieve entry")
    async def get_entry(self, entry_id: str) -> Dict[str, Any]:
        entry = await self.db.get_entry(entry_id)
        return EnrichedEntry(**entry).model_dump()

    @log_service_call("updated your entry", "update entry")
    async def update_entry(self, entry_id: str, updated_data: InputEntry) -> None:
        entry = await self.db.get_entry(entry_id)
        updated_data_dict = updated_data.model_dump()
        
        for field in ["work", "struggle", "intention"]:
            if updated_data_dict[field].strip():
                entry[field] = updated_data_dict[field]
        
        entry["updated_at"] = datetime.now().isoformat("#", "seconds")
        await self.db.update_entry(entry_id, entry)
    
    @log_service_call("deleted entry", "delete entry")
    async def delete_entry(self, entry_id: str) -> None:
        await self.db.delete_entry(entry_id)