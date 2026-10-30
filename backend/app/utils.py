from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import User


def current_user():
    uid = get_jwt_identity()
    return User.query.get(int(uid)) if uid else None


def role_required(*roles):
    def deco(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = current_user()
            if not user or not user.active:
                return jsonify(error="Account not found or disabled"), 401
            if roles and user.role not in roles:
                return jsonify(error="You do not have permission for this action"), 403
            return fn(*args, **kwargs)
        return jwt_required()(wrapper)
    return deco
