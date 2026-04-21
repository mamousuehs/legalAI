import pytest
from pathlib import Path
from TaoxinAI.schemas.retrieval import RetrievedAuthority
from TaoxinAI.services.retrieval.law_retriever import LawRetriever
from TaoxinAI.services.retrieval.case_retriever import CaseRetriever
from TaoxinAI.services.retrieval.template_retriever import TemplateRetriever
from TaoxinAI.services.retrieval.reranker import Reranker

# ==========================================
# 1. 构造一个假的数据库仓储 (Mock Object)
# ==========================================
class MockChromaRepo:
    """模拟仓储层，避免在单元测试中真实连接 Chroma 数据库"""
    def query(self, query: str, n_results: int):
        # 故意混杂法条、案例和无效数据，用来测试 Retriever 的过滤能力
        return [
            {"source_id": "law_123", "content": "法条内容", "metadata": {"source_type": "norm", "title": "《劳动法》"}},
            {"source_id": "case_456", "content": "案例内容", "metadata": {"source_type": "case", "title": "张三讨薪案"}},
            {"source_id": "noise_789", "content": "干扰数据", "metadata": {"source_type": "unknown"}}
        ]

# ==========================================
# 2. 测试具体的召回器
# ==========================================
class TestRetrievers:
    def setup_method(self):
        """每个测试前，注入我们伪造的数据库"""
        self.mock_repo = MockChromaRepo()

    def test_law_retriever_filters_correctly(self):
        """测试法条召回器：必须准确过滤出 norm 类别，无视案例和干扰数据"""
        retriever = LawRetriever(self.mock_repo)
        results = retriever.retrieve("欠薪")
        
        assert len(results) == 1, "应该只召回 1 条法条数据"
        assert results[0].source_id == "law_123"
        assert results[0].source_type == "norm"
        assert results[0].title == "《劳动法》"

    def test_case_retriever_filters_correctly(self):
        """测试案例召回器：必须准确过滤出 case 类别"""
        retriever = CaseRetriever(self.mock_repo)
        results = retriever.retrieve("欠薪")
        
        assert len(results) == 1, "应该只召回 1 条案例数据"
        assert results[0].source_id == "case_456"
        assert results[0].source_type == "case"

class TestTemplateRetriever:
    def test_retrieve_yaml_templates_only(self, tmp_path):
        """
        利用 pytest 内置的 tmp_path 构造一个临时文件夹
        测试模板召回器是否只抓取 .yaml 文件
        """
        # 在临时目录里造两个假文件
        (tmp_path / "issue_templates.yaml").write_text("dummy content", encoding="utf-8")
        (tmp_path / "readme.txt").write_text("should be ignored", encoding="utf-8")
        
        retriever = TemplateRetriever(template_root=tmp_path)
        results = retriever.retrieve("需要争点模板")
        
        assert len(results) == 1, "只能召回 yaml 格式的模板文件"
        assert results[0].source_type == "template"
        assert results[0].title == "issue_templates.yaml"

# ==========================================
# 3. 测试重排器
# ==========================================
class TestReranker:
    def test_rerank_sorts_by_score_descending(self):
        """测试重排逻辑：必须按 score 从大到小排列"""
        # 故意打乱分数顺序
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
        assert ranked[0].title == "B", "最高分的文档必须排在第一位"
