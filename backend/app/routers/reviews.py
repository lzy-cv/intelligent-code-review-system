from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, auth
from ..engine import pipeline, semgrep
from ..schemas import (
    ReviewRequest, ReviewResponse, ReviewListItem, ReviewDetail,
    Defect, Summary, AuditLogItem,
)

router = APIRouter(prefix="/api", tags=["reviews"])


def _defect_out(d: models.Defect) -> Defect:
    return Defect(
        line=d.line, level=d.level, cat=d.cat, title=d.title,
        desc=d.desc, fix=d.fix, rule_id=d.rule_id, cwe=d.cwe,
        source=d.source, code=d.code,
    )


@router.post("/review", response_model=ReviewResponse)
def review(
    req: ReviewRequest,
    user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    if not req.code.strip():
        raise HTTPException(400, "代码不能为空")

    try:
        defects, counts, duration, raw, llm_used = pipeline.run_review(req.code, req.language, req.ruleset)
    except semgrep.SemgrepRunError as e:
        raise HTTPException(500, str(e))

    # 审查记录落库
    review = models.Review(
        user_id=user.id,
        file_name=req.file_name or "",
        language=req.language,
        ruleset=req.ruleset,
        code=req.code,
        total=counts["total"],
        high=counts["high"],
        mid=counts["mid"],
        low=counts["low"],
        duration_ms=duration,
    )
    db.add(review)
    db.flush()

    for d in defects:
        db.add(models.Defect(review_id=review.id, **d))

    engine_desc = f"{req.language} 检出 {counts['total']} 处缺陷" + ("（含 LLM 分析）" if llm_used else "")
    db.add(models.AuditLog(user_id=user.id, action="review", detail=engine_desc))
    db.commit()
    db.refresh(review)

    return ReviewResponse(
        review_id=review.id,
        defects=[Defect(**d) for d in defects],
        summary=Summary(**counts),
        duration_ms=duration,
        rule_findings=raw,
        llm_used=llm_used,
    )


@router.get("/reviews", response_model=list[ReviewListItem])
def list_reviews(user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    rows = (
        db.query(models.Review)
        .filter(models.Review.user_id == user.id)
        .order_by(models.Review.id.desc())
        .all()
    )
    return [
        ReviewListItem(
            id=r.id, file_name=r.file_name, language=r.language,
            total=r.total, high=r.high, mid=r.mid, low=r.low,
            duration_ms=r.duration_ms, created_at=r.created_at,
        )
        for r in rows
    ]


@router.get("/reviews/{review_id}", response_model=ReviewDetail)
def get_review(review_id: int, user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    review = db.get(models.Review, review_id)
    if not review or review.user_id != user.id:
        raise HTTPException(404, "记录不存在")
    defects = sorted(review.defects, key=lambda d: d.id)
    return ReviewDetail(
        id=review.id, file_name=review.file_name, language=review.language,
        code=review.code, total=review.total, high=review.high, mid=review.mid, low=review.low,
        duration_ms=review.duration_ms, created_at=review.created_at,
        defects=[_defect_out(d) for d in defects],
    )


@router.get("/logs", response_model=list[AuditLogItem])
def get_logs(user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    rows = (
        db.query(models.AuditLog)
        .filter(models.AuditLog.user_id == user.id)
        .order_by(models.AuditLog.id.desc())
        .limit(50)
        .all()
    )
    return [AuditLogItem(id=l.id, action=l.action, detail=l.detail, created_at=l.created_at) for l in rows]
