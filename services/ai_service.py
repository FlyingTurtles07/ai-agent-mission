"""
AI 서비스 모듈: 코디세이 공개 API(OpenAI 호환 엔드포인트)로 AI를 호출한다.

필요한 환경변수(.env):
- CODYSSEY_API_KEY  : 코디세이에서 발급받은 키 (필수)
- CODYSSEY_BASE_URL : 코디세이 OpenAI 호환 주소 (선택, 기본값: https://copa.codyssey.kr/v1)
- AI_MODEL          : 코디세이 모델 ID (선택, 기본값: gpt-5-mini)

chat 라우터는 ask_ai()의 실패를 RuntimeError/ValueError로만 처리하므로,
이 모듈의 모든 실패는 RuntimeError로 통일해서 던진다.
"""

import os

DEFAULT_CODYSSEY_BASE_URL = "https://copa.codyssey.kr/v1"
DEFAULT_MODEL = "gpt-5-mini"


def build_system_prompt(summary: dict) -> str:
    """데이터 요약(dict)을 받아 시스템 프롬프트 문자열로 변환한다 (컨텍스트 주입)."""
    metrics = summary["metrics"]
    return (
        "당신은 데이터 분석 비서입니다.\n\n"
        "[사용자 데이터 요약]\n"
        f"- 데이터 기간: {summary['period']}\n"
        f"- 총 레코드: {summary['count']}개\n"
        f"- 주요 지표: 평균 {metrics['average']}건, 최대 {metrics['max']}건, "
        f"최소 {metrics['min']}건, 표준편차 {metrics['std_dev']}\n"
        f"- 최근 트렌드: {summary['trend']}\n"
        f"- 특이일(메모 있는 날) 수: {summary['memo_day_count']}일\n\n"
        "위에 제공된 수치만 근거로 답변하세요.\n"
        "제공되지 않은 세부 날짜별 수치나 통계는 절대로 지어내지 마세요.\n"
        "모르는 내용은 \"현재 요약 정보에는 없는 내용입니다\"라고 답하세요."
    )


def ask_ai(system_prompt: str, user_message: str, history: list[dict] | None = None) -> str:
    """코디세이(OpenAI 호환 엔드포인트)로 채팅 요청을 보내고 답변 텍스트를 반환한다."""
    from openai import OpenAI, OpenAIError

    api_key = (os.getenv("CODYSSEY_API_KEY") or "").strip()
    if not api_key:
        raise RuntimeError("CODYSSEY_API_KEY 환경변수가 설정되어 있지 않습니다.")

    base_url = (os.getenv("CODYSSEY_BASE_URL") or DEFAULT_CODYSSEY_BASE_URL).strip()
    model = (os.getenv("AI_MODEL") or DEFAULT_MODEL).strip()

    client = OpenAI(api_key=api_key, base_url=base_url)

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend({"role": h["role"], "content": h["content"]} for h in (history or []))
    messages.append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
        )
    except OpenAIError as e:
        raise RuntimeError(f"코디세이 API 호출 실패 (model={model}): {e}") from e

    if not response.choices or not response.choices[0].message.content:
        raise RuntimeError(f"AI가 빈 응답을 반환했습니다. (model={model})")
    return response.choices[0].message.content