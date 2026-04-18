from TaoxinAI.schemas.issue import Issue
from TaoxinAI.schemas.match import ElementMatch
from TaoxinAI.schemas.reasoning import ReasonBundle
from TaoxinAI.schemas.retrieval import RetrievedAuthority
from TaoxinAI.services.reasoning.irac_generator import IRACGenerator


def test_irac_generator_returns_one_draft_per_issue():
    issues = [
        Issue(issue_code="unpaid_wages", issue_name="是否欠薪", description=""),
    ]
    matches = [
        ElementMatch(
            issue_code="unpaid_wages",
            element_name="拖欠工资事实是否明确",
            status="partial",
            supporting_facts=["amount"],
            supporting_authorities=["norm_1"],
            missing_evidence=[],
        )
    ]
    reasons = [
        ReasonBundle(
            issue_code="unpaid_wages",
            support_reasons=["拖欠工资事实是否明确：partial"],
            oppose_reasons=[],
            evidence_gaps=[],
            tentative_conclusion="可继续分析",
        )
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

    drafts = IRACGenerator().generate(issues, matches, reasons, authorities)

    assert len(drafts) == 1
    assert drafts[0].issue == "是否欠薪"
