import pytest

from TaoxinAI.pipelines.case_analysis import CaseAnalysisPipeline
from TaoxinAI.schemas.common import Message
from TaoxinAI.schemas.intake import CaseInput
from TaoxinAI.schemas.reasoning import (
    DocumentGenerationRequest,
    FullAnalysisResponse,
    IRACDraft,
    VerificationResult,
)


class MockCollection:
    def __init__(self, mock_type: str = "norm"):
        self.mock_type = mock_type

    def query(self, query_texts, n_results):
        if self.mock_type == "norm":
            return {
                "documents": [["《劳动合同法》第三十条", "用人单位应当按照劳动合同约定和国家规定，及时足额支付劳动报酬。"]],
                "ids": [["law_30", "law_31"]],
                "metadatas": [[
                    {"source_type": "norm", "title": "《劳动合同法》第三十条"},
                    {"source_type": "norm", "title": "《劳动合同法》第三十条"},
                ]],
            }

        return {
            "documents": [["相似案例内容"]],
            "ids": [[f"{self.mock_type}_123"]],
            "metadatas": [[{"source_type": self.mock_type, "title": "测试案例"}]],
        }

    def get(self, ids, include):
        record_map = {
            "law_30": {
                "document": "《劳动合同法》第三十条",
                "metadata": {"source_type": "norm", "title": "《劳动合同法》第三十条"},
            },
            "law_31": {
                "document": "用人单位应当按照劳动合同约定和国家规定，及时足额支付劳动报酬。",
                "metadata": {"source_type": "norm", "title": "《劳动合同法》第三十条"},
            },
        }

        found_ids = []
        found_docs = []
        found_metadatas = []
        for doc_id in ids:
            if doc_id not in record_map:
                continue
            found_ids.append(doc_id)
            found_docs.append(record_map[doc_id]["document"])
            found_metadatas.append(record_map[doc_id]["metadata"])

        return {
            "ids": found_ids,
            "documents": found_docs,
            "metadatas": found_metadatas,
        }


class MockLLMClient:
    pass


class FakeMessage:
    def __init__(self, content: str):
        self.content = content


class FakeChoice:
    def __init__(self, content: str):
        self.message = FakeMessage(content)


class FakeCompletionResponse:
    def __init__(self, content: str):
        self.choices = [FakeChoice(content)]


class FakeCompletions:
    def __init__(self, content: str):
        self.content = content
        self.calls = []

    async def create(self, **kwargs):
        self.calls.append(kwargs)
        return FakeCompletionResponse(self.content)


class FakeChatAPI:
    def __init__(self, content: str):
        self.completions = FakeCompletions(content)


class FakeLLMClient:
    def __init__(self, content: str):
        self.chat = FakeChatAPI(content)


@pytest.fixture
def pipeline():
    law_col = MockCollection("norm")
    case_col = MockCollection("case")
    return CaseAnalysisPipeline(law_col, case_col, MockLLMClient())


@pytest.mark.asyncio
async def test_analyze_chat_turn_uses_rule_based_fallback_without_llm(pipeline: CaseAnalysisPipeline):
    messages = [Message(role="user", content="公司拖欠我工资！")]
    case_input = CaseInput(messages=messages, extracted_info={"_stage": "initial"})

    response = await pipeline.analyze_chat_turn(case_input)

    assert response.conversation_stage == "basic_facts"
    assert response.quick_replies
    assert response.extracted_info.get("employer_type") == "company"
    assert response.reply_source == "rule_based"


@pytest.mark.asyncio
async def test_analyze_chat_turn_prefers_legalone_when_available():
    law_col = MockCollection("norm")
    case_col = MockCollection("case")
    llm_client = FakeLLMClient("依据《劳动合同法》第三十条，用人单位应及时足额支付工资。请问您是否有转账记录或劳动合同？")
    pipeline = CaseAnalysisPipeline(law_col, case_col, llm_client)

    response = await pipeline.analyze_chat_turn(
        CaseInput(
            messages=[Message(role="user", content="公司拖欠我工资")],
            extracted_info={"_stage": "initial"},
        )
    )

    assert response.reply_source == "legalone"
    assert "《劳动合同法》第三十条" in response.reply
    assert llm_client.chat.completions.calls


@pytest.mark.asyncio
async def test_run_full_analysis(pipeline: CaseAnalysisPipeline):
    messages = [Message(role="user", content="建筑公司拖欠了我8000块，我有劳动合同，也有微信转账记录和考勤记录。")]
    case_input = CaseInput(messages=messages)

    response = await pipeline.run_full_analysis(case_input)

    assert isinstance(response, FullAnalysisResponse)
    assert response.retrieved_authorities

    fact_types = [fact.fact_type for fact in response.facts]
    assert "amount" in fact_types
    assert "contract_status" in fact_types

    assert response.irac_drafts
    draft = response.irac_drafts[0]
    assert draft.issue
    assert draft.application


@pytest.mark.asyncio
async def test_generate_document(pipeline: CaseAnalysisPipeline):
    mock_case_input = CaseInput(
        messages=[],
        extracted_info={
            "amount": "8000元",
            "employer_name": "某建设工程有限公司",
            "worker_name": "张三",
        },
    )

    mock_analysis = FullAnalysisResponse(
        case_summary="",
        retrieved_authorities=[],
        issues=[],
        facts=[],
        element_matches=[],
        reason_bundles=[],
        irac_drafts=[
            IRACDraft(
                issue="测试",
                rule="",
                application="案件事实明确，存在拖欠工资情形。",
                conclusion="",
                citations=[],
            )
        ],
        verification=VerificationResult(consistency_warnings=["证据仍需补强"]),
    )

    request = DocumentGenerationRequest(case_input=mock_case_input, analysis=mock_analysis)
    response = await pipeline.generate_document(request)

    assert "张三" in response.document
    assert "某建设工程有限公司" in response.document
    assert "8000元" in response.document
    assert "案件事实明确，存在拖欠工资情形。" in response.document
    assert "证据仍需补强" in response.risk_notes[0]


@pytest.mark.asyncio
async def test_generate_document_switches_to_arbitration_when_not_yet_arbitrated(pipeline: CaseAnalysisPipeline):
    mock_case_input = CaseInput(
        messages=[],
        extracted_info={
            "name": "张三",
            "employer_name": "某劳务公司",
            "amount": "12000元",
            "has_arbitration": False,
        },
    )
    mock_analysis = FullAnalysisResponse(
        case_summary="",
        retrieved_authorities=[],
        issues=[],
        facts=[],
        element_matches=[],
        reason_bundles=[],
        irac_drafts=[],
        verification=VerificationResult(),
    )

    response = await pipeline.generate_document(
        DocumentGenerationRequest(
            document_type="labor_arbitration_application",
            case_input=mock_case_input,
            analysis=mock_analysis,
        )
    )

    assert "劳动仲裁申请书" in response.document
    assert "请求裁决被申请人支付拖欠工资 12000元" in response.document


@pytest.mark.asyncio
async def test_generate_document_docx_returns_word_bytes_and_filename(pipeline: CaseAnalysisPipeline):
    case_input = CaseInput(
        messages=[Message(role="user", content="公司拖欠了我8000元工资")],
        extracted_info={
            "name": "张三",
            "employer_name": "某建设工程有限公司",
            "has_arbitration": False,
        },
    )

    file_bytes, filename = await pipeline.generate_document_docx(case_input)

    assert filename == "劳动仲裁申请书.docx"
    assert file_bytes[:2] == b"PK"
