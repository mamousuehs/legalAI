from TaoxinAI.schemas.retrieval import RetrievedAuthority


class CaseRetriever:
    """Retrieves candidate similar cases from the shared Chroma repository."""

    def __init__(self, chroma_repo):
        self.chroma_repo = chroma_repo

    def retrieve(self, query: str, n_results: int = 3) -> list[RetrievedAuthority]:
        if not query:
            return []

        results = self.chroma_repo.query(query, n_results=n_results)
        documents = results.get("documents", [[]])[0]
        ids = results.get("ids", [[]])[0]

        items: list[RetrievedAuthority] = []
        for index, (doc_id, document) in enumerate(zip(ids, documents)):
            if not doc_id.startswith("case"):
                continue
            items.append(
                RetrievedAuthority(
                    source_type="case",
                    source_id=doc_id,
                    title=doc_id,
                    snippet=document[:200],
                    score=max(0.1, 1.0 - index * 0.1),
                    metadata={},
                )
            )
        return items
