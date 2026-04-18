from typing import List, Dict, Any

class ChromaRepository:
    """Thin wrapper placeholder for Chroma access."""

    def __init__(self, collection):
        self.collection = collection

    def query(self, query_text: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """执行查询并将原生复杂结果清洗为标准字典列表"""
        raw_results = self.collection.query(
            query_texts=[query_text], 
            n_results=n_results
        )
        
        formatted_results = []
        # 防呆检查：如果没查到东西
        if not raw_results or not raw_results.get('documents') or not raw_results['documents'][0]:
            return formatted_results
            
        docs = raw_results['documents'][0]
        # 如果没有元数据，为了不报错塞入空字典
        metadatas = raw_results['metadatas'][0] if raw_results.get('metadatas') else [{}] * len(docs)
        ids = raw_results['ids'][0]
        
        # 将分离的数组拉平组合在一起
        for doc, meta, doc_id in zip(docs, metadatas, ids):
            formatted_results.append({
                "source_id": doc_id,
                "content": doc,
                "metadata": meta
            })
            
        return formatted_results

    def count(self) -> int:
        return self.collection.count()
