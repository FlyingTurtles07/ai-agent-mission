from fastapi import APIRouter, HTTPException

from models.schemas import DataItemCreate, DataItemUpdate, DataItemResponse, DataSummaryResponse
from services import firestore_service
from services.summary_service import calc_summary

router = APIRouter(prefix="/api/data", tags=["data"])


@router.post("", response_model=DataItemResponse)
def add_data(item: DataItemCreate):
    """새 데이터 추가"""
    # item.date는 Pydantic이 검증한 date 객체 -> Firestore/CSV와 같은 문자열 형식으로 저장
    created = firestore_service.create_data(item.date.isoformat(), item.value, item.memo or "")
    return created


@router.get("", response_model=list[DataItemResponse])
def get_data_list():
    """데이터 목록 조회"""
    return firestore_service.list_data()


@router.get("/summary", response_model=DataSummaryResponse)
def get_data_summary():
    """
    데이터 요약(프롬프트 주입용).
    주의: 라우트 순서상 이 엔드포인트는 반드시 '/{id}' 보다 위에 있어야 한다.
    """
    rows = firestore_service.list_data()
    return calc_summary(rows)


@router.put("/{data_id}", response_model=DataItemResponse)
def modify_data(data_id: str, item: DataItemUpdate):
    """데이터 수정"""
    updates = item.model_dump()
    if updates.get("date") is not None:
        updates["date"] = updates["date"].isoformat()
    try:
        updated = firestore_service.update_data(data_id, updates)
        return updated
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{data_id}")
def remove_data(data_id: str):
    """데이터 삭제"""
    try:
        firestore_service.delete_data(data_id)
        return {"result": "deleted", "id": data_id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))