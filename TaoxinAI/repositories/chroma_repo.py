class ChromaRepository:
    """Thin wrapper placeholder for Chroma access."""

    def __init__(self, collection):
        self.collection = collection

    def query(self, query_text: str, n_results: int = 3):
        return self.collection.query(query_texts=[query_text], n_results=n_results)

    def count(self) -> int:
        return self.collection.count()
