from pathlib import Path
import uuid

import chromadb
import pandas as pd


TAOXIN_ROOT = Path(__file__).resolve().parents[1]
LEGACY_BACKEND_DIR = TAOXIN_ROOT.parent / "huxin_backend"
DB_PATH = TAOXIN_ROOT / "legal_db"


def get_legacy_case_source() -> Path:
    """Return the first xlsx source under the legacy backend directory."""
    exact = LEGACY_BACKEND_DIR / "涉欠薪典型案例汇总.xlsx"
    if exact.exists():
        return exact

    candidates = sorted(LEGACY_BACKEND_DIR.glob("*.xlsx"))
    if not candidates:
        raise FileNotFoundError("No .xlsx case source found under huxin_backend")
    return candidates[0]


def import_cases_to_db() -> int:
    file_path = get_legacy_case_source()
    df = pd.read_excel(file_path).fillna("")

    client = chromadb.PersistentClient(path=str(DB_PATH))
    collection = client.get_or_create_collection(name="cases")

    docs, metadatas, ids = [], [], []

    for index, row in df.iterrows():
        title = str(row.get("标题", f"案例_{index}"))
        content = str(row.get("案情摘要", "")) or str(row.to_dict())
        docs.append(content)
        metadatas.append(
            {
                "source_type": "case",
                "title": title,
                "court": str(row.get("法院", "未知法院")),
                "result": str(row.get("裁判结果", "未知结果")),
            }
        )
        ids.append(f"case_{uuid.uuid4().hex[:8]}")

    if docs:
        collection.add(documents=docs, metadatas=metadatas, ids=ids)
    return len(docs)


if __name__ == "__main__":
    count = import_cases_to_db()
    print(f"imported cases: {count}")
