from TaoxinAI.schemas.fact import FactItem
from TaoxinAI.schemas.issue import Issue
from TaoxinAI.schemas.retrieval import RetrievedAuthority
from TaoxinAI.services.matching.element_matcher import ElementMatcher


def test_element_matcher_marks_unpaid_wage_amount_as_partial_when_present():
    issues = [
        Issue(issue_code="unpaid_wages", issue_name="是否欠薪", description=""),
    ]
    facts = [
        FactItem(fact_type="amount", value="3000元", evidence_status="claimed"),
    ]
    authorities = [
        RetrievedAuthority(
            source_type="norm",
            source_id="norm_1",
            title="劳动合同法第八十二条",
            snippet="...",
            score=1.0,
            metadata={},
        )
    ]

    matches = ElementMatcher().match(issues, facts, authorities)

    assert matches
    assert matches[0].status == "partial"
