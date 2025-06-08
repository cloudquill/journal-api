from typing import List
from datetime import datetime, timezone

from fastapi import FastAPI, status, HTTPException

from models.entry import (
    EntryCreate, 
    EntryResponse, 
    EntrySummary, 
    EntryUpdate
)

entries = {}

app = FastAPI()

@app.get("/")
def home():
    return("Hello, Journal API!!")

@app.post("/entries/", status_code=status.HTTP_201_CREATED)
def create_entry(entry_data: EntryCreate) -> EntryResponse:
    full_entry = EntryResponse(**entry_data.model_dump())
    entries[full_entry.id] = full_entry
    return full_entry

@app.get("/entries/")
def get_entries() -> List[EntrySummary]:
    entry_summaries = [
        EntrySummary(id=key, intention=entries[key].intention) 
        for key in entries
    ]

    return entry_summaries

@app.get("/entries/{entry_id}", response_model=EntryResponse)
def get_an_entry(entry_id: str):
    if entry_id in entries:
        return entries[entry_id]
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Journal entry with id {entry_id} not found"
        )

@app.put("/entries/{entry_id}", response_model=EntryResponse)
def update_entry(entry_id: str, update_data: EntryUpdate):
    if entry_id not in entries:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Journal entry with id {entry_id} not found"
        )

    existing_entry = entries[entry_id]

    # Converts to a dictionary with empty vars excluded
    update_data_dict = update_data.model_dump(exclude_unset=True)

    for field_name, field_value in update_data_dict.items():
        # Updates existing variables to new values
        if field_name not in ["id", "created_at"]:
            setattr(existing_entry, field_name, field_value)
    
    existing_entry.updated_at = datetime.now(timezone.utc)
    
    return existing_entry

@app.delete("/entries/{entry_id}")
def delete_entry(entry_id: str) -> str:
    if entry_id not in entries:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Journal entry with id {entry_id} not found"
        )

    del entries[entry_id]
    return f"Journal entry with id {entry_id} has been deleted."