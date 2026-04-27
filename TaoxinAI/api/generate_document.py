from io import BytesIO
from urllib.parse import quote

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from TaoxinAI.schemas.intake import CaseInput
from TaoxinAI.schemas.reasoning import DocumentGenerationRequest, DocumentGenerationResponse


router = APIRouter()


@router.post("/generate-document", response_model=DocumentGenerationResponse)
async def generate_document_endpoint(
    payload: DocumentGenerationRequest,
    request: Request,
) -> DocumentGenerationResponse:
    pipeline = request.app.state.pipeline
    return await pipeline.generate_document(payload)


@router.post("/generate-document-docx")
async def generate_document_docx_endpoint(
    case_input: CaseInput,
    request: Request,
):
    pipeline = request.app.state.pipeline
    document_bytes, filename = await pipeline.generate_document_docx(case_input)
    encoded_filename = quote(filename)
    headers = {
        "Content-Disposition": (
            f"attachment; filename=document.docx; filename*=UTF-8''{encoded_filename}"
        )
    }

    return StreamingResponse(
        BytesIO(document_bytes),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers=headers,
    )

