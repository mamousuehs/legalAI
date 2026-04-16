from pathlib import Path

from TaoxinAI.schemas.retrieval import RetrievedAuthority


class TemplateRetriever:
    """Retrieves local template files as candidate analysis aids."""

    def __init__(self, template_root: Path):
        self.template_root = template_root

    def retrieve(self, query: str, n_results: int = 2) -> list[RetrievedAuthority]:
        if not self.template_root.exists():
            return []

        candidates = []
        for path in sorted(self.template_root.glob("*.yaml")):
            candidates.append(
                RetrievedAuthority(
                    source_type="template",
                    source_id=path.stem,
                    title=path.name,
                    snippet=f"本地模板文件：{path.name}",
                    score=0.5,
                    metadata={"path": str(path)},
                )
            )
        return candidates[:n_results]
