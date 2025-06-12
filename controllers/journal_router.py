import logging
from typing import List
from datetime import datetime, timezone

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Request, HTTPException
from azure.cosmos import exceptions
from azure.core.exceptions import ServiceRequestError, ResourceNotFoundError, ResourceExistsError

from models.entry import (
    EntryCreate, 
    EntryFull, 
    EntryUpdate
)

router = APIRouter()
logger = logging.getLogger("journal_api")

@router.post("/create")
async def create_entry(request: Request, entry_data: EntryCreate):
    full_entry = EntryFull(**jsonable_encoder(entry_data))
    item_to_create = jsonable_encoder(full_entry)
    
    try:
        await request.app.entry_container.create_item(item_to_create)
    except ResourceExistsError as e:
        if e.status_code == 409:
            raise HTTPException(
                status_code=409,
                detail=f"Entry {full_entry.id} already exists."
            )
        raise e
    return JSONResponse(content=item_to_create, status_code=201)

@router.get("/listall")
async def get_entries(request: Request):
    all_entries = request.app.entry_container.read_all_items()
    entry_summaries = [
        jsonable_encoder(entry, include=["id", "intention", "work", "struggle"]) 
        async for entry in all_entries
    ]

    return JSONResponse(content=entry_summaries, status_code=200)

@router.get("/{entry_id}")
async def get_an_entry(request: Request, entry_id: str):
    try:
        item = await request.app.entry_container.read_item(item=entry_id, partition_key=entry_id)
    except ResourceNotFoundError:
        raise HTTPException(
            status_code=404,
            message=f"Entry {entry_id} does not exist."
        )
    
    item_to_display = jsonable_encoder(EntryFull(**item))
    return JSONResponse(content=item_to_display, status_code=200)

@router.put("/update/{entry_id}")
async def update_entry(
    entry_id: str, 
    update_data: EntryUpdate,
    request: Request
):
    try:
        existing_item = await request.app.entry_container.read_item(entry_id, partition_key=entry_id) 
    except ResourceNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=f"Entry {entry_id} doesn't exist."
        )

    update_data_dict = jsonable_encoder(update_data, exclude_unset=True)

    for field_name, field_value in update_data_dict.items():
        if field_name not in ["id", "created_at"]:
            existing_item[field_name] = field_value
    
    existing_item["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    try:
        updated_item = await request.app.entry_container.replace_item(entry_id, existing_item)
    except servi as e:
        if e.status_code == 500:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to update entry in Cosmos DB."
            )
        raise e
    
    entry_to_display = jsonable_encoder(EntryFull(**updated_item))
    return JSONResponse(content=entry_to_display, status_code=200)

@router.delete("/delete/{entry_id}")
async def delete_entry(request: Request, entry_id: str) -> str:
    try:
        await request.app.entry_container.delete_item(item=entry_id, partition_key=entry_id)
    except HTTPException as e:
        if e.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail=f"Entry {entry_id} doesn't exist."
            )
        raise e

    return f"Entry {entry_id} has been deleted."