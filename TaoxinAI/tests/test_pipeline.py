import pytest
from TaoxinAI.schemas.common import Message
from TaoxinAI.schemas.intake import CaseInput
from TaoxinAI.schemas.reasoning import DocumentGenerationRequest, FullAnalysisResponse, VerificationResult, IRACDraft
from TaoxinAI.pipelines.case_analysis import CaseAnalysisPipeline

# ==========================================
# 1. 准备 Mock (假) 数据库和客户端
# ==========================================
class MockCollection:
    """模拟 ChromaDB 的 Collection 对象"""
    def __init__(self, mock_type="norm"):
        self.mock_type = mock_type

    def query(self, query_texts, n_results):
        # 模拟 Chroma 原生返回的复杂字典格式
        return {
            "documents": [["测试文本内容"]],
            "ids": [[f"{self.mock_type}_123"]],
            "metadatas": [[{"source_type": self.mock_type, "title": "测试依据"}]]
        }

class MockLLMClient:
    """模拟大模型客户端 (目前还没接大模型，先占位)"""
    pass

# ==========================================
# 2. Pipeline 集成测试
# ==========================================
@pytest.fixture
def pipeline():
    """Pytest 夹具：在每次测试前组装好 Pipeline"""
    law_col = MockCollection("norm")
    case_col = MockCollection("case")
    llm_client = MockLLMClient()
    return CaseAnalysisPipeline(law_col, case_col, llm_client)

@pytest.mark.asyncio
async def test_analyze_chat_turn(pipeline: CaseAnalysisPipeline):
    """测试多轮对话的状态流转 (StateMachine)"""
    # 模拟用户刚进来的第一句话
    messages = [Message(role="user", content="公司拖欠我工资！")]
    case_input = CaseInput(messages=messages, extracted_info={"_stage": "initial"})
    
    response = await pipeline.analyze_chat_turn(case_input)
    
    # 验证状态机是否正确向下流转
    assert response.conversation_stage == "basic_facts", "应该从 initial 流转到 basic_facts"
    assert len(response.quick_replies) > 0, "必须生成快捷回复按钮"
    # 验证是否顺手提取了实体
    assert response.extracted_info.get("employer_type") == "company", "必须识别出'公司'实体"

@pytest.mark.asyncio
async def test_run_full_analysis(pipeline: CaseAnalysisPipeline):
    """测试核心链路：从输入到生成 IRAC 的端到端分析"""
    # 给定一个证据确凿的完美案情
    messages = [Message(role="user", content="建筑公司拖欠了我8000块，我有劳动合同，也有微信转账记录和考勤记录。")]
    case_input = CaseInput(messages=messages)
    
    response = await pipeline.run_full_analysis(case_input)
    
    # 验证是否生成了完整分析结果
    assert isinstance(response, FullAnalysisResponse)
    
    # 检查检索层是否工作
    assert len(response.retrieved_authorities) > 0
    
    # 检查事实抽取是否工作
    fact_types = [f.fact_type for f in response.facts]
    assert "amount" in fact_types
    assert "contract_status" in fact_types
    
    # 检查 IRAC 生成是否工作
    assert len(response.irac_drafts) > 0
    draft = response.irac_drafts[0]
    assert draft.issue != ""
    assert draft.application != ""

@pytest.mark.asyncio
async def test_generate_document(pipeline: CaseAnalysisPipeline):
    """测试文书生成环节的拼装逻辑"""
    # 伪造一个前面的分析结果
    mock_case_input = CaseInput(messages=[], extracted_info={
        "amount": "8000元",
        "employer_name": "某某建设工程有限公司",
        "worker_name": "张三"
    })
    
    mock_analysis = FullAnalysisResponse(
        case_summary="", retrieved_authorities=[], issues=[], facts=[], element_matches=[], reason_bundles=[],
        irac_drafts=[IRACDraft(issue="测试", rule="", application="案件事实明确，存在拖欠", conclusion="", citations=[])],
        verification=VerificationResult(is_complete=True, missing_elements=[], consistency_warnings=["证据尚有瑕疵"])
    )
    
    request = DocumentGenerationRequest(case_input=mock_case_input, analysis=mock_analysis)
    response = await pipeline.generate_document(request)
    
    # 验证占位符是否被正确替换
    assert "张三" in response.document
    assert "某某建设工程有限公司" in response.document
    assert "8000元" in response.document
    assert "案件事实明确，存在拖欠" in response.document
    assert "证据尚有瑕疵" in response.risk_notes[0]
