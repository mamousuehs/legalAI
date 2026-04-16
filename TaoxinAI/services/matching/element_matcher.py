from TaoxinAI.schemas.fact import FactItem
from TaoxinAI.schemas.issue import Issue
from TaoxinAI.schemas.match import ElementMatch
from TaoxinAI.schemas.retrieval import RetrievedAuthority


class ElementMatcher:
    """Matches extracted facts against issue-specific legal elements."""

    def match(
        self,
        issues: list[Issue],
        facts: list[FactItem],
        retrieved_authorities: list[RetrievedAuthority],
    ) -> list[ElementMatch]:
        matches: list[ElementMatch] = []
        fact_types = {fact.fact_type for fact in facts}
        authority_ids = [item.source_id for item in retrieved_authorities]

        for issue in issues:
            if issue.issue_code == "unpaid_wages":
                status = "partial" if "amount" in fact_types else "insufficient"
                matches.append(
                    ElementMatch(
                        issue_code=issue.issue_code,
                        element_name="拖欠工资事实是否明确",
                        status=status,
                        supporting_facts=["amount"] if "amount" in fact_types else [],
                        supporting_authorities=authority_ids[:1],
                        missing_evidence=[] if "amount" in fact_types else ["工资金额或计算依据"],
                    )
                )

            if issue.issue_code == "labor_relationship":
                status = "partial" if "contract_status" in fact_types else "insufficient"
                matches.append(
                    ElementMatch(
                        issue_code=issue.issue_code,
                        element_name="劳动关系线索是否存在",
                        status=status,
                        supporting_facts=["contract_status"] if "contract_status" in fact_types else [],
                        supporting_authorities=authority_ids[:1],
                        missing_evidence=[] if "contract_status" in fact_types else ["合同、考勤、聊天或工友证言"],
                    )
                )

        return matches

