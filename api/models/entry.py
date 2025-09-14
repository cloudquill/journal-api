import uuid
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class InputEntry(BaseModel):
    work: str = Field(
        ...,
        max_length=256,
        description="What do you want to do today?")
    struggle: str = Field(
        ...,
        max_length= 256,
        description= "What did you struggle with?"
    )
    intention: str = Field(
        ...,
        max_length= 256,
        description= "How do you plan to solve your struggle?"
    )

class EnrichedEntry(InputEntry):
    id: str = Field(
        default_factory= lambda: str(uuid.uuid4()),
        description="Unique identifier for the entry (UUID)."
    )
    created_at: Optional[str] = Field(
        default_factory= lambda: datetime.now().isoformat("#", "seconds"),
        description= "Date this entry was created."
    )
    updated_at: Optional[str] = Field(
        default= "None",
        description="Date this entry was last modified."
    )