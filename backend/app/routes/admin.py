from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models import User, Question, Resource, QuizAttempt, ROLES
from ..utils import role_required, current_user
from ..ml import predictor

bp = Blueprint("admin", __name__, url_prefix="/api/admin")


@bp.get("/stats")
@role_required("admin")
def stats():
    return jsonify(users=User.query.count(), questions=Question.query.count(), resources=Resource.query.count(),
                   attempts=QuizAttempt.query.count())


@bp.get("/users")
@role_required("admin")
def users():
    return jsonify(users=[u.to_dict() for u in User.query.order_by(User.id).all()])


@bp.post("/users")
@role_required("admin")
def create_user():
    d = request.get_json(silent=True) or {}
    email = (d.get("email") or "").strip().lower()
    if not d.get("name") or not email or len(d.get("password") or "") < 8 or d.get("role") not in ROLES:
        return jsonify(error="Name, email, role and a password of 8+ characters are required"), 400
    if User.query.filter_by(email=email).first():
        return jsonify(error="Email already exists"), 409
    u = User(name=d["name"].strip(), email=email, role=d["role"])
    u.set_password(d["password"])
    db.session.add(u)
    db.session.commit()
    return jsonify(user=u.to_dict()), 201


@bp.patch("/users/<int:uid>")
@role_required("admin")
def update_user(uid):
    d = request.get_json(silent=True) or {}
    u = db.get_or_404(User, uid)
    if u.id == current_user().id and (d.get("active") is False or d.get("role") not in (None, "admin")):
        return jsonify(error="You cannot disable or demote your own account"), 400
    if d.get("role") in ROLES:
        u.role = d["role"]
    if isinstance(d.get("active"), bool):
        u.active = d["active"]
    db.session.commit()
    return jsonify(user=u.to_dict())


@bp.post("/train-model")
@role_required("admin")
def train_model():
    return jsonify(predictor.train())
