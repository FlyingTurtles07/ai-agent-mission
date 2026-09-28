import json

TOOLS = [
    {"type": "function", "function": {
        "name": "get_data_summary",
        "description": "계약서 발송·서명 현황 데이터의 기간, 개수, 평균, 최대/최소, 추세 요약을 조회한다.",
        "parameters": {"type": "object", "properties": {}, "required": []},
    }},
    {"type": "function", "function": {
        "name": "get_data_statistics",
        "description": "일별 신규계약 건수의 최근 7일 이동평균 시계열과 최신 이동평균 값을 조회한다. 최근 흐름/추세 질문에 사용한다.",
        "parameters": {"type": "object", "properties": {}, "required": []},
    }},
    {"type": "function", "function": {
        "name": "list_conversations",
        "description": "저장된 이전 대화 목록(제목, 메시지 수, 생성일)을 최신순으로 조회한다.",
        "parameters": {"type": "object", "properties": {
            "limit": {"type": "integer", "description": "가져올 개수 (기본 10)"}
        }, "required": []},
    }},
    {"type": "function", "function": {
        "name": "get_conversation",
        "description": "특정 대화의 전체 메시지를 조회한다. 이전 대화 내용을 물었을 때 사용한다.",
        "parameters": {"type": "object", "properties": {
            "conversation_id": {"type": "string", "description": "대화 ID"}
        }, "required": ["conversation_id"]},
    }},
]

TOOL_GUIDE = (
    "\n\n[도구 사용 지침] 질문에 답하려면 더 자세한 정보가 필요할 때만 제공된 도구를 호출하세요. "
    "도구 결과에 없는 내용은 추정하거나 임의로 계산하지 말고, 알 수 없다고 답하세요."
)


def run_with_tools(client, model, messages, handlers, max_rounds=3):
    """도구 호출 루프. (최종 답변, 사용한 도구 목록) 반환."""
    used = []
    for _ in range(max_rounds):
        resp = client.chat.completions.create(model=model, messages=messages, tools=TOOLS)
        msg = resp.choices[0].message
        if not msg.tool_calls:
            return msg.content, used

        messages.append({
            "role": "assistant",
            "content": msg.content,
            "tool_calls": [
                {"id": tc.id, "type": "function",
                 "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                for tc in msg.tool_calls
            ],
        })
        for tc in msg.tool_calls:
            name = tc.function.name
            try:
                args = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}
            handler = handlers.get(name)
            try:
                result = handler(**args) if handler else {"error": f"알 수 없는 도구: {name}"}
            except Exception as e:
                result = {"error": str(e)}
            used.append({"name": name, "arguments": args})
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": json.dumps(result, ensure_ascii=False, default=str)[:6000],
            })

    resp = client.chat.completions.create(model=model, messages=messages)
    return resp.choices[0].message.content, used