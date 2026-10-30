import re
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from ..extensions import db
from ..models import User, STYLES
from ..utils import role_required, current_user

bp = Blueprint("auth", __name__, url_prefix="/api/auth")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _token(user):
    return create_access_token(identity=str(user.id), additional_claims={"role": user.role})


@bp.post("/register")
def register():
    d = request.get_json(silent=True) or {}
    name, email, pw = (d.get("name") or "").strip(), (d.get("email") or "").strip().lower(), d.get("password") or ""
    if not name or not EMAIL_RE.match(email) or len(pw) < 8:
        return jsonify(error="Enter a name, a valid email and a password of at least 8 characters"), 400
    if User.query.filter_by(email=email).first():
        return jsonify(error="This email is already registered"), 409
    style = d.get("learning_style") if d.get("learning_style") in STYLES else "reading"
    user = User(name=name, email=email, role="student", learning_style=style)  # public signup = student only
    user.set_password(pw)
    db.session.add(user)
    db.session.commit()
    return jsonify(token=_token(user), user=user.to_dict()), 201


@bp.post("/login")
def login():
    d = request.get_json(silent=True) or {}
    user = User.query.filter_by(email=(d.get("email") or "").strip().lower()).first()
    if not user or not user.check_password(d.get("password") or ""):
        return jsonify(error="Incorrect email or password"), 401
    if not user.active:
        return jsonify(error="This account is disabled"), 403
    return jsonify(token=_token(user), user=user.to_dict())


@bp.get("/me")
@role_required()
def me():
    return jsonify(user=current_user().to_dict())
