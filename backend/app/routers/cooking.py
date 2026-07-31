from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.cooking import CookingRecord, CookingStep
from app.schemas.cooking import CookingRecordCreate, CookingRecordUpdate, CookingStepUpdate, CookingRecordInDB

router = APIRouter(prefix="/cooking-records", tags=["烹饪记录"])


@router.post("", response_model=CookingRecordInDB)
def create_record(req: CookingRecordCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    import json
    dishes_json = json.dumps(req.dish_ids)
    record = CookingRecord(user_id=current_user.id, dishes_json=dishes_json)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("", response_model=list[CookingRecordInDB])
def list_records(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    records = db.query(CookingRecord).filter(CookingRecord.user_id == current_user.id).order_by(CookingRecord.created_at.desc()).all()
    return records


@router.get("/{record_id}", response_model=CookingRecordInDB)
def get_record(record_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    record = db.query(CookingRecord).filter(CookingRecord.id == record_id, CookingRecord.user_id == current_user.id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    return record


@router.put("/{record_id}", response_model=CookingRecordInDB)
def update_record(record_id: int, req: CookingRecordUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    record = db.query(CookingRecord).filter(CookingRecord.id == record_id, CookingRecord.user_id == current_user.id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    if req.status is not None:
        record.status = req.status
    if req.buy_list is not None:
        record.buy_list = req.buy_list
    if req.prep_steps is not None:
        record.prep_steps = req.prep_steps
    if req.cook_steps is not None:
        record.cook_steps = req.cook_steps
    db.commit()
    db.refresh(record)
    return record


@router.post("/{record_id}/steps", response_model=list[dict])
def create_steps(record_id: int, steps: list[dict], db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    record = db.query(CookingRecord).filter(CookingRecord.id == record_id, CookingRecord.user_id == current_user.id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    db_steps = []
    for i, s in enumerate(steps):
        step = CookingStep(
            record_id=record.id,
            title=s.get("title"),
            detail=s.get("detail"),
            timer_minutes=s.get("timer_minutes"),
            sort_order=i,
        )
        db.add(step)
        db_steps.append(step)
    db.commit()
    return [{"id": s.id, "title": s.title, "detail": s.detail, "timer_minutes": s.timer_minutes} for s in db_steps]


@router.put("/steps/{step_id}")
def update_step(step_id: int, req: CookingStepUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    step = db.query(CookingStep).join(CookingRecord).filter(CookingStep.id == step_id, CookingRecord.user_id == current_user.id).first()
    if not step:
        raise HTTPException(status_code=404, detail="步骤不存在")
    if req.is_done is not None:
        step.is_done = req.is_done
    if req.timer_minutes is not None:
        step.timer_minutes = req.timer_minutes
    db.commit()
    return {"ok": True}
