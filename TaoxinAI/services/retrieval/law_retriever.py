import re

from TaoxinAI.schemas.retrieval import RetrievedAuthority


CITATION_PATTERN = re.compile(r"《[^》]+》第[一二三四五六七八九十百千万零〇\d]+条")
SOURCE_ID_PATTERN = re.compile(r"^(?:law|norm)_(\d+)$")
LAW_PREFIX = "【法律规范】"
RELEVANCE_KEYWORDS = {
    "工资": 0.45,
    "欠薪": 0.45,
    "拖欠": 0.4,
    "报酬": 0.25,
    "合同": 0.2,
    "劳动关系": 0.25,
    "仲裁": 0.2,
    "包工头": 0.2,
    "农民工": 0.2,
    "转账": 0.15,
    "考勤": 0.15,
    "证据": 0.15,
}


class LawRetriever:
    """Retrieves candidate legal norms from the norm collection."""

    def __init__(self, chroma_repo):
        self.chroma_repo = chroma_repo

    def retrieve(self, query: str, n_results: int = 3) -> list[RetrievedAuthority]:
        records = self.chroma_repo.query(query, n_results=n_results)
        items: list[RetrievedAuthority] = []

        for index, record in enumerate(records):
            source_id = record["source_id"]
            metadata = record.get("metadata", {})
            source_type = metadata.get("source_type")

            if source_type not in {"norm", "law"} and not source_id.startswith(("law", "norm")):
                continue

            title, snippet = self._build_authority_text(record)
            normalized_metadata = dict(metadata)
            if title:
                normalized_metadata["citation_title"] = title

            items.append(
                RetrievedAuthority(
                    source_type="norm",
                    source_id=source_id,
                    title=title or metadata.get("title") or source_id,
                    snippet=snippet[:200],
                    score=self._score_authority(query, title, snippet, index),
                    metadata=normalized_metadata,
                )
            )

        return self._deduplicate_by_title(items)

    def _build_authority_text(self, record: dict) -> tuple[str, str]:
        source_id = record["source_id"]
        metadata = record.get("metadata", {})
        current_text = self._clean_text(record.get("content", ""))

        title = self._resolve_title(source_id, metadata, current_text)
        anchor_index = self._resolve_anchor_index(source_id, current_text)
        snippet = self._build_snippet(anchor_index, current_text)

        if not snippet:
            snippet = current_text

        return title, snippet

    def _resolve_title(self, source_id: str, metadata: dict, current_text: str) -> str:
        metadata_title = (metadata.get("title") or "").strip()
        article_no = (metadata.get("article_no") or "").strip()

        if metadata_title and CITATION_PATTERN.search(metadata_title):
            return metadata_title

        if metadata_title and article_no and article_no not in metadata_title:
            return f"{metadata_title}{article_no}"

        current_citation = self._extract_citation(current_text)
        if current_citation:
            return current_citation

        nearby_citation = self._find_nearby_citation(source_id)
        if nearby_citation:
            return nearby_citation

        if metadata_title:
            return metadata_title

        return source_id

    def _resolve_anchor_index(self, source_id: str, current_text: str) -> int | None:
        source_index = self._parse_source_index(source_id)
        if source_index is None:
            return None

        if self._extract_citation(current_text):
            return source_index

        nearby_records = self._get_neighbor_records(source_index, backwards=8, forwards=2)
        for neighbor in reversed(nearby_records):
            if self._extract_citation(self._clean_text(neighbor.get("content", ""))):
                neighbor_index = self._parse_source_index(neighbor["source_id"])
                if neighbor_index is not None:
                    return neighbor_index

        return source_index

    def _build_snippet(self, anchor_index: int | None, current_text: str) -> str:
        if anchor_index is None:
            return current_text

        snippet_parts: list[str] = []
        forward_records = self._get_neighbor_records(anchor_index, backwards=0, forwards=4)
        seen_citation = False

        for record in forward_records:
            text = self._clean_text(record.get("content", ""))
            if not text:
                continue

            citation = self._extract_citation(text)
            if citation:
                if seen_citation:
                    break
                seen_citation = True
                continue

            snippet_parts.append(text)
            if len(snippet_parts) >= 2:
                break

        if current_text and current_text not in snippet_parts and not self._extract_citation(current_text):
            snippet_parts.append(current_text)

        return " ".join(self._deduplicate_texts(snippet_parts))

    def _find_nearby_citation(self, source_id: str) -> str | None:
        source_index = self._parse_source_index(source_id)
        if source_index is None:
            return None

        nearby_records = self._get_neighbor_records(source_index, backwards=8, forwards=2)
        for record in reversed(nearby_records):
            citation = self._extract_citation(self._clean_text(record.get("content", "")))
            if citation:
                return citation
        return None

    def _get_neighbor_records(self, source_index: int, backwards: int, forwards: int) -> list[dict]:
        if not hasattr(self.chroma_repo, "get_by_ids"):
            return []

        start = max(0, source_index - backwards)
        ids = [f"law_{index}" for index in range(start, source_index + forwards + 1)]
        records = self.chroma_repo.get_by_ids(ids)
        records_by_id = {record["source_id"]: record for record in records}
        ordered_records = []

        for doc_id in ids:
            if doc_id in records_by_id:
                ordered_records.append(records_by_id[doc_id])

        return ordered_records

    def _deduplicate_by_title(self, items: list[RetrievedAuthority]) -> list[RetrievedAuthority]:
        deduped: dict[str, RetrievedAuthority] = {}

        for item in items:
            existing = deduped.get(item.title)
            if existing is None:
                deduped[item.title] = item
                continue

            merged_snippets = self._deduplicate_texts([existing.snippet, item.snippet])[:2]
            existing.snippet = " ".join(merged_snippets)[:200]
            existing.score = max(existing.score, item.score)

        return list(deduped.values())

    def _parse_source_index(self, source_id: str) -> int | None:
        match = SOURCE_ID_PATTERN.match(source_id)
        if not match:
            return None
        return int(match.group(1))

    def _score_authority(self, query: str, title: str, snippet: str, index: int) -> float:
        base_score = max(0.1, 1.0 - index * 0.1)
        combined_text = f"{title} {snippet}"
        relevance_boost = 0.0

        for keyword, weight in RELEVANCE_KEYWORDS.items():
            if keyword in query and keyword in combined_text:
                relevance_boost += weight

        return base_score + relevance_boost

    def _extract_citation(self, text: str) -> str | None:
        match = CITATION_PATTERN.search(text)
        return match.group(0) if match else None

    def _clean_text(self, text: str) -> str:
        normalized = text.strip()
        if normalized.startswith(LAW_PREFIX):
            normalized = normalized[len(LAW_PREFIX):].strip()
        return normalized

    def _deduplicate_texts(self, texts: list[str]) -> list[str]:
        unique_texts: list[str] = []
        for text in texts:
            normalized = text.strip()
            if normalized and normalized not in unique_texts:
                unique_texts.append(normalized)
        return unique_texts
