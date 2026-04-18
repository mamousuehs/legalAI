from pathlib import Path
import pandas as pd
import chromadb
import uuid

LEGACY_BACKEND_DIR = Path(__file__).resolve().parents[2] / "huxin_backend"
DB_PATH = LEGACY_BACKEND_DIR / "legal_db"

def get_legacy_case_source() -> Path:
    """Returns the legacy wage-recovery case spreadsheet path."""
    return LEGACY_BACKEND_DIR / "涉欠薪典型案例汇总.xlsx"

def import_cases_to_db():
    file_path = get_legacy_case_source()
    if not file_path.exists():
        print(f"❌ 找不到案例文件: {file_path}")
        return

    print("⏳ 开始读取案例 Excel...")
    # 读取 Excel 并将空值填充为空字符串
    df = pd.read_excel(file_path).fillna("")
    
    client = chromadb.PersistentClient(path=str(DB_PATH))
    # 创建或获取 cases 集合
    collection = client.get_or_create_collection(name="cases")
    
    docs, metadatas, ids = [], [], []
    
    for index, row in df.iterrows():
        # 假设 Excel 有这些常见的列，如果没有会自动跳过（这里作防御性提取）
        title = str(row.get('标题', f'案例_{index}'))
        content = str(row.get('案情摘要', row.to_dict())) # 如果没有摘要列，就把整行转成字符串
        
        docs.append(content)
        # ChromaDB 的 metadata 值只能是 str, int, float, bool
        metadatas.append({
            "source_type": "case",
            "title": title,
            "court": str(row.get('法院', '未知法院')),
            "result": str(row.get('裁判结果', '未知结果'))
        })
        ids.append(f"case_{uuid.uuid4().hex[:8]}")

    if docs:
        print(f"📥 正在将 {len(docs)} 条案例写入向量库...")
        collection.add(documents=docs, metadatas=metadatas, ids=ids)
        print("✅ 案例入库完成！")

if __name__ == "__main__":
    import_cases_to_db()
