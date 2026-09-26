# 📊 AI Agent Mission — 나만의 AI 비서

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-black?logo=fastapi)
![Firebase](https://img.shields.io/badge/Firestore-FFCA28?logo=firebase&logoColor=black)
![OpenAI](https://img.shields.io/badge/OpenAI%20Compatible-412991?logo=openai&logoColor=white)
![Vercel](https://img.shields.io/badge/Frontend-Vercel-black?logo=vercel)
![Render](https://img.shields.io/badge/Backend-Render-46E3B7?logo=render&logoColor=white)

시계열 데이터(계약서 발송·서명 현황)를 분석해 요약 정보를 생성하고, 이를 시스템 프롬프트에 주입해 대화하는 AI 비서 웹 서비스입니다. FastAPI 백엔드와 바닐라 HTML/CSS/JS 프론트엔드로 구성되어 있으며, 데이터는 Firebase Firestore에 저장하고 대화 응답은 OpenAI 호환 API를 통해 생성합니다.

## ✨ 주요 기능

- **AI 챗봇**: 계약서 발송·서명 현황 데이터 요약을 컨텍스트로 주입해 질문에 답변, 대화 history 유지
- **데이터 관리(CRUD)**: 날짜별 신규계약 건수 데이터 조회/등록/수정/삭제
- **대화기록 관리**: 대화 목록 조회, 상세 로그 확인, 삭제

## 🛠 기술 스택

| 구분 | 기술 |
|---|---|
| 백엔드 | FastAPI, Python 3.12 |
| 데이터베이스 | Firebase Firestore |
| AI | OpenAI 호환 API (코디세이, gpt-5-mini) |
| 프론트엔드 | HTML / CSS / Vanilla JS |
| 배포 | 백엔드 Render, 프론트엔드 Vercel |

## 📁 폴더 구조

```
ai-agent-mission/
├── main.py                # FastAPI 엔트리포인트
├── routers/
│   ├── data.py             # 데이터 CRUD 라우터
│   └── chat.py             # 대화기록 + 챗봇 라우터
├── services/
│   └── ai_service.py        # AI 호출 및 컨텍스트 구성 로직
├── requirements.txt
├── requirements.lock.txt
└── frontend/
    ├── index.html           # 챗봇 화면
    ├── data.html            # 데이터 관리 화면
    ├── history.html          # 대화기록 화면
    ├── css/style.css
    └── js/
        ├── config.js
        ├── api.js
        ├── chat.js
        ├── data.js
        └── history.js
```

## 🚀 설치 및 실행 방법

### 백엔드

```bash
git clone https://github.com/FlyingTurtles07/ai-agent-mission.git
cd ai-agent-mission

python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.lock.txt

# .env 파일 작성 후 (아래 환경변수 안내 참고)
python -m uvicorn main:app --reload
```

Swagger UI 확인: `http://127.0.0.1:8000/docs`

### 프론트엔드

```bash
cd frontend
python -m http.server 5500
```

브라우저에서 `http://127.0.0.1:5500` 접속 (로컬 실행 시 `js/config.js`가 자동으로 `http://127.0.0.1:8000` 백엔드를 바라봅니다.)

## 🔑 환경변수 (.env)

```env
FIREBASE_CREDENTIALS_JSON=<Firebase 서비스 계정 JSON 내용 또는 경로>
CODYSSEY_API_KEY=<코디세이 발급 API 키>
CODYSSEY_BASE_URL=<코디세이 OpenAI 호환 base url>
AI_MODEL=gpt-5-mini
```

## 📡 API 명세

### 데이터 CRUD

| 메서드 | 경로 | 설명 |
|---|---|---|
| GET | `/api/data` | 전체 데이터 목록 조회 |
| GET | `/api/data/summary` | 데이터 요약 통계 조회 (count, 평균, 표준편차 등) |
| POST | `/api/data` | 데이터 등록 |
| PUT | `/api/data/{id}` | 데이터 수정 |
| DELETE | `/api/data/{id}` | 데이터 삭제 |

### 대화기록

| 메서드 | 경로 | 설명 |
|---|---|---|
| POST | `/api/conversations` | 새 대화 생성 |
| GET | `/api/conversations` | 대화 목록 조회 (내림차순) |
| GET | `/api/conversations/{id}` | 대화 상세(메시지 로그) 조회 |
| DELETE | `/api/conversations/{id}` | 대화 삭제 |

### 챗봇

| 메서드 | 경로 | 설명 |
|---|---|---|
| POST | `/api/chat` | 메시지 전송, 데이터 요약 컨텍스트 주입 후 AI 응답 반환 |

## ☁️ 배포 정보

- **백엔드**: Render — `https://ai-agent-mission.onrender.com`
- **프론트엔드**: Vercel — `ai-agent-mission.vercel.app` <br/> 저장소 루트가 아닌 `frontend` 폴더를 Root Directory로 지정해 정적 배포
- Vercel 배포 시 Framework Preset은 **Other**로 설정 (Python 백엔드 코드 자동 감지 방지)
```

---

## 테스트표 (10단계)

| # | 항목 | 확인 방법 | 기대 결과 |
|---|---|---|---|
| 1 | 뱃지 렌더링 | GitHub 저장소에서 README.md 미리보기 | 6개 뱃지 정상 표시 |
| 2 | 코드블록/표 렌더링 | 마크다운 미리보기 | 설치 명령어, API 표 깨짐 없이 표시 |
| 3 | 폴더 구조 일치 | 실제 저장소 구조와 비교 | README와 실제 구조 동일 |
| 4 | 설치 가이드 재현 | 새 환경에서 README만 보고 따라해보기 | venv 생성부터 서버 실행까지 문제없이 진행 |
| 5 | API 명세 정확성 | 실제 Swagger UI(/docs)와 대조 | 경로/메서드 일치 |

저장소에 `README.md`로 저장하시고, 1~5번 확인해서 알려주시면 최종 검증표까지 정리하고 미션 마무리할게요.
