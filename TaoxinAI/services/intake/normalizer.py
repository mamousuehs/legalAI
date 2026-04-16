class IntakeNormalizer:
    """Normalizes raw chat input before retrieval and analysis."""

    def normalize(self, text: str) -> str:
        return " ".join(text.strip().split())
