"""
시계열 데이터(list of {date, value, memo})를 받아
2단계에서 확정한 형식의 요약 정보를 계산하는 모듈.

trend 계산 방식: 최근 60일 평균 vs 직전 60일 평균 (동일한 기간 길이로 비교)
"""

import statistics
from datetime import date, timedelta


def calc_summary(rows: list[dict]) -> dict:
    if not rows:
        return {
            "period": "데이터 없음",
            "count": 0,
            "metrics": {"average": 0, "max": 0, "min": 0, "std_dev": 0},
            "trend": "데이터 없음",
            "memo_day_count": 0,
        }

    rows_sorted = sorted(rows, key=lambda r: r["date"])
    values = [r["value"] for r in rows_sorted]

    period_start = rows_sorted[0]["date"]
    period_end = rows_sorted[-1]["date"]
    count = len(rows_sorted)
    average = round(sum(values) / count, 1)
    max_v = max(values)
    min_v = min(values)
    std_dev = round(statistics.pstdev(values), 1) if count > 1 else 0.0

    end_date = date.fromisoformat(period_end)
    recent_cutoff = end_date - timedelta(days=60)      # 최근 60일 시작점
    prev_cutoff = recent_cutoff - timedelta(days=60)    # 그 직전 60일 시작점

    recent_vals = [
        r["value"] for r in rows_sorted
        if date.fromisoformat(r["date"]) >= recent_cutoff
    ]
    prev_vals = [
        r["value"] for r in rows_sorted
        if prev_cutoff <= date.fromisoformat(r["date"]) < recent_cutoff
    ]

    if recent_vals and prev_vals:
        recent_avg = sum(recent_vals) / len(recent_vals)
        prev_avg = sum(prev_vals) / len(prev_vals)
        if prev_avg == 0:
            trend = "직전 60일 데이터가 0건이라 증감률을 계산할 수 없음"
        else:
            pct_change = round((recent_avg - prev_avg) / prev_avg * 100, 1)
            if pct_change > 0:
                word = "상승"
            elif pct_change < 0:
                word = "하락"
            else:
                word = "유지"
            trend = f"{word} (직전 60일 평균 대비 {pct_change:+.1f}%)"
    else:
        trend = "비교할 데이터가 충분하지 않음 (최근/직전 60일 중 데이터 없음)"

    memo_day_count = sum(1 for r in rows_sorted if r.get("memo", "").strip() != "")

    return {
        "period": f"{period_start} ~ {period_end}",
        "count": count,
        "metrics": {
            "average": average,
            "max": max_v,
            "min": min_v,
            "std_dev": std_dev,
        },
        "trend": trend,
        "memo_day_count": memo_day_count,
    }