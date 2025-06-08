from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
from uuid import uuid4

class EntryCreate(BaseModel):
    intention: str = Field(
        ...,
        max_length=256,
        description="What will you study/work on tomorrow?"
    )
    work: str = Field(
        ...,
        max_length=256,
        description="What did you work on today?"
    )
    struggle: str = Field(
        ...,
        max_length=256,
        description="What’s one thing you struggled with today?"
    )

class EntryResponse(EntryCreate):
    id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique identifier for the entry (UUID)."
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when the entry was created."
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when the entry was last updated."
    )

class EntrySummary(BaseModel):    
    id: str = Field(
        description="Unique identifier for the entry (UUID)."
    )
    intention: str = Field(
        description="What will you study/work on tomorrow?"
    )

class EntryUpdate(BaseModel):
    intention: Optional[str] = Field(
        default=None,
        max_length=256,
        description="What will you study/work on tomorrow?"
    )
    work: Optional[str] = Field(
        default=None,
        max_length=256,
        description="What did you work on today?"
    )
    struggle: Optional[str] = Field(
        default=None,
        max_length=256,
        description="What’s one thing you struggled with today?"
    )