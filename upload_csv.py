"""
CSV 파일의 시계열 데이터를 Firestore 'data' 컬렉션에 일괄 업로드하는 스크립트.
실행 방법 (프로젝트 루트에서): python upload_csv.py 데이터파일경로.csv
"""
import sys
import csv

from dotenv import load_dotenv
load_dotenv()

from services import firestore_service


def upload_csv(csv_path: str) -> None:
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    total = len(rows)
    if total == 0:
        print("CSV에 데이터가 없습니다.")
        return

    print(f"총 {total}개 데이터를 Firestore에 업로드합니다...")

    success = 0
    failed = []
    for i, row in enumerate(rows, start=1):
        date = (row.get("date") or "").strip()
        value_raw = (row.get("value") or "").strip()
        memo = (row.get("memo") or "").strip()

        if not date or value_raw == "":
            failed.append((i, row, "date 또는 value가 비어 있음"))
            continue

        try:
            value = int(value_raw)
        except ValueError:
            failed.append((i, row, f"value를 정수로 변환 불가: {value_raw}"))
            continue

        try:
            firestore_service.create_data(date, value, memo)
            success += 1
            print(f"[{i}/{total}] 저장 완료: {date} (value={value})")
        except Exception as e:
            failed.append((i, row, str(e)))

    print("\n=== 업로드 결과 ===")
    print(f"성공: {success}개 / 전체: {total}개")
    if failed:
        print(f"실패: {len(failed)}개")
        for idx, row, reason in failed:
            print(f"  - {idx}번째 행 {row}: {reason}")
    else:
        print("실패한 행 없음.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python upload_csv.py <csv파일경로>")
        sys.exit(1)
    upload_csv(sys.argv[1])
