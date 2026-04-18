from TaoxinAI.schemas.common import Message
from TaoxinAI.schemas.intake import CaseInput
from TaoxinAI.schemas.issue import Issue
from TaoxinAI.services.fact.rule_based_extractor import RuleBasedFactExtractor


def test_fact_extractor_pulls_amount_and_evidence_clues():
    case_input = CaseInput(
        messages=[
            Message(role="user", content="老板拖欠我3000元工资，我有聊天记录和转账记录。")
        ]
    )
    issues = [
        Issue(issue_code="unpaid_wages", issue_name="是否欠薪", description=""),
    ]

    facts = RuleBasedFactExtractor().extract(case_input, issues)
    fact_types = {fact.fact_type for fact in facts}

    assert "amount" in fact_types
    assert "chat_record" in fact_types
    assert "transfer_record" in fact_types
