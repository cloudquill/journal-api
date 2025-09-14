import logging
from typing import Dict, List, Any
from fastapi import APIRouter, Depends

from services.entry_service import EntryService
from repositories.cosmos_repository import CosmosDB
from models.entry import InputEntry

logger = logging.getLogger("journal")
router = APIRouter(prefix="/entries")


async def get_entry_service():
    async with CosmosDB() as db:
        yield EntryService(db)


@router.post("/create", status_code=201)
async def create_entry(
        entry_data: InputEntry, 
        entry_service: EntryService = Depends(get_entry_service)
) -> Dict[str, str]:
    logger.info("Creating an entry")
    await entry_service.create_entry(entry_data)
    return {"detail": "Entry created successfully"}


@router.get("/all")
async def get_all_entries(
        entry_service: EntryService = Depends(get_entry_service)
) -> List[Dict[str, Any]]:
    logger.info("Retrieving all entries")
    return await entry_service.get_all_entries()


@router.get("/{entry_id}")
async def get_entry(
        entry_id: str, 
        entry_service: EntryService = Depends(get_entry_service)
) -> Dict[str, Any]:
    logger.info("Retrieving entry with ID: %s", entry_id)
    return await entry_service.get_entry(entry_id)


@router.patch("/update/{entry_id}")
async def update_entry(
        entry_id: str, 
        updated_data: InputEntry, 
        entry_service: EntryService = Depends(get_entry_service)
) -> Dict[str, str]:
    logger.info("Updating entry with ID %s", entry_id)
    await entry_service.update_entry(entry_id, updated_data)
    return {"detail": "Entry updated successfully"}


@router.delete("/delete/{entry_id}")
async def delete_entry(
        entry_id: str, 
        entry_service: EntryService = Depends(get_entry_service)
) -> Dict[str, str]:
    logger.info("Deleting entry with ID %s", entry_id)
    await entry_service.delete_entry(entry_id)
    return {"detail": "Entry deleted successfully"}