from TaoxinAI.schemas.retrieval import RetrievedAuthority

class Reranker:
    """
    Score sorter for retrieved authorities.
    目前使用基础分数排序。未来这里可无缝接入 BGE-Reranker 等交叉编码器模型进行语义二次重排。
    """

    def rerank(self, items: list[RetrievedAuthority]) -> list[RetrievedAuthority]:
        if not items:
            return []
            
        # 按照 RetrievedAuthority 里的 score 属性从大到小降序排列
        return sorted(items, key=lambda item: item.score, reverse=True)
