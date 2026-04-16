from pydantic import BaseModel, Field


class Issue(BaseModel):
    issue_code: str
    issue_name: str
    description: str
    priority: int = 0
    triggered_by: list[str] = Field(default_factory=list)

