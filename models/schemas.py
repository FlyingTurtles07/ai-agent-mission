from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date as DateType


# ---------- 데이터(시계열) 관련 스키마 ----------

class DataItemCreate(BaseModel):
    """POST /api/data 요청 바디"""
    date: DateType = Field(..., description="YYYY-MM-DD 형식의 실제 존재하는 날짜")
    value: int = Field(..., ge=0, description="해당 날짜의 서명 완료 건수 (0 이상)")
    memo: Optional[str] = Field("", description="특이사항 메모 (없으면 빈 문자열)")


class DataItemUpdate(BaseModel):
    """PUT /api/data/{id} 요청 바디 (부분 수정 허용)"""
    date: Optional[DateType] = None
    value: Optional[int] = Field(None, ge=0)
    memo: Optional[str] = None


class DataItemResponse(BaseModel):
    """데이터 조회/생성/수정 응답"""
    id: str
    date: str
    value: int
    memo: str


class DataSummaryResponse(BaseModel):
    """GET /api/data/summary 응답"""
    period: str
    count: int
    metrics: dict
    trend: str
    memo_day_count: int


# ---------- 대화 기록 관련 스키마 ----------

class Message(BaseModel):
    role: str = Field(..., description="'user' 또는 'assistant'")
    content: str


class ConversationCreate(BaseModel):
    """POST /api/conversations 요청 바디"""
    title: Optional[str] = Field(None, description="대화 제목 (없으면 첫 메시지로 자동 생성)")
    messages: List[Message] = Field(..., description="전체 대화 메시지 목록")


class ConversationSummary(BaseModel):
    """GET /api/conversations 목록 조회 시 각 항목"""
    id: str
    title: str
    created_at: str
    message_count: int


class ConversationDetail(BaseModel):
    """GET /api/conversations/{id} 상세 조회 응답"""
    id: str
    title: str
    created_at: str
    messages: List[Message]


# ---------- 챗봇 관련 스키마 ----------

class ChatRequest(BaseModel):
    """POST /api/chat 요청 바디"""
    message: str = Field(..., min_length=1, description="사용자 질문")
    conversation_id: Optional[str] = Field(
        None, description="이어서 대화할 conversation_id (없으면 새 대화 생성)"
    )


class ChatResponse(BaseModel):
    """POST /api/chat 응답"""
    reply: str
    conversation_id: str