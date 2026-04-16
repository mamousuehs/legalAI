from fastapi import APIRouter, Request

from TaoxinAI.schemas.reasoning import DocumentGenerationRequest, DocumentGenerationResponse


router = APIRouter()


@router.post("/generate-document", response_model=DocumentGenerationResponse)
async def generate_document_endpoint(
    payload: DocumentGenerationRequest,
    request: Request,
) -> DocumentGenerationResponse:
    pipeline = request.app.state.pipeline
    return await pipeline.generate_document(payload)

