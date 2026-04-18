from TaoxinAI.services.intake.entity_extractor import EntityExtractor
from TaoxinAI.services.intake.normalizer import IntakeNormalizer


def test_normalizer_collapses_whitespace():
    assert IntakeNormalizer().normalize(" 老板   拖欠  我工资 ") == "老板 拖欠 我工资"


def test_entity_extractor_extracts_amount_and_evidence():
    extracted = EntityExtractor().extract("老板拖欠我3000元工资，我有聊天记录和转账记录。")
    assert extracted["amount"] == "3000元"
    assert "聊天记录" in extracted["evidence_types"]
