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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(reviews.router)


@app.get("/health")
def health():
    return {"status": "ok", "engine": "semgrep"}
