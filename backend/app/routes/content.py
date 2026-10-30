from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models import Subject, Topic, Question
from ..utils import role_required

bp = Blueprint("content", __name__, url_prefix="/api/content")


@bp.get("/topics")
@role_required()
def topics():
    return jsonify(topics=[t.to_dict() for t in Topic.query.order_by(Topic.subject_id, Topic.name).all()])


@bp.post("/topics")
@role_required("teacher", "admin")
def add_topic():
    d = request.get_json(silent=True) or {}
    sname, tname = (d.get("subject") or "").strip(), (d.get("name") or "").strip()
    if not sname or not tname:
        return jsonify(error="Subject and topic name are required"), 400
    subject = Subject.query.filter_by(name=sname).first() or Subject(name=sname)
    db.session.add(subject)
    db.session.flush()
    topic = Topic(subject_id=subject.id, name=tname, description=d.get("description", ""))
    db.session.add(topic)
    db.session.commit()
    return jsonify(topic=topic.to_dict()), 201


@bp.post("/questions")
@role_required("teacher", "admin")
def add_question():
    d = request.get_json(silent=True) or {}
    opts = d.get("options") or []
    if not d.get("text") or len(opts) != 4 or d.get("answer_index") not in (0, 1, 2, 3) or not db.session.get(Topic, d.get("topic_id") or 0):
        return jsonify(error="Provide topic, question text, 4 options and the correct option"), 400
    q = Question(topic_id=d["topic_id"], text=d["text"].strip(), options=[str(o) for o in opts],
                 answer_index=d["answer_index"], difficulty=min(max(int(d.get("difficulty", 2)), 1), 3),
                 explanation=d.get("explanation", ""))
    db.session.add(q)
    db.session.commit()
    return jsonify(question=q.to_public()), 201
