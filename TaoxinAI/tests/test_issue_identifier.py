import pytest
from TaoxinAI.schemas.common import Message
from TaoxinAI.schemas.intake import CaseInput
from TaoxinAI.services.issue.rule_based_identifier import RuleBasedIssueIdentifier

class TestRuleBasedIssueIdentifier:
    """测试基于规则的争点识别功能"""
    
    def setup_method(self):
        """每个测试前初始化识别器和空的检索占位符"""
        self.identifier = RuleBasedIssueIdentifier()
        self.dummy_authorities = [] # 规则版暂不需要用到检索库

    def test_identify_unpaid_wages_only(self):
        """测试单一触发：仅触发欠薪争点"""
        messages = [Message(role="user", content="别人一直拖欠我的血汗钱")]
        case_input = CaseInput(messages=messages)
        
        issues = self.identifier.identify(case_input, self.dummy_authorities)
        codes = [issue.issue_code for issue in issues]
        
        assert len(issues) == 1
        assert "unpaid_wages" in codes, "含有'拖欠'关键字，必须触发欠薪争点"

    def test_identify_labor_relationship_only(self):
        """测试单一触发：仅触发劳动关系争点"""
        messages = [Message(role="user", content="我天天去工地上班")]
        case_input = CaseInput(messages=messages)
        
        issues = self.identifier.identify(case_input, self.dummy_authorities)
        codes = [issue.issue_code for issue in issues]
        
        assert len(issues) == 1
        assert "labor_relationship" in codes, "含有'上班'和'工地'，必须触发劳动关系争点"

    def test_identify_multiple_issues(self):
        """测试组合触发：一句话同时触发多个核心争点"""
        messages = [Message(role="user", content="公司老板一直欠薪不给！")]
        case_input = CaseInput(messages=messages)
        
        issues = self.identifier.identify(case_input, self.dummy_authorities)
        codes = [issue.issue_code for issue in issues]
        
        assert len(issues) == 2, "应该同时识别出两个争点"
        assert "unpaid_wages" in codes
        assert "labor_relationship" in codes

    def test_ignore_assistant_messages(self):
        """测试防呆边界：必须忽略 AI 助手自己说的话，防止系统被自己带偏"""
        messages = [
            # 助手的话里包含了所有触发关键词
            Message(role="assistant", content="请问老板或者公司有拖欠你的工资吗？"),
            # 用户的话里没有任何关键词
            Message(role="user", content="是的，太让人头疼了")
        ]
        case_input = CaseInput(messages=messages)
        
        issues = self.identifier.identify(case_input, self.dummy_authorities)
        
        assert len(issues) == 0, "只能从用户的话语中识别争点，不能被助手的问题触发"

    def test_no_issue_triggered(self):
        """测试防呆边界：没有相关线索时不应报错"""
        messages = [Message(role="user", content="我想咨询个问题，能帮帮我吗")]
        case_input = CaseInput(messages=messages)
        
        issues = self.identifier.identify(case_input, self.dummy_authorities)
        
        assert isinstance(issues, list)
        assert len(issues) == 0, "无相关关键词时返回空列表"
