import pytest
from TaoxinAI.schemas.issue import Issue
from TaoxinAI.schemas.match import ElementMatch
from TaoxinAI.schemas.reasoning import ReasonBundle
from TaoxinAI.schemas.retrieval import RetrievedAuthority
from TaoxinAI.services.reasoning.reason_builder import ReasonBuilder
from TaoxinAI.services.reasoning.irac_generator import IRACGenerator

class TestReasonBuilder:
    """测试理由构建逻辑：能否准确提取支持理由与证据缺口"""
    
    def setup_method(self):
        self.builder = ReasonBuilder()
        self.issues = [Issue(issue_code="unpaid_wages", issue_name="拖欠报酬", description="")]
        
    def test_build_support_and_gaps(self):
        """测试正常路径：有部分证据，也有证据缺口"""
        matches = [
            ElementMatch(
                issue_code="unpaid_wages", 
                element_name="拖欠金额", 
                status="partial", # 状态为部分满足
                missing_evidence=["微信转账记录"] # 存在缺口
            )
        ]
        
        bundles = self.builder.build(self.issues, matches)
        
        assert len(bundles) == 1
        bundle = bundles[0]
        assert bundle.issue_code == "unpaid_wages"
        
        # 因为状态是 partial，所以必须出现在支持理由中
        assert any("拖欠金额" in reason for reason in bundle.support_reasons)
        # 必须准确抓取出证据缺口
        assert "微信转账记录" in bundle.evidence_gaps
        assert "仍需补强" in bundle.tentative_conclusion

    def test_ignore_insufficient_support(self):
        """测试边界防呆：如果状态是 insufficient，绝不能放进支持理由里"""
        matches = [
            ElementMatch(
                issue_code="unpaid_wages", 
                element_name="用工主体", 
                status="insufficient", # 证据严重不足
                missing_evidence=["公司名称或营业执照"]
            )
        ]
        
        bundles = self.builder.build(self.issues, matches)
        bundle = bundles[0]
        
        # 状态不足，支持理由必须为空，防盲目乐观
        assert len(bundle.support_reasons) == 0, "证据不足(insufficient)的要件不能作为支持理由"
        # 但缺口必须被记录
        assert "公司名称或营业执照" in bundle.evidence_gaps


class TestIRACGenerator:
    """测试 IRAC 草稿生成逻辑：能否将所有信息结构化排版"""
    
    def setup_method(self):
        self.generator = IRACGenerator()
        self.issues = [Issue(issue_code="unpaid_wages", issue_name="拖欠报酬", description="")]
        self.authorities = [
            RetrievedAuthority(source_type="norm", source_id="1", title="《劳动合同法》", snippet="", score=1.0)
        ]

    def test_generate_draft_structure(self):
        """测试正常路径：生成的 IRAC 草稿必须包含所有必要维度"""
        matches = [
            ElementMatch(issue_code="unpaid_wages", element_name="拖欠金额", status="partial")
        ]
        reasons = [
            ReasonBundle(issue_code="unpaid_wages", support_reasons=[], oppose_reasons=[], evidence_gaps=["考勤表"])
        ]
        
        drafts = self.generator.generate(self.issues, matches, reasons, self.authorities)
        
        assert len(drafts) == 1
        draft = drafts[0]
        
        # 验证 I (Issue)
        assert draft.issue == "拖欠报酬"
        # 验证 A (Application) 中是否缝合了状态和缺口
        assert "拖欠金额" in draft.application
        assert "考勤表" in draft.application
        # 验证引用的法条
        assert "《劳动合同法》" in draft.citations
