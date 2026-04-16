import shutil
from pathlib import Path

import chromadb
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from openai import AsyncOpenAI

from TaoxinAI.api.analyze import router as analyze_router
from TaoxinAI.api.chat import router as chat_router
from TaoxinAI.api.generate_document import router as generate_router
from TaoxinAI.pipelines.case_analysis import CaseAnalysisPipeline


BASE_DIR = Path(__file__).resolve().parent
LEGAL_DB_DIR = BASE_DIR / "legal_db"
LEGACY_BACKEND_DIR = BASE_DIR.parent / "huxin_backend"
LEGACY_LEGAL_DB_DIR = LEGACY_BACKEND_DIR / "legal_db"

app = FastAPI(title="TaoxinAI", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def build_llm_client() -> AsyncOpenAI:
    return AsyncOpenAI(
        base_url="http://127.0.0.1:11434/v1",
        api_key="ollama",
    )


def build_collection():
    _bootstrap_legacy_knowledge_base()
    chroma_client = chromadb.PersistentClient(path=str(LEGAL_DB_DIR))
    collection = chroma_client.get_or_create_collection(name="laws")

    if collection.count() == 0:
        collection.add(
            documents=[
                "《劳动合同法》第八十二条：用人单位自用工之日起超过一个月不满一年未与劳动者订立书面劳动合同的，应当向劳动者每月支付二倍的工资。",
                "【办案指引】在没有书面合同的情况下，微信聊天记录、转账记录、考勤打卡记录均可作为认定存在事实劳动关系的有效证据。",
            ],
            ids=["law_1", "case_1"],
        )

    return collection


def _bootstrap_legacy_knowledge_base() -> None:
    LEGAL_DB_DIR.mkdir(parents=True, exist_ok=True)
    has_local_data = any(LEGAL_DB_DIR.iterdir())
    has_legacy_data = LEGACY_LEGAL_DB_DIR.exists() and any(LEGACY_LEGAL_DB_DIR.iterdir())

    if has_local_data or not has_legacy_data:
        return

    for item in LEGACY_LEGAL_DB_DIR.iterdir():
        target = LEGAL_DB_DIR / item.name
        if target.exists():
            continue
        if item.is_dir():
            shutil.copytree(item, target)
        else:
            shutil.copy2(item, target)


llm_client = build_llm_client()
knowledge_collection = build_collection()
pipeline = CaseAnalysisPipeline(
    collection=knowledge_collection,
    llm_client=llm_client,
)

app.state.pipeline = pipeline

app.include_router(chat_router, prefix="/api", tags=["chat"])
app.include_router(analyze_router, prefix="/api", tags=["analysis"])
app.include_router(generate_router, prefix="/api", tags=["document"])


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "TaoxinAI"}
