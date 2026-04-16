from typing import Literal

from pydantic import BaseModel, Field


class ElementMatch(BaseModel):
    issue_code: str
    element_name: str
    status: Literal["satisfied", "partial", "insufficient", "not_satisfied"]
    supporting_facts: list[str] = Field(default_factory=list)
    supporting_authorities: list[str] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)

