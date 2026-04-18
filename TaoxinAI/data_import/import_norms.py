from pathlib import Path
import docx
import chromadb
import uuid
import re

LEGACY_BACKEND_DIR = Path(__file__).resolve().parents[2] / "huxin_backend"
DB_PATH = LEGACY_BACKEND_DIR / "legal_db"

def get_legacy_norm_source() -> Path:
    """Returns the legacy wage-recovery norm document path."""
    return LEGACY_BACKEND_DIR / "法条适用.docx"

def import_norms_to_db():
    file_path = get_legacy_norm_source()
    if not file_path.exists():
        print(f"❌ 找不到法条文件: {file_path}")
        return

    print("⏳ 开始解析法条 Word 文档...")
    doc = docx.Document(file_path)
    
    client = chromadb.PersistentClient(path=str(DB_PATH))
    collection = client.get_or_create_collection(name="laws")
    
    docs, metadatas, ids = [], [], []
    current_article = []
    article_title = "未知法规"
    
    # 简易启发式解析：遇到 "第XX条" 就认为是一条新的法条
    article_pattern = re.compile(r'^第[一二三四五六七八九十百千万\d]+条')

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
            
        if article_pattern.match(text):
            # 保存上一条法条
            if current_article:
                full_text = "\n".join(current_article)
                docs.append(full_text)
                metadatas.append({
                    "source_type": "norm",
                    "title": article_title,
                    "article_no": current_article[0][:15] # 取法条开头做摘要
                })
                ids.append(f"norm_{uuid.uuid4().hex[:8]}")
            # 开始新法条
            current_article = [text]
        else:
            # 判断是否是法律名称标题 (比如《中华人民共和国劳动法》)
            if "《" in text and "》" in text and len(text) < 30:
                article_title = text
            current_article.append(text)

    # 保存最后一条
    if current_article:
        docs.append("\n".join(current_article))
        metadatas.append({"source_type": "norm", "title": article_title})
        ids.append(f"norm_{uuid.uuid4().hex[:8]}")

    if docs:
        print(f"📥 正在将 {len(docs)} 条法条写入向量库...")
        collection.add(documents=docs, metadatas=metadatas, ids=ids)
        print("✅ 法条入库完成！")

if __name__ == "__main__":
    import_norms_to_db()
