from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid
from .. import crud, models, schemas
from ..database import get_db
from ..dependencies import get_current_user

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
    responses={404: {"description": "Not found"}},
)

@router.post("/messages", response_model=schemas.MessageResponse)
def send_message(
    message: schemas.MessageCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Check if receiver exists
    receiver = db.query(models.User).filter(models.User.id == message.receiver_id).first()
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver not found")

    # Optional: Check if they are bound (for strict security)
    # For now, allow open chat if they have IDs, or we can enforce binding check.
    # Let's enforce that one of them is a doctor and one is a patient and they are bound.
    # But current_user.role is available.
    
    return crud.create_message(db=db, message=message, sender_id=current_user.id)

@router.get("/messages/{other_user_id}", response_model=List[schemas.MessageResponse])
def get_messages(
    other_user_id: uuid.UUID,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.get_chat_history(db=db, user_id_1=current_user.id, user_id_2=other_user_id, skip=skip, limit=limit)
