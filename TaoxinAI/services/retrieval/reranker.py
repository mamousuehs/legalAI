from TaoxinAI.schemas.retrieval import RetrievedAuthority


class Reranker:
    """Simple score sorter placeholder for retrieved authorities."""

    def rerank(self, items: list[RetrievedAuthority]) -> list[RetrievedAuthority]:
        return sorted(items, key=lambda item: item.score, reverse=True)
