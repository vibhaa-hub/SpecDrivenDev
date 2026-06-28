from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User
from ..services.portability_service import export_user_data
from .auth_controller import get_current_user_email

router = APIRouter()

@router.get("/export-all", response_class=StreamingResponse)
def export_all_data(email: str = Depends(get_current_user_email), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    zip_buffer = export_user_data(db, user.id)
    
    return StreamingResponse(
        zip_buffer, 
        media_type="application/zip", 
        headers={"Content-Disposition": "attachment; filename=user_data_export.zip"}
    )
