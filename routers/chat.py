from fastapi import APIRouter, HTTPException

from models.schemas import ChatRequest, ChatResponse
from services import firestore_service, ai_service
from services.summary_service import calc_summary

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(req: ChatRequest):
    rows = firestore_service.list_data()
    summary = calc_summary(rows)
    system_prompt = ai_service.build_system_prompt(summary)

    history = []
    if req.conversation_id:
        try:
            conv = firestore_service.get_conversation(req.conversation_id)
            history = conv.get("messages", [])
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))

    try:
        reply = ai_service.ask_ai(system_prompt, req.message, history=history)
    except (RuntimeError, ValueError) as e:
        raise HTTPException(status_code=500, detail=f"AI 호출 실패: {e}")

    if req.conversation_id:
        firestore_service.append_message(req.conversation_id, "user", req.message)
        firestore_service.append_message(req.conversation_id, "assistant", reply)
        conversation_id = req.conversation_id
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