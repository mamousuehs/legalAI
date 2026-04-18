from TaoxinAI.schemas.common import Message
from TaoxinAI.schemas.intake import CaseInput
from TaoxinAI.services.issue.rule_based_identifier import RuleBasedIssueIdentifier


def test_issue_identifier_detects_wage_and_relationship_issues():
    case_input = CaseInput(
        messages=[
            Message(role="user", content="老板拖欠我3000元工资，没有合同，但是我在工地上班。")
        ]
    )

    issues = RuleBasedIssueIdentifier().identify(case_input, [])
    issue_codes = {issue.issue_code for issue in issues}

    assert "unpaid_wages" in issue_codes
    assert "labor_relationship" in issue_codes
