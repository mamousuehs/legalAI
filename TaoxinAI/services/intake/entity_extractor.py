import re


AMOUNT_PATTERN = re.compile(r"(\d+(?:\.\d+)?)\s*(\u5143|\u5757)")
COMPANY_TOKENS = ("\u516c\u53f8", "\u5355\u4f4d")
CONTRACTOR_TOKENS = ("\u8001\u677f", "\u5305\u5de5\u5934")
CONTRACT_TOKEN = "\u5408\u540c"
NEGATION_TOKENS = ("\u6ca1", "\u65e0", "\u672a")
EVIDENCE_KEYWORDS = (
    "\u804a\u5929\u8bb0\u5f55",
    "\u8f6c\u8d26\u8bb0\u5f55",
    "\u8003\u52e4\u8bb0\u5f55",
    "\u6b20\u6761",
    "\u7ed3\u7b97\u5355",
    "\u5de5\u53cb\u8bc1\u8a00",
)


class EntityExtractor:
    """Small rule-based extractor for wage-recovery intake fields."""

    def extract(self, text: str) -> dict:
        extracted = {}

        amount_match = AMOUNT_PATTERN.search(text)
        if amount_match:
            extracted["amount"] = f"{amount_match.group(1)}{amount_match.group(2)}"

        if any(token in text for token in COMPANY_TOKENS):
            extracted["employer_type"] = "company"
        elif any(token in text for token in CONTRACTOR_TOKENS):
            extracted["employer_type"] = "contractor_or_employer"

        if CONTRACT_TOKEN in text:
            has_negation = any(token in text for token in NEGATION_TOKENS)
            extracted["has_contract"] = "\u6709" if not has_negation else "\u6ca1\u6709"

        evidence_hits = [keyword for keyword in EVIDENCE_KEYWORDS if keyword in text]
        if evidence_hits:
            extracted["evidence_types"] = "\u3001".join(evidence_hits)

        return extracted
