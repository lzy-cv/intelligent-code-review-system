import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine, SessionLocal
from . import models, auth
from .routers import auth as auth_router
from .routers import reviews


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    # 首次启动时预置演示账号 demo / demo123
    db = SessionLocal()
    try:
        if not db.query(models.User).first():
            db.add(models.User(username="demo", password_hash=auth.hash_password("demo123")))
            db.commit()
    finally:
        db.close()
    yield


app = FastAPI(title="智能代码审查平台 API", version="0.2.0", lifespan=lifespan)

# 允许的前端来源，可用 CORS_ORIGINS 环境变量覆盖（逗号分隔）
ALLOWED_ORIGINS = [
    o.strip()
    for o in os.environ.get(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if o.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    # 认证走 Authorization 头而非 Cookie，因此关闭凭证模式；
    # 通配来源 + allow_credentials=True 是规范禁止的组合
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth_router.router)
app.include_router(reviews.router)


@app.get("/health")
def health():
    return {"status": "ok", "engine": "semgrep"}
