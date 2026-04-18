from TaoxinAI.schemas.retrieval import RetrievedAuthority


class CaseRetriever:
    """Retrieves candidate similar cases from the case collection."""

    def __init__(self, chroma_repo):
        self.chroma_repo = chroma_repo

    def retrieve(self, query: str, n_results: int = 3) -> list[RetrievedAuthority]:
        records = self.chroma_repo.query(query, n_results=n_results)
        items: list[RetrievedAuthority] = []

        for index, record in enumerate(records):
            source_id = record["source_id"]
            metadata = record.get("metadata", {})
            source_type = metadata.get("source_type")

            if source_type != "case" and not source_id.startswith("case"):
                continue

            items.append(
                RetrievedAuthority(
                    source_type="case",
                    source_id=source_id,
                    title=metadata.get("title") or source_id,
                    snippet=record["content"][:200],
                    score=max(0.1, 1.0 - index * 0.1),
                    metadata=metadata,
                )
            )
        return items
