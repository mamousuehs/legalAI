from TaoxinAI.pipelines.case_analysis import CaseAnalysisPipeline
from TaoxinAI.schemas.common import Message
from TaoxinAI.schemas.intake import CaseInput


class DummyCollection:
    def __init__(self, records):
        self.records = records

    def query(self, query_texts, n_results=3):
        docs = [record["content"] for record in self.records[:n_results]]
        metas = [record["metadata"] for record in self.records[:n_results]]
        ids = [record["source_id"] for record in self.records[:n_results]]
        return {"documents": [docs], "metadatas": [metas], "ids": [ids]}

    def count(self):
        return len(self.records)


def test_pipeline_full_analysis_returns_issue_fact_match_chain():
    law_collection = DummyCollection(
        [
            {
                "source_id": "norm_1",
                "content": "劳动合同法相关条文",
                "metadata": {"source_type": "norm", "title": "劳动合同法第八十二条"},
            }
        ]
    )
    case_collection = DummyCollection(
        [
            {
                "source_id": "case_1",
                "content": "聊天记录和转账记录可证明事实劳动关系",
                "metadata": {"source_type": "case", "title": "事实劳动关系证据指引"},
            }
        ]
    )
    pipeline = CaseAnalysisPipeline(law_collection=law_collection, case_collection=case_collection, llm_client=None)
    case_input = CaseInput(
        messages=[
            Message(role="user", content="老板拖欠我3000元工资，没有合同，但我有聊天记录和转账记录。")
        ],
        extracted_info={"_stage": "analysis_ready"},
    )

    import asyncio

    result = asyncio.run(pipeline.run_full_analysis(case_input))

    assert result.issues
    assert result.facts
    assert result.element_matches
    assert result.irac_drafts
