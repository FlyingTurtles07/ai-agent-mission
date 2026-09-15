"""
Firestore 연동을 담당하는 모듈.
- 서비스 계정 키는 코드에 하드코딩하지 않고 환경변수(FIREBASE_SERVICE_ACCOUNT_JSON)에서 읽는다.
- 클라이언트는 앱이 실제로 DB를 사용할 때 한 번만 초기화한다 (lazy init).
"""

import os
import json
import uuid
from datetime import datetime, timezone

import firebase_admin
from firebase_admin import credentials, firestore

_db = None  # Firestore 클라이언트를 담아둘 전역 변수 (최초 1회만 생성)


def get_db():
    """Firestore 클라이언트를 반환한다. 최초 호출 시에만 초기화한다."""
    global _db
    if _db is not None:
        return _db

    if not firebase_admin._apps:
        service_account_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
        if not service_account_json:
            raise RuntimeError(
                "FIREBASE_SERVICE_ACCOUNT_JSON 환경변수가 설정되어 있지 않습니다. "
                ".env 파일을 확인하세요."
            )
        cred_dict = json.loads(service_account_json)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)

    _db = firestore.client()
    return _db


# ---------- data 컬렉션 (시계열 데이터) ----------

DATA_COLLECTION = "data"


def create_data(date: str, value: int, memo: str = "") -> dict:
    db = get_db()
    doc_id = str(uuid.uuid4())
    payload = {"date": date, "value": value, "memo": memo}
    db.collection(DATA_COLLECTION).document(doc_id).set(payload)
    return {"id": doc_id, **payload}


def list_data() -> list[dict]:
    db = get_db()
    docs = db.collection(DATA_COLLECTION).order_by("date").stream()
    return [{"id": d.id, **d.to_dict()} for d in docs]


def update_data(doc_id: str, updates: dict) -> dict:
    db = get_db()
    doc_ref = db.collection(DATA_COLLECTION).document(doc_id)
    if not doc_ref.get().exists:
        raise ValueError(f"id={doc_id} 데이터를 찾을 수 없습니다.")
    updates = {k: v for k, v in updates.items() if v is not None}
    doc_ref.update(updates)
    updated = doc_ref.get().to_dict()
    return {"id": doc_id, **updated}


def delete_data(doc_id: str) -> None:
    db = get_db()
    doc_ref = db.collection(DATA_COLLECTION).document(doc_id)
    if not doc_ref.get().exists:
        raise ValueError(f"id={doc_id} 데이터를 찾을 수 없습니다.")
    doc_ref.delete()


# ---------- conversations 컬렉션 (대화 기록) ----------

CONVERSATIONS_COLLECTION = "conversations"


def create_conversation(title: str, messages: list[dict]) -> dict:
    db = get_db()
    doc_id = str(uuid.uuid4())
    payload = {
        "title": title,
        "messages": messages,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    db.collection(CONVERSATIONS_COLLECTION).document(doc_id).set(payload)
    return {"id": doc_id, **payload}


def append_message(conversation_id: str, role: str, content: str) -> dict:
    """기존 대화에 메시지 1개를 추가한다 (챗봇 자동 저장용)."""
    db = get_db()
    doc_ref = db.collection(CONVERSATIONS_COLLECTION).document(conversation_id)
    snapshot = doc_ref.get()
    if not snapshot.exists:
        raise ValueError(f"id={conversation_id} 대화를 찾을 수 없습니다.")
    data = snapshot.to_dict()
    messages = data.get("messages", [])
    messages.append({"role": role, "content": content})
    doc_ref.update({"messages": messages})
    return {"id": conversation_id, **data, "messages": messages}


def list_conversations() -> list[dict]:
    db = get_db()
    docs = db.collection(CONVERSATIONS_COLLECTION).order_by(
        "created_at", direction=firestore.Query.DESCENDING
    ).stream()
    result = []
    for d in docs:
        data = d.to_dict()
        result.append({
            "id": d.id,
            "title": data.get("title", ""),
            "created_at": data.get("created_at", ""),
            "message_count": len(data.get("messages", [])),
        })
    return result


def get_conversation(conversation_id: str) -> dict:
    db = get_db()
    doc_ref = db.collection(CONVERSATIONS_COLLECTION).document(conversation_id)
    snapshot = doc_ref.get()
    if not snapshot.exists:
        raise ValueError(f"id={conversation_id} 대화를 찾을 수 없습니다.")
    data = snapshot.to_dict()
    return {"id": conversation_id, **data}


def delete_conversation(conversation_id: str) -> None:
    db = get_db()
    doc_ref = db.collection(CONVERSATIONS_COLLECTION).document(conversation_id)
    if not doc_ref.get().exists:
        raise ValueError(f"id={conversation_id} 대화를 찾을 수 없습니다.")
    doc_ref.delete()