from datetime import date, datetime


def _to_date(v):
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, date):
        return v
    return datetime.strptime(str(v)[:10], "%Y-%m-%d").date()


def moving_average_7d(items):
    """최근 7개 데이터 포인트 기준 이동평균 (7개 미만 구간은 None)."""
    rows = sorted(
        ({"date": _to_date(i["date"]), "value": float(i["value"])} for i in items),
        key=lambda r: r["date"],
    )
    out = []
    for idx, r in enumerate(rows):
        if idx >= 6:
            window = [x["value"] for x in rows[idx - 6: idx + 1]]
            ma = round(sum(window) / 7, 2)
        else:
            ma = None
        out.append({"date": r["date"].isoformat(), "value": r["value"], "ma7": ma})
    return out


def build_statistics(items):
    series = moving_average_7d(items)
    latest = next((r for r in reversed(series) if r["ma7"] is not None), None)
    return {
        "window": "최근 7개 데이터 포인트",
        "count": len(series),
        "latest_date": latest["date"] if latest else None,
        "latest_ma7": latest["ma7"] if latest else None,
        "series": series,
    }