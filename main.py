import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()  # .env 파일의 환경변수를 읽어온다

from routers import data, conversations, chat  # noqa: E402  (load_dotenv 이후에 import)

app = FastAPI(
    title="AI 데이터 비서 API",
    description="시계열 데이터를 분석하고, 요약을 기반으로 대화하는 AI 비서 API",
    version="1.0.0",
)

# CORS 설정: ALLOWED_ORIGINS 환경변수를 콤마로 구분해서 리스트로 변환
allowed_origins_raw = os.getenv("ALLOWED_ORIGINS", "*")
allowed_origins = (
    ["*"] if allowed_origins_raw.strip() == "*"
    else [origin.strip() for origin in allowed_origins_raw.split(",")]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(data.router)
app.include_router(conversations.router)
app.include_router(chat.router)


@app.get("/")
def root():
    """헬스체크 겸 콜드스타트 확인용 엔드포인트"""
    return {"status": "ok", "message": "AI 데이터 비서 API가 정상 동작 중입니다."}