from TaoxinAI.schemas.issue import Issue
from TaoxinAI.schemas.match import ElementMatch
from TaoxinAI.schemas.reasoning import ReasonBundle


class ReasonBuilder:
    """Builds support and oppose reasons from element matches."""

    def build(self, issues: list[Issue], matches: list[ElementMatch]) -> list[ReasonBundle]:
        bundles: list[ReasonBundle] = []
        for issue in issues:
            issue_matches = [item for item in matches if item.issue_code == issue.issue_code]
            support = [
                f"{item.element_name}：{item.status}"
                for item in issue_matches
                if item.status in {"satisfied", "partial"}
            ]
            gaps = [gap for item in issue_matches for gap in item.missing_evidence]
            bundles.append(
                ReasonBundle(
                    issue_code=issue.issue_code,
                    support_reasons=support,
                    oppose_reasons=[],
                    evidence_gaps=gaps,
                    tentative_conclusion="现有材料可以进入进一步分析，但仍需补强关键事实。",
                )
            )
        return bundles

