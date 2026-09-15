"""
AI 모델 호출을 하나의 인터페이스로 통합한 모듈.
AI_MODEL_PROVIDER 환경변수 값("gemini" 또는 "openai")에 따라
실제로 호출하는 API만 바뀌고, 이 모듈을 사용하는 쪽(chat 라우터)의 코드는 바뀌지 않는다.
"""

import os


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


def ask_ai(system_prompt: str, user_message: str) -> str:
    """설정된 provider에 따라 실제 AI API를 호출하고 답변 텍스트를 반환한다."""
    # 미션 필수 요구사항이 OpenAI/GPT API이므로 기본값은 openai로 둔다.
    # 개발 중 비용 절감을 위해 .env에서 AI_MODEL_PROVIDER=gemini로 명시적으로 바꿔서 쓸 수 있다.
    provider = os.getenv("AI_MODEL_PROVIDER", "openai").lower()

    if provider == "gemini":
        return _ask_gemini(system_prompt, user_message)
    elif provider == "openai":
        return _ask_openai(system_prompt, user_message)
    else:
        raise ValueError(
            f"알 수 없는 AI_MODEL_PROVIDER 값입니다: '{provider}' "
            "('gemini' 또는 'openai'만 사용 가능)"
        )


def _ask_gemini(system_prompt: str, user_message: str) -> str:
    import google.generativeai as genai

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY 환경변수가 설정되어 있지 않습니다.")
    genai.configure(api_key=api_key)

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=system_prompt,
    )
    response = model.generate_content(user_message)
    return response.text


def _ask_openai(system_prompt: str, user_message: str) -> str:
    from openai import OpenAI

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY 환경변수가 설정되어 있지 않습니다.")
    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        max_tokens=1000,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
    )
    return response.choices[0].message.content