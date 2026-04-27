from fastapi.testclient import TestClient

from TaoxinAI.main import app


client = TestClient(app)


def test_chat_api_accepts_case_input_contract():
    response = client.post(
        "/api/chat",
        json={
            "messages": [{"role": "user", "content": "\u516c\u53f8\u62d6\u6b20\u6211\u5de5\u8d44"}],
            "extracted_info": {
                "name": "\u5f20\u4e09",
                "work_location": "\u5317\u4eac",
                "_stage": "initial",
            },
            "case_type_hint": "taoxin",
        },
    )

    assert response.status_code == 200
    payload = response.json()

    assert payload["conversation_stage"] == "basic_facts"
    assert payload["extracted_info"]["name"] == "\u5f20\u4e09"
    assert payload["extracted_info"]["work_location"] == "\u5317\u4eac"
    assert payload["extracted_info"]["_stage"] == "basic_facts"
    assert payload["quick_replies"]


def test_chat_api_rejects_legacy_payload_shape():
    response = client.post(
        "/api/chat",
        json={
            "message": "\u516c\u53f8\u62d6\u6b20\u6211\u5de5\u8d44",
            "user_info": {
                "name": "\u5f20\u4e09",
                "work_location": "\u5317\u4eac",
                "_stage": "initial",
            },
        },
    )

    assert response.status_code == 422


def test_generate_document_docx_api_returns_word_file():
    response = client.post(
        "/api/generate-document-docx",
        json={
            "messages": [{"role": "user", "content": "\u516c\u53f8\u62d6\u6b20\u6211 8000 \u5143\u5de5\u8d44"}],
            "extracted_info": {
                "name": "\u5f20\u4e09",
                "employer_name": "\u67d0\u5efa\u8bbe\u5de5\u7a0b\u6709\u9650\u516c\u53f8",
                "has_arbitration": False,
            },
            "case_type_hint": "taoxin",
        },
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith(
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    assert "filename*=UTF-8''" in response.headers["content-disposition"]
    assert response.content[:2] == b"PK"
