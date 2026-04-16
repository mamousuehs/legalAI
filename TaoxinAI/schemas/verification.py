from pydantic import BaseModel, Field


class VerificationResult(BaseModel):
    passed: bool = True
    citation_errors: list[str] = Field(default_factory=list)
    missing_elements: list[str] = Field(default_factory=list)
    unsupported_claims: list[str] = Field(default_factory=list)
    consistency_warnings: list[str] = Field(default_factory=list)

