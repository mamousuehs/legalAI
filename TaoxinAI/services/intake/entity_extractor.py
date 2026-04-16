import re


class EntityExtractor:
    """Small rule-based extractor for wage-recovery intake fields."""

    def extract(self, text: str) -> dict:
        extracted = {}

        amount_match = re.search(r"(\d+(?:\.\d+)?)\s*(元|块)", text)
        if amount_match:
            extracted["amount"] = amount_match.group(0)

        if any(token in text for token in ["公司", "单位"]):
            extracted["employer_type"] = "company"
        elif any(token in text for token in ["老板", "包工头"]):
            extracted["employer_type"] = "contractor_or_employer"

        if "合同" in text:
            extracted["has_contract"] = "有" if "没" not in text else "没有"

        evidence_hits = []
        for keyword in ["聊天记录", "转账记录", "考勤记录", "欠条", "结算单", "工友证言"]:
            if keyword in text:
                evidence_hits.append(keyword)
        if evidence_hits:
            extracted["evidence_types"] = "、".join(evidence_hits)

        return extracted
