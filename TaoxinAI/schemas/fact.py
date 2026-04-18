from typing import Literal, Optional

from pydantic import BaseModel


class FactItem(BaseModel):
    issue_code: Optional[str] = None
    fact_type: str
    value: str
    evidence_status: Literal["supported", "claimed", "missing", "contradicted"]
    source_span: Optional[str] = None
