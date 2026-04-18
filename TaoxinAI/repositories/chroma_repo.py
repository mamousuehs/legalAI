from typing import Any


class ChromaRepository:
    """Wrapper around a Chroma collection that returns normalized records."""

    def __init__(self, collection):
        self.collection = collection

    def query(self, query_text: str, n_results: int = 3) -> list[dict[str, Any]]:
        """Query the collection and normalize the result into a flat list."""
        if self.collection is None or not query_text:
            return []

        raw_results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
        )

        if not raw_results or not raw_results.get("documents") or not raw_results["documents"][0]:
            return []

        docs = raw_results["documents"][0]
        metadatas = raw_results["metadatas"][0] if raw_results.get("metadatas") else [{}] * len(docs)
        ids = raw_results["ids"][0]

        formatted_results = []
        for doc, meta, doc_id in zip(docs, metadatas, ids):
            formatted_results.append(
                {
                    "source_id": doc_id,
                    "content": doc,
                    "metadata": meta or {},
                }
            )

        return formatted_results

    def count(self) -> int:
        if self.collection is None:
            return 0
        return self.collection.count()
