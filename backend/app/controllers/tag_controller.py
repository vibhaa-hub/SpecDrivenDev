from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.tag import Tag
from ..models.user import User
from ..schemas.tag import TagCreate, TagUpdate, TagResponse
from .auth_controller import get_current_user_email
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=list[TagResponse])
def list_tags(email: str = Depends(get_current_user_email), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return db.query(Tag).filter(Tag.user_id == user.id).all()

@router.post("/", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
def create_tag(tag_data: TagCreate, email: str = Depends(get_current_user_email), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    
    # Check if tag already exists for this user
    existing_tag = db.query(Tag).filter(Tag.name == tag_data.name, Tag.user_id == user.id).first()
    if existing_tag:
        raise HTTPException(status_code=400, detail="Tag already exists")
    
    new_tag = Tag(name=tag_data.name, user_id=user.id)
    db.add(new_tag)
    db.commit()
    db.refresh(new_tag)
    return new_tag

@router.patch("/{tag_id}", response_model=TagResponse)
def update_tag(tag_id: int, update_data: TagUpdate, email: str = Depends(get_current_user_email), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    if tag.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this tag")
    
    tag.name = update_data.name
    db.commit()
    db.refresh(tag)
    return tag

@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(tag_id: int, email: str = Depends(get_current_user_email), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    if tag.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this tag")
    
    db.delete(tag)
    db.commit()
    return None
