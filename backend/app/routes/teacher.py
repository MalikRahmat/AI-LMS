from flask import Blueprint, jsonify
from sqlalchemy import func, case
from ..extensions import db
from ..models import User, AnswerLog, Topic, QuizAttempt
from ..utils import role_required
from ..ml.analytics import weakness_report, overall_stats

bp = Blueprint("teacher", __name__, url_prefix="/api/teacher")


@bp.get("/overview")
@role_required("teacher", "admin")
def overview():
    students = User.query.filter_by(role="student", active=True).all()
    rows = []
    for s in students:
        stats = overall_stats(s.id)
        rep = weakness_report(s.id)
        last = db.session.query(func.max(QuizAttempt.created_at)).filter_by(user_id=s.id).scalar()
        rows.append({"id": s.id, "name": s.name, "email": s.email, "learning_style": s.learning_style, **stats,
                     "weakest_topic": rep[0]["topic"] if rep and stats["answered"] else None,
                     "last_active": last.isoformat() if last else None})
    topic_rows = (db.session.query(Topic.name, func.count(AnswerLog.id),
                                   func.sum(case((AnswerLog.correct == True, 1), else_=0)))  # noqa: E712
                  .join(AnswerLog, AnswerLog.topic_id == Topic.id).group_by(Topic.id, Topic.name).all())
    topics = [{"topic": n, "answered": int(c), "accuracy": round(int(k or 0) / int(c), 3)} for n, c, k in topic_rows]
    topics.sort(key=lambda x: x["accuracy"])
    avg = [r["accuracy"] for r in rows if r["accuracy"] is not None]
    return jsonify(students=rows, topics=topics, class_accuracy=round(sum(avg) / len(avg), 3) if avg else None)


@bp.get("/student/<int:sid>")
@role_required("teacher", "admin")
def student_detail(sid):
    s = db.get_or_404(User, sid)
    attempts = QuizAttempt.query.filter_by(user_id=sid).order_by(QuizAttempt.created_at).all()
    return jsonify(user=s.to_dict(), stats=overall_stats(sid), topics=weakness_report(sid),
                   history=[{"score": a.score, "total": a.total, "date": a.created_at.isoformat()} for a in attempts])
