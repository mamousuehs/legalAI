from typing import Literal

from pydantic import BaseModel, Field


class RetrievedAuthority(BaseModel):
    source_type: Literal["norm", "case", "template"]
    source_id: str
    title: str
    snippet: str
    score: float
    metadata: dict = Field(default_factory=dict)

