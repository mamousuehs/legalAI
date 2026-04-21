import pytest
from TaoxinAI.schemas.common import Message
from TaoxinAI.schemas.intake import CaseInput
from TaoxinAI.schemas.issue import Issue
from TaoxinAI.services.fact.rule_based_extractor import RuleBasedFactExtractor

def test_extract_wage_amount():
    """测试正常情况：能否正确通过正则提取出金额"""
    # 模拟前端传来的对话历史
    messages = [
        Message(role="assistant", content="请问老板欠你多少钱？"),
        Message(role="user", content="他在上个月少发了我 5000.5 块的工资")
    ]
    case_input = CaseInput(messages=messages)
    
    extractor = RuleBasedFactExtractor()
    # 当前规则版抽取并不强依赖 issues 参数，传个空列表就行
    facts = extractor.extract(case_input, issues=[])
    
    # 我们期望它能抓出 5000.5 块这个信息
    amount_facts = [f for f in facts if f.fact_type == "amount"]
    
    assert len(amount_facts) == 1, "必须提取出一条金额事实"
    assert amount_facts[0].value == "5000.5 块", "提取的金额数值或单位不对"
    assert amount_facts[0].issue_code == "unpaid_wages", "金额事实应该归类到拖欠工资的争点下"
    assert amount_facts[0].evidence_status == "claimed", "从用户话语中直接提取的，只能算主张(claimed)，不能算证实"

def test_extract_evidence_keywords():
    """测试边界情况：一段话里包含多种证据线索时，能否全部抓取"""
    messages = [
        Message(role="user", content="我有微信聊天截图，也有他当时打给我的欠条，当时没签劳动合同。")
    ]
    case_input = CaseInput(messages=messages)
    
    extractor = RuleBasedFactExtractor()
    facts = extractor.extract(case_input, issues=[])
    
    # 提取所有抓取到的 fact_type
    fact_types = [f.fact_type for f in facts]
    
    assert "chat_record" in fact_types, "未能识别到'聊天'关键字"
    assert "iou" in fact_types, "未能识别到'欠条'关键字"
    assert "contract_status" in fact_types, "未能识别到'合同'关键字"
    assert "transfer_record" not in fact_types, "不该无中生有提取出转账记录"

def test_extract_empty_or_irrelevant_input():
    """测试防呆情况：用户废话连篇毫无线索时，系统不能报错"""
    messages = [
        Message(role="user", content="老板就是个王八蛋，我天天起早贪黑干活，他良心被狗吃了！")
    ]
    case_input = CaseInput(messages=messages)
    
    extractor = RuleBasedFactExtractor()
    facts = extractor.extract(case_input, issues=[])
    
    # 因为没有金额数字，也没有规定的关键字，返回的必须是空列表
    assert isinstance(facts, list)
    assert len(facts) == 0, "用户没有提供有效事实，提取列表应该为空"
