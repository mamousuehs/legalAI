from pathlib import Path


class TemplateRepository:
    """Reads local text and yaml templates used by the reasoning flow."""

    def __init__(self, root: Path):
        self.root = root

