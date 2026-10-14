from datetime import datetime
from pydantic import BaseModel, Field


# ---------- 认证 ----------
class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)


class LoginRequest(BaseModel):
    username: str
    password: str


class UserInfo(BaseModel):
    id: int
    username: str
    created_at: datetime | None = None


class TokenResponse(BaseModel):
    token: str
    user: UserInfo


# ---------- 审查 ----------
class ReviewRequest(BaseModel):
    code: str = Field(..., min_length=1, description="待审查代码")
    language: str = Field("javascript")
    ruleset: str = Field("local")
    file_name: str = Field("", description="文件名（可选）")


class Defect(BaseModel):
    line: int
    level: str
    cat: str
    title: str
    desc: str
    fix: str
    rule_id: str = ""
    cwe: str = ""
    source: str = "rule"   # rule / llm
    code: str = ""         # 参考修复代码（RAG 检索）


class Summary(BaseModel):
    total: int
    high: int
    mid: int
    low: int


class ReviewResponse(BaseModel):
    review_id: int
    defects: list[Defect]
    summary: Summary
    duration_ms: int
    rule_findings: int
    llm_used: bool = False


class ReviewListItem(BaseModel):
    id: int
    file_name: str
    language: str
    total: int
    high: int
    mid: int
    low: int
    duration_ms: int
    created_at: datetime


class ReviewDetail(BaseModel):
    id: int
    file_name: str
    language: str
    code: str
    total: int
    high: int
    mid: int
    low: int
    duration_ms: int
    created_at: datetime
    defects: list[Defect]


class AuditLogItem(BaseModel):
    id: int
    action: str
    detail: str
    created_at: datetime
