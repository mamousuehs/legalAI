import re

from TaoxinAI.schemas.fact import FactItem
from TaoxinAI.schemas.intake import CaseInput
from TaoxinAI.schemas.issue import Issue


class RuleBasedFactExtractor:
    """Simple rule-based extractor for wage, contract, and evidence clues."""

    def extract(self, case_input: CaseInput, issues: list[Issue]) -> list[FactItem]:
        text = " ".join(message.content for message in case_input.messages if message.role == "user")
        facts: list[FactItem] = []

        amount_match = re.search(r"(\d+(?:\.\d+)?)\s*(元|块)", text)
        if amount_match:
            facts.append(
                FactItem(
                    issue_code="unpaid_wages",
                    fact_type="amount",
                    value=amount_match.group(0),
                    evidence_status="claimed",
                )
            )

        if "合同" in text:
            facts.append(
                FactItem(
                    issue_code="labor_relationship",
                    fact_type="contract_status",
                    value="提到合同情况",
                    evidence_status="claimed",
                )
            )

        for keyword, fact_type in [
            ("聊天", "chat_record"),
            ("转账", "transfer_record"),
            ("考勤", "attendance_record"),
            ("欠条", "iou"),
        ]:
            if keyword in text:
                facts.append(
                    FactItem(
                        issue_code="unpaid_wages",
                        fact_type=fact_type,
                        value=f"提到{keyword}证据",
                        evidence_status="claimed",
                    )
                )

        return facts
