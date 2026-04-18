from typing import Optional

from pydantic import BaseModel, Field

from TaoxinAI.schemas.common import Message


class CaseInput(BaseModel):
    messages: list[Message] = Field(default_factory=list)
    extracted_info: dict = Field(default_factory=dict)
    case_type_hint: Optional[str] = "taoxin"
