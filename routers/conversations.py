from fastapi import APIRouter, HTTPException

from models.schemas import ConversationCreate, ConversationSummary, ConversationDetail
from services import firestore_service

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


@router.post("", response_model=ConversationDetail)
def save_conversation(conv: ConversationCreate):
    """대화 저장 (수동 저장용. 챗봇 사용 시에는 /api/chat이 자동 저장한다)"""
    title = conv.title or (conv.messages[0].content[:20] if conv.messages else "새 대화")
    messages = [m.model_dump() for m in conv.messages]
    created = firestore_service.create_conversation(title, messages)
    return created


@router.get("", response_model=list[ConversationSummary])
def get_conversation_list():
    """대화 목록 조회 (messages 본문은 포함하지 않음 - 목록은 가볍게)"""
    return firestore_service.list_conversations()


@router.get("/{conversation_id}", response_model=ConversationDetail)
def get_conversation_detail(conversation_id: str):
    """특정 대화의 전체 messages 조회 (대화 불러오기 UX용)"""
    try:
        return firestore_service.get_conversation(conversation_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{conversation_id}")
def remove_conversation(conversation_id: str):
    """대화 삭제"""
    try:
        firestore_service.delete_conversation(conversation_id)
        return {"result": "deleted", "id": conversation_id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))