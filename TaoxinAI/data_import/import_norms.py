from pathlib import Path
import re
import uuid

import chromadb
import docx


TAOXIN_ROOT = Path(__file__).resolve().parents[1]
LEGACY_BACKEND_DIR = TAOXIN_ROOT.parent / "huxin_backend"
DB_PATH = TAOXIN_ROOT / "legal_db"


def get_legacy_norm_source() -> Path:
    """Return the first docx source under the legacy backend directory."""
    exact = LEGACY_BACKEND_DIR / "法条适用.docx"
    if exact.exists():
        return exact

    candidates = sorted(LEGACY_BACKEND_DIR.glob("*.docx"))
    if not candidates:
        raise FileNotFoundError("No .docx norm source found under huxin_backend")
    return candidates[0]


def import_norms_to_db() -> int:
    file_path = get_legacy_norm_source()
    doc = docx.Document(file_path)

    client = chromadb.PersistentClient(path=str(DB_PATH))
    collection = client.get_or_create_collection(name="laws")

    docs, metadatas, ids = [], [], []
    current_article = []
    article_title = "讨薪规范材料"
    article_pattern = re.compile(r"^第[一二三四五六七八九十百千万\d]+条")

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue

        if article_pattern.match(text):
            if current_article:
                full_text = "\n".join(current_article)
                docs.append(full_text)
                metadatas.append(
                    {
                        "source_type": "norm",
                        "title": article_title,
                        "article_no": current_article[0][:20],
                    }
                )
                ids.append(f"norm_{uuid.uuid4().hex[:8]}")
            current_article = [text]
        else:
            if "《" in text and "》" in text and len(text) < 40:
                article_title = text
            if not current_article:
                current_article = [text]
            else:
                current_article.append(text)

    if current_article:
        docs.append("\n".join(current_article))
        metadatas.append(
            {
                "source_type": "norm",
                "title": article_title,
                "article_no": current_article[0][:20],
            }
        )
        ids.append(f"norm_{uuid.uuid4().hex[:8]}")

    if docs:
        collection.add(documents=docs, metadatas=metadatas, ids=ids)
    return len(docs)


if __name__ == "__main__":
    count = import_norms_to_db()
    print(f"imported norms: {count}")
