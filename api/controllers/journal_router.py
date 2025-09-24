import logging
from typing import Annotated, Dict, List, Any

from fastapi import APIRouter, Depends

from services.entry_service import EntryService
from repositories.cosmos_repository import CosmosDB
from models.entry import InputEntry
from controllers.login_router import oauth2_scheme, read_users_me

logger = logging.getLogger("journal")
router = APIRouter(prefix="/users/me/entries", dependencies=[Depends(oauth2_scheme)])


async def get_entry_service():
    async with CosmosDB() as db:
        yield EntryService(db)


@router.post("/create", status_code=201)
async def create_entry(
        entry_data: InputEntry,
        current_user_id: Annotated[str, Depends(read_users_me)],
        entry_service: Annotated[EntryService, Depends(get_entry_service)]
) -> Dict[str, str]:
    logger.info("Creating an entry")
    await entry_service.create_entry(entry_data, current_user_id)
    return {"detail": "Entry created successfully"}


@router.get("/all")
async def get_all_entries(
        current_user_id: Annotated[str, Depends(read_users_me)],
        entry_service: Annotated[EntryService, Depends(get_entry_service)]
) -> List[Dict[str, Any]]:
    logger.info("Retrieving all entries")
    return await entry_service.get_all_entries(current_user_id)


@router.get("/{entry_id}")
async def get_entry(
        entry_id: str, 
        current_user_id: Annotated[str, Depends(read_users_me)],
        entry_service: Annotated[EntryService, Depends(get_entry_service)]
) -> Dict[str, Any]:
    logger.info("Retrieving entry with ID: %s", entry_id)
    return await entry_service.get_entry(entry_id, current_user_id)


@router.patch("/update/{entry_id}")
async def update_entry(
        entry_id: str, 
        updated_data: InputEntry, 
        current_user_id: Annotated[str, Depends(read_users_me)],
        entry_service: Annotated[EntryService, Depends(get_entry_service)]
) -> Dict[str, str]:
    logger.info("Updating entry with ID %s", entry_id)
    await entry_service.update_entry(entry_id, updated_data, current_user_id)
    return {"detail": "Entry updated successfully"}


@router.delete("/delete/{entry_id}")
async def delete_entry(
        entry_id: str, 
        current_user_id: Annotated[str, Depends(read_users_me)],
        entry_service: Annotated[EntryService, Depends(get_entry_service)]
) -> Dict[str, str]:
    logger.info("Deleting entry with ID %s", entry_id)
    await entry_service.delete_entry(entry_id, current_user_id)
    return {"detail": "Entry deleted successfully"}