from TaoxinAI.schemas.retrieval import RetrievedAuthority
from TaoxinAI.services.retrieval.case_retriever import CaseRetriever
from TaoxinAI.services.retrieval.law_retriever import LawRetriever
from TaoxinAI.services.retrieval.reranker import Reranker
from TaoxinAI.services.retrieval.template_retriever import TemplateRetriever


class MockChromaRepo:
    def query(self, query: str, n_results: int):
        return [
            {"source_id": "law_123", "content": "法条内容", "metadata": {"source_type": "norm", "title": "《劳动法》"}},
            {"source_id": "case_456", "content": "案例内容", "metadata": {"source_type": "case", "title": "张三讨薪案"}},
            {"source_id": "noise_789", "content": "干扰数据", "metadata": {"source_type": "unknown"}},
        ]

    def get_by_ids(self, ids):
        return []


class MockLawContextRepo:
    def query(self, query: str, n_results: int):
        return [
            {"source_id": "law_123", "content": "【法律规范】分包或者转包欠钱，总包清偿后向责任人追偿。", "metadata": {}},
            {"source_id": "law_124", "content": "【法律规范】分包单位拖欠农民工工资的，由施工总承包单位先行清偿，再依法追偿。", "metadata": {}},
        ]

    def get_by_ids(self, ids):
        record_map = {
            "law_122": {"source_id": "law_122", "content": "【法律规范】《保障农民工工资支付条例》第三十条", "metadata": {}},
            "law_123": {"source_id": "law_123", "content": "【法律规范】分包或者转包欠钱，总包清偿后向责任人追偿。", "metadata": {}},
            "law_124": {"source_id": "law_124", "content": "【法律规范】分包单位拖欠农民工工资的，由施工总承包单位先行清偿，再依法追偿。", "metadata": {}},
        }
        return [record_map[doc_id] for doc_id in ids if doc_id in record_map]


class TestRetrievers:
    def setup_method(self):
        self.mock_repo = MockChromaRepo()

    def test_law_retriever_filters_correctly(self):
        retriever = LawRetriever(self.mock_repo)
        results = retriever.retrieve("欠薪")

        assert len(results) == 1
        assert results[0].source_id == "law_123"
        assert results[0].source_type == "norm"
        assert results[0].title == "《劳动法》"

    def test_law_retriever_infers_citation_and_merges_duplicate_rows(self):
        retriever = LawRetriever(MockLawContextRepo())
        results = retriever.retrieve("欠薪")

        assert len(results) == 1
        assert results[0].title == "《保障农民工工资支付条例》第三十条"
        assert "施工总承包单位先行清偿" in results[0].snippet

    def test_case_retriever_filters_correctly(self):
        retriever = CaseRetriever(self.mock_repo)
        results = retriever.retrieve("欠薪")

        assert len(results) == 1
        assert results[0].source_id == "case_456"
        assert results[0].source_type == "case"


class TestTemplateRetriever:
    def test_retrieve_yaml_templates_only(self, tmp_path):
        (tmp_path / "issue_templates.yaml").write_text("dummy content", encoding="utf-8")
        (tmp_path / "readme.txt").write_text("should be ignored", encoding="utf-8")

        retriever = TemplateRetriever(template_root=tmp_path)
        results = retriever.retrieve("需要争点模板")

        assert len(results) == 1
        assert results[0].source_type == "template"
        assert results[0].title == "issue_templates.yaml"


class TestReranker:
    def test_rerank_sorts_by_score_descending(self):
        items = [
            RetrievedAuthority(source_type="norm", source_id="1", title="A", snippet="", score=0.5),
            RetrievedAuthority(source_type="norm", source_id="2", title="B", snippet="", score=0.9),
            RetrievedAuthority(source_type="norm", source_id="3", title="C", snippet="", score=0.2),
        ]

        reranker = Reranker()
        ranked = reranker.rerank(items)

        assert ranked[0].score == 0.9
        assert ranked[1].score == 0.5
        assert ranked[2].score == 0.2
        assert ranked[0].title == "B"
