from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User
from ..schemas.user import UserCreate, UserLogin, UserResponse
from ..schemas.token import Token
from ..schemas.auth import PasswordResetRequest, PasswordResetConfirm
from ..schemas.profile import UserUpdate, PasswordChange
from ..services.auth_service import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from ..services.token_blacklist import blacklist_token, is_token_blacklisted
import logging
from jose import jwt

router = APIRouter()
logger = logging.getLogger(__name__)

def get_current_user_email(request: Request, db: Session = Depends(get_db)):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    
    token = auth_header.split(" ")[1]
    if is_token_blacklisted(token):
        raise HTTPException(status_code=401, detail="Token has been invalidated")
    
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return payload.get("sub")

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pw = hash_password(user.password)
    new_user = User(full_name=user.full_name, email=user.email, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    logger.info(f"Registered user: {new_user.email}")
    return new_user

@router.post("/login", response_model=Token)
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_credentials.email).first()
    if not user or not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    
    return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")

@router.post("/logout")
def logout(request: Request, db: Session = Depends(get_db)):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=400, detail="Missing Authorization header")
    
    token = auth_header.split(" ")[1]
    payload = decode_token(token)
    if payload:
        # Blacklist the token until it expires
        exp = payload.get("exp")
        if exp:
            import datetime
            remaining = int((datetime.datetime.utcfromtimestamp(exp) - datetime.datetime.utcnow()).total_seconds())
            if remaining > 0:
                blacklist_token(token, remaining)
    
    return {"detail": "Successfully logged out"}

@router.post("/refresh", response_model=Token)
def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    if is_token_blacklisted(refresh_token):
        raise HTTPException(status_code=401, detail="Refresh token invalidated")
        
    payload = decode_token(refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    email = payload.get("sub")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    new_access_token = create_access_token(data={"sub": user.email})
    new_refresh_token = create_refresh_token(data={"sub": user.email})
    
    return Token(access_token=new_access_token, refresh_token=new_refresh_token, token_type="bearer")

@router.post("/forgot-password")
def forgot_password(request: PasswordResetRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        # Avoid revealing if user exists for security
        return {"detail": "If the email exists, a reset link has been sent"}
    
    # Generate a reset token (normally this would be a separate table/token with expiry)
    # For this demo, we use a simple JWT
    reset_token = create_access_token(data={"sub": user.email, "type": "reset"}, expires_delta=None)
    
    logger.info(f"Password reset requested for {user.email}. Token: {reset_token}")
    return {"detail": "If the email exists, a reset link has been sent"}

@router.post("/reset-password")
def reset_password(request: PasswordResetConfirm, db: Session = Depends(get_db)):
    payload = decode_token(request.token)
    if payload is None or payload.get("type") != "reset":
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    
    email = payload.get("sub")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.hashed_password = hash_password(request.new_password)
    db.commit()
    
    return {"detail": "Password has been successfully reset"}


@router.patch("/profile", response_model=UserResponse)
def update_profile(update_data: UserUpdate, email: str = Depends(get_current_user_email), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    for key, value in update_data.dict(exclude_unset=True).items():
        setattr(user, key, value)
    
    db.commit()
    db.refresh(user)
    return user

@router.post("/change-password")
def change_password(change_data: PasswordChange, email: str = Depends(get_current_user_email), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(change_data.current_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password incorrect")
    
    user.hashed_password = hash_password(change_data.new_password)
    db.commit()
    
    return {"detail": "Password changed successfully"}

@router.delete("/account")
def delete_account(email: str = Depends(get_current_user_email), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    
    return {"detail": "Account and all associated data deleted successfully"}
