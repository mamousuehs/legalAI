from fastapi import APIRouter, Request

from TaoxinAI.schemas.intake import CaseInput
from TaoxinAI.schemas.reasoning import FullAnalysisResponse


router = APIRouter()


@router.post("/analyze", response_model=FullAnalysisResponse)
async def analyze_endpoint(case_input: CaseInput, request: Request) -> FullAnalysisResponse:
    pipeline = request.app.state.pipeline
    return await pipeline.run_full_analysis(case_input)

