from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models import ChatMessage
from ..utils import role_required, current_user
from ..ml.analytics import weakness_report
from ..ml.chatbot_engine import fallback_answer
from ..services import llm

bp = Blueprint("chatbot", __name__, url_prefix="/api/chat")


@bp.get("")
@role_required("student", "teacher", "admin")
def history():
    msgs = ChatMessage.query.filter_by(user_id=current_user().id).order_by(ChatMessage.id.desc()).limit(30).all()
    return jsonify(messages=[{"role": m.role, "content": m.content} for m in reversed(msgs)])


@bp.post("")
@role_required("student", "teacher", "admin")
def ask():
    user = current_user()
    text = ((request.get_json(silent=True) or {}).get("message") or "").strip()
    if not text or len(text) > 2000:
        return jsonify(error="Type a question (max 2000 characters)"), 400
    past = ChatMessage.query.filter_by(user_id=user.id).order_by(ChatMessage.id.desc()).limit(8).all()
    db.session.add(ChatMessage(user_id=user.id, role="user", content=text))
    mode = "offline"
    reply = None
    if llm.llm_available():
        weak = ", ".join(r["topic"] for r in weakness_report(user.id)[:3])
        system = (f"You are a friendly AI tutor. The student's name is {user.name}, learning style: {user.learning_style}. "
                  f"Their weakest topics: {weak}. Explain simply with short examples, adapt to their learning style, "
                  "and end with one practice question when helpful. Keep answers under 200 words.")
        msgs = [{"role": "system", "content": system}] + [{"role": m.role, "content": m.content} for m in reversed(past)]
        msgs.append({"role": "user", "content": text})
        try:
            reply, mode = llm.chat(msgs), "llm"
        except Exception:
            reply = None
    if reply is None:
        reply = fallback_answer(text)
    db.session.add(ChatMessage(user_id=user.id, role="assistant", content=reply))
    db.session.commit()
    return jsonify(reply=reply, mode=mode)
