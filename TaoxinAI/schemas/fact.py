from typing import Literal

from pydantic import BaseModel


class FactItem(BaseModel):
    issue_code: str | None = None
    fact_type: str
    value: str
    evidence_status: Literal["supported", "claimed", "missing", "contradicted"]
    source_span: str | None = None

