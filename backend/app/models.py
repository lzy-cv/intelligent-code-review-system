from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    reviews = relationship("Review", back_populates="owner", cascade="all, delete-orphan")


class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    file_name = Column(String(200), default="")
    language = Column(String(50), default="javascript")
    ruleset = Column(String(50), default="local")
    code = Column(Text, default="")
    total = Column(Integer, default=0)
    high = Column(Integer, default=0)
    mid = Column(Integer, default=0)
    low = Column(Integer, default=0)
    duration_ms = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="reviews")
    defects = relationship("Defect", back_populates="review", cascade="all, delete-orphan")


class Defect(Base):
    __tablename__ = "defects"
    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("reviews.id"), nullable=False, index=True)
    line = Column(Integer, default=0)
    level = Column(String(10), default="low")
    cat = Column(String(50), default="")
    title = Column(String(200), default="")
    desc = Column(Text, default="")
    fix = Column(Text, default="")
    rule_id = Column(String(100), default="")
    cwe = Column(String(50), default="")
    source = Column(String(10), default="rule")
    code = Column(Text, default="")

    review = relationship("Review", back_populates="defects")


class AuditLog(Base):
    """操作日志：记录登录、注册、审查等行为"""
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    action = Column(String(100), nullable=False)
    detail = Column(String(500), default="")
    created_at = Column(DateTime, default=datetime.utcnow)
