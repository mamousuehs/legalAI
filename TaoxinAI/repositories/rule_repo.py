from pathlib import Path


class RuleRepository:
    """Reads local rule configuration files."""

    def __init__(self, root: Path):
        self.root = root

