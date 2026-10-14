from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, auth
from ..schemas import RegisterRequest, LoginRequest, TokenResponse, UserInfo

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _token_response(user: models.User) -> TokenResponse:
    return TokenResponse(
        token=auth.create_token(user.id, user.username),
        user=UserInfo(id=user.id, username=user.username, created_at=user.created_at),
    )


@router.post("/register", response_model=TokenResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    exists = db.query(models.User).filter(models.User.username == req.username).first()
    if exists:
        raise HTTPException(400, "用户名已存在")
    user = models.User(username=req.username, password_hash=auth.hash_password(req.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    db.add(models.AuditLog(user_id=user.id, action="register", detail=req.username))
    db.commit()
    return _token_response(user)


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == req.username).first()
    if not user or not auth.verify_password(req.password, user.password_hash):
        raise HTTPException(401, "用户名或密码错误")
    db.add(models.AuditLog(user_id=user.id, action="login", detail=req.username))
    db.commit()
    return _token_response(user)


@router.get("/me", response_model=UserInfo)
def me(user: models.User = Depends(auth.get_current_user)):
    return UserInfo(id=user.id, username=user.username, created_at=user.created_at)
