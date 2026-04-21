import pytest
from TaoxinAI.schemas.fact import FactItem
from TaoxinAI.schemas.issue import Issue
from TaoxinAI.schemas.retrieval import RetrievedAuthority
from TaoxinAI.services.matching.element_matcher import ElementMatcher

class TestElementMatcher:
    """测试要件匹配逻辑（核对事实是否满足法律要件）"""
    
    def setup_method(self):
        """每个测试用例前初始化 matcher 和一些假数据"""
        self.matcher = ElementMatcher()
        # 模拟从向量库检索出来的法条
        self.dummy_authorities = [
            RetrievedAuthority(
                source_type="norm", 
                source_id="law_1", 
                title="《劳动合同法》", 
                snippet="...", 
                score=0.9
            )
        ]

    def test_unpaid_wages_satisfied_with_amount(self):
        """测试正常路径：有具体金额事实时，欠薪要件应判定为 partial"""
        issues = [Issue(issue_code="unpaid_wages", issue_name="拖欠报酬", description="")]
        # 事实列表里包含了 amount
        facts = [
            FactItem(issue_code="unpaid_wages", fact_type="amount", value="5000", evidence_status="claimed")
        ]
        
        matches = self.matcher.match(issues, facts, self.dummy_authorities)
        
        assert len(matches) == 1
        assert matches[0].issue_code == "unpaid_wages"
        assert matches[0].status == "partial", "拥有金额事实，状态必须是 partial"
        assert "amount" in matches[0].supporting_facts
        assert len(matches[0].missing_evidence) == 0, "金额已明确，不应再提示缺失金额证据"
        assert "law_1" in matches[0].supporting_authorities, "检索到的法条应成功挂载到该匹配结果上"

    def test_unpaid_wages_insufficient(self):
        """测试边界防呆：主张欠薪，但连个金额都没提，要件必须被卡住"""
        issues = [Issue(issue_code="unpaid_wages", issue_name="拖欠报酬", description="")]
        # 事实列表里只有个聊天记录，没有具体金额 (amount)
        facts = [
            FactItem(issue_code="unpaid_wages", fact_type="chat_record", value="微信聊天", evidence_status="claimed")
        ]
        
        matches = self.matcher.match(issues, facts, self.dummy_authorities)
        
        assert matches[0].status == "insufficient", "没有提取到金额，状态必须是 insufficient"
        assert len(matches[0].supporting_facts) == 0
        assert "工资金额或计算依据" in matches[0].missing_evidence, "必须准确提示缺失的关键证据"

    def test_labor_relationship_satisfied(self):
        """测试正常路径：有合同情况时，劳动关系要件应判定为 partial"""
        issues = [Issue(issue_code="labor_relationship", issue_name="劳动关系", description="")]
        facts = [
            FactItem(issue_code="labor_relationship", fact_type="contract_status", value="没签合同", evidence_status="claimed")
        ]
        
        matches = self.matcher.match(issues, facts, self.dummy_authorities)
        
        assert matches[0].status == "partial"
        assert "contract_status" in matches[0].supporting_facts

    def test_multiple_issues_mixed_facts(self):
        """测试复杂场景：多个争点同时存在，有的证据足，有的证据不足"""
        issues = [
            Issue(issue_code="unpaid_wages", issue_name="拖欠报酬", description=""),
            Issue(issue_code="labor_relationship", issue_name="劳动关系", description="")
        ]
        # 用户只说了被欠 8000 块钱，完全没提有没有签合同
        facts = [
            FactItem(issue_code="unpaid_wages", fact_type="amount", value="8000", evidence_status="claimed")
        ]
        
        matches = self.matcher.match(issues, facts, self.dummy_authorities)
        
        assert len(matches) == 2, "有两个争点，就必须生成两个要件匹配报告"
        
        # 欠薪部分因为有 amount，是 partial
        unpaid_match = next(m for m in matches if m.issue_code == "unpaid_wages")
        assert unpaid_match.status == "partial"
        
        # 劳动关系部分因为没有 contract_status，直接打回 insufficient
        labor_match = next(m for m in matches if m.issue_code == "labor_relationship")
        assert labor_match.status == "insufficient"
        assert len(labor_match.missing_evidence) > 0
