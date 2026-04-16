from TaoxinAI.schemas.issue import Issue
from TaoxinAI.schemas.match import ElementMatch
from TaoxinAI.schemas.reasoning import IRACDraft, ReasonBundle
from TaoxinAI.schemas.retrieval import RetrievedAuthority


class IRACGenerator:
    """Builds simple IRAC drafts from the structured intermediate results."""

    def generate(
        self,
        issues: list[Issue],
        matches: list[ElementMatch],
        reasons: list[ReasonBundle],
        retrieved_authorities: list[RetrievedAuthority],
    ) -> list[IRACDraft]:
        citations = [item.title for item in retrieved_authorities[:2]]
        drafts: list[IRACDraft] = []

        for issue in issues:
            issue_matches = [item for item in matches if item.issue_code == issue.issue_code]
            issue_reasons = next((item for item in reasons if item.issue_code == issue.issue_code), None)
            application = "；".join(
                [f"{item.element_name}当前状态为{item.status}" for item in issue_matches]
            ) or "当前尚未形成完整的要件匹配结果。"
            if issue_reasons and issue_reasons.evidence_gaps:
                application += f" 仍需补强：{'、'.join(issue_reasons.evidence_gaps)}。"

            drafts.append(
                IRACDraft(
                    issue=issue.issue_name,
                    rule="后续将在此处绑定具体法条、司法解释和裁判规则。",
                    application=application,
                    conclusion="当前结论为初步判断，需结合更多证据继续分析。",
                    citations=citations,
                )
            )

        return drafts

