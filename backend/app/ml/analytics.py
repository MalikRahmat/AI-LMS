from sqlalchemy import func, case
from ..extensions import db
from ..models import AnswerLog, Topic
from .predictor import feat, predict_success


def user_topic_state(user_id):
    rows = (db.session.query(AnswerLog.topic_id, func.count(AnswerLog.id),
                             func.sum(case((AnswerLog.correct == True, 1), else_=0)))  # noqa: E712
            .filter(AnswerLog.user_id == user_id).group_by(AnswerLog.topic_id).all())
    return {tid: (int(c or 0), int(n)) for tid, n, c in rows}


def weakness_report(user_id):
    """Per-topic weakness (0..1, higher = weaker), sorted weakest first."""
    state = user_topic_state(user_id)
    uc = sum(c for c, _ in state.values())
    ut = sum(n for _, n in state.values())
    report = []
    for t in Topic.query.all():
        c, n = state.get(t.id, (0, 0))
        p = predict_success(feat(c, n, uc, ut, 2))
        if p is None:  # heuristic fallback (Bayesian-smoothed accuracy)
            p = (c + 1) / (n + 2)
        report.append({"topic_id": t.id, "topic": t.name, "subject": t.subject.name, "answered": n,
                       "accuracy": round(c / n, 3) if n else None,
                       "predicted_success": round(p, 3), "weakness": round(1 - p, 3)})
    report.sort(key=lambda r: r["weakness"], reverse=True)
    return report


def overall_stats(user_id):
    state = user_topic_state(user_id)
    c = sum(x for x, _ in state.values())
    n = sum(x for _, x in state.values())
    return {"answered": n, "correct": c, "accuracy": round(c / n, 3) if n else None}
