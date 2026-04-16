from fastapi import APIRouter, Request

from TaoxinAI.schemas.intake import CaseInput
from TaoxinAI.schemas.reasoning import AnalysisResponse


router = APIRouter()


@router.post("/chat", response_model=AnalysisResponse)
async def chat_endpoint(case_input: CaseInput, request: Request) -> AnalysisResponse:
    pipeline = request.app.state.pipeline
    return await pipeline.analyze_chat_turn(case_input)

