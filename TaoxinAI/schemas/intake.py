from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from TaoxinAI.schemas.common import Message


class CaseInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    messages: list[Message] = Field(default_factory=list)
    extracted_info: dict[str, Any] = Field(default_factory=dict)
    case_type_hint: Optional[str] = "taoxin"
