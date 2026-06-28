from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User
from ..services.import_service import process_csv_import
from .auth_controller import get_current_user_email

router = APIRouter()

@router.post("/import-csv")
async def import_transactions_csv(
    file: UploadFile = File(...), 
    email: str = Depends(get_current_user_email), 
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV")
        
    results = process_csv_import(db, user, file)
    return {
        "summary": results,
        "message": f"Import completed. {results['success']} succeeded, {results['failed']} failed."
    }
