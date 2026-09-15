from fastapi import APIRouter, HTTPException

from models.schemas import ChatRequest, ChatResponse
from services import firestore_service, ai_service
from services.summary_service import calc_summary

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(req: ChatRequest):
    """
    동작 흐름:
    1. 데이터 요약 조회
    2. 요약을 시스템 프롬프트에 삽입
    3. AI API 호출 (Gemini/OpenAI, AI_MODEL_PROVIDER로 분기)
    4. 대화 내용을 conversations에 저장 (자동 저장)
    """
    rows = firestore_service.list_data()
    summary = calc_summary(rows)
    system_prompt = ai_service.build_system_prompt(summary)

    try:
        reply = ai_service.ask_ai(system_prompt, req.message)
    except (RuntimeError, ValueError) as e:
        raise HTTPException(status_code=500, detail=f"AI 호출 실패: {e}")

    if req.conversation_id:
        try:
            firestore_service.append_message(req.conversation_id, "user", req.message)
            firestore_service.append_message(req.conversation_id, "assistant", reply)
            conversation_id = req.conversation_id
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
    else:
        created = firestore_service.create_conversation(
            title=req.message[:20],
            messages=[
                {"role": "user", "content": req.message},
                {"role": "assistant", "content": reply},
            ],
        )
        conversation_id = created["id"]

    return {"reply": reply, "conversation_id": conversation_id}