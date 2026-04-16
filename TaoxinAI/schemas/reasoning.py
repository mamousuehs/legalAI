from pydantic import BaseModel, Field

from TaoxinAI.schemas.fact import FactItem
from TaoxinAI.schemas.issue import Issue
from TaoxinAI.schemas.match import ElementMatch
from TaoxinAI.schemas.retrieval import RetrievedAuthority
from TaoxinAI.schemas.verification import VerificationResult


class ReasonBundle(BaseModel):
    issue_code: str
    support_reasons: list[str] = Field(default_factory=list)
    oppose_reasons: list[str] = Field(default_factory=list)
    evidence_gaps: list[str] = Field(default_factory=list)
    tentative_conclusion: str = ""


class IRACDraft(BaseModel):
    issue: str
    rule: str
    application: str
    conclusion: str
    citations: list[str] = Field(default_factory=list)


class AnalysisResponse(BaseModel):
    reply: str
    quick_replies: list[str] = Field(default_factory=list)
    conversation_stage: str
    extracted_info: dict = Field(default_factory=dict)
    retrieved_authorities: list[RetrievedAuthority] = Field(default_factory=list)
    issues: list[Issue] = Field(default_factory=list)
    facts: list[FactItem] = Field(default_factory=list)
    element_matches: list[ElementMatch] = Field(default_factory=list)
    reasoning_summary: dict = Field(default_factory=dict)
    verification: dict = Field(default_factory=dict)
    can_generate_doc: bool = False


class FullAnalysisResponse(BaseModel):
    case_summary: str
    retrieved_authorities: list[RetrievedAuthority] = Field(default_factory=list)
    issues: list[Issue] = Field(default_factory=list)
    facts: list[FactItem] = Field(default_factory=list)
    element_matches: list[ElementMatch] = Field(default_factory=list)
    reason_bundles: list[ReasonBundle] = Field(default_factory=list)
    irac_drafts: list[IRACDraft] = Field(default_factory=list)
    verification: VerificationResult = Field(default_factory=VerificationResult)


class DocumentGenerationRequest(BaseModel):
    document_type: str = "labor_complaint"
    case_input: "CaseInput"
    analysis: FullAnalysisResponse


class DocumentGenerationResponse(BaseModel):
    document: str
    citations: list[str] = Field(default_factory=list)
    risk_notes: list[str] = Field(default_factory=list)


from TaoxinAI.schemas.intake import CaseInput

DocumentGenerationRequest.model_rebuild()

