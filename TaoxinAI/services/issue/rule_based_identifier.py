from TaoxinAI.schemas.intake import CaseInput
from TaoxinAI.schemas.issue import Issue
from TaoxinAI.schemas.retrieval import RetrievedAuthority


class RuleBasedIssueIdentifier:
    """Simple rule-first issue detector for the wage-recovery scenario."""

    def identify(
        self,
        case_input: CaseInput,
        retrieved_authorities: list[RetrievedAuthority],
    ) -> list[Issue]:
        text = " ".join(message.content for message in case_input.messages if message.role == "user")
        issues: list[Issue] = []

        if any(token in text for token in ["工资", "欠薪", "拖欠"]):
            issues.append(
                Issue(
                    issue_code="unpaid_wages",
                    issue_name="是否存在拖欠劳动报酬",
                    description="判断用工主体是否存在拖欠工资的情况。",
                    priority=1,
                    triggered_by=["工资", "欠薪", "拖欠"],
                )
            )

        if any(token in text for token in ["合同", "上班", "工地", "公司", "老板"]):
            issues.append(
                Issue(
                    issue_code="labor_relationship",
                    issue_name="是否成立劳动关系或事实劳动关系",
                    description="判断申请人与被申请人之间是否存在劳动关系。",
                    priority=2,
                    triggered_by=["合同", "公司", "老板"],
                )
            )

        return issues

