from TaoxinAI.schemas.issue import Issue
from TaoxinAI.schemas.match import ElementMatch
from TaoxinAI.schemas.reasoning import IRACDraft
from TaoxinAI.schemas.verification import VerificationResult


class CompletenessChecker:
    """Checks whether core issues and element matches are present."""

    def check(
        self,
        issues: list[Issue],
        matches: list[ElementMatch],
        irac_drafts: list[IRACDraft],
    ) -> VerificationResult:
        missing_elements = []

        if issues and not matches:
            missing_elements.append("存在争点但尚未生成要件匹配结果")
        if issues and len(irac_drafts) < len(issues):
            missing_elements.append("部分争点尚未生成 IRAC 草稿")

        return VerificationResult(
            passed=not missing_elements,
            missing_elements=missing_elements,
            consistency_warnings=[] if not missing_elements else ["当前分析仍为骨架版本。"],
        )

