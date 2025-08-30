from typing import Dict, List, Any
from fastapi import APIRouter, Depends, HTTPException

from services.entry_service import EntryService
from repositories.cosmos_repository import cosmosDB
from models.entry import inputEntry

router = APIRouter(prefix="/entries")

def get_entry_service():
    db = cosmosDB()
    yield EntryService(db)

@router.post("/create", status_code=201)
def create_entry(
    entry_data: inputEntry, 
    entry_service: EntryService = Depends(get_entry_service)
) -> Dict[str, str]:
    try:
        entry_service.create_entry(entry_data)
    except HTTPException as e:
            if e.status_code == 409:
                raise HTTPException(
                    status_code=409, detail="You already have an entry for today."
                )
            raise e
    return {"detail": "Entry created successfully"}

@router.get("/all")
def get_all_entries(
    entry_service: EntryService = Depends(get_entry_service)
) -> List[Dict[str, Any]]:
    try:
        return entry_service.get_all_entries()
    except HTTPException:
        raise HTTPException(detail="Error getting your journal.")

@router.get("/{entry_id}")
def get_entry(
    entry_id: str, 
    entry_service: EntryService = Depends(get_entry_service)
) -> Dict[str, Any]:
    try:
        return entry_service.get_entry(entry_id)
    except HTTPException:
        raise HTTPException(status_code=404, detail=f"Entry {entry_id} not found")
 
@router.patch("/update/{entry_id}")
def update_entry(
    entry_id: str, 
    updated_data: inputEntry, 
    entry_service: EntryService = Depends(get_entry_service)
) -> Dict[str, str]:
    try:
        entry_service.update_entry(entry_id, updated_data)
    except HTTPException:
        raise HTTPException(status_code=404,detail=f"Entry {entry_id} not found")
    return {"detail": "Entry updated successfully"}

@router.delete("/delete/{entry_id}")
def delete_entry(
    entry_id: str, 
    entry_service: EntryService = Depends(get_entry_service)
) -> Dict[str, str]:
    try:
        entry_service.delete_entry(entry_id)
    except HTTPException:
        raise HTTPException(status_code=404,detail=f"Entry {entry_id} not found")
    return {"detail": "Entry deleted successfully"}