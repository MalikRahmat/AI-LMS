from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models import Question, Topic
from ..utils import role_required, current_user
from ..services.quiz import generate_quiz, grade_quiz
from ..services import llm

bp = Blueprint("quiz", __name__, url_prefix="/api/quiz")


@bp.post("/generate")
@role_required("student")
def generate():
    d = request.get_json(silent=True) or {}
    num = max(1, min(int(d.get("num", 10)), 30))
    qs = generate_quiz(current_user(), num, d.get("topic_id"))
    if not qs:
        return jsonify(error="No questions available yet"), 404
    return jsonify(questions=[q.to_public() for q in qs])


@bp.post("/submit")
@role_required("student")
def submit():
    answers = (request.get_json(silent=True) or {}).get("answers") or []
    if not answers:
        return jsonify(error="No answers submitted"), 400
    attempt, results = grade_quiz(current_user(), answers)
    from ..ml.analytics import weakness_report
    return jsonify(attempt_id=attempt.id, score=attempt.score, total=attempt.total, results=results,
                   weakest=weakness_report(current_user().id)[:3])


@bp.post("/ai-generate")
@role_required("student", "teacher", "admin")
def ai_generate():
    """Uses the LLM to create new questions for a topic and stores them in the question bank."""
    if not llm.llm_available():
        return jsonify(error="AI generation needs LLM_API_KEY in backend/.env"), 503
    d = request.get_json(silent=True) or {}
    topic = db.session.get(Topic, int(d.get("topic_id", 0)))
    if not topic:
        return jsonify(error="Topic not found"), 404
    num = max(1, min(int(d.get("num", 5)), 10))
    prompt = (f"Create {num} multiple-choice questions about '{topic.name}' ({topic.subject.name}). "
              'Return ONLY JSON: {"questions":[{"text":"","options":["","","",""],"answer_index":0,'
              '"difficulty":1,"explanation":""}]}. difficulty is 1-3.')
    try:
        data = llm.chat_json([{"role": "user", "content": prompt}])
    except Exception as e:
        return jsonify(error=f"AI generation failed: {e}"), 502
    created = []
    for q in data.get("questions", []):
        if len(q.get("options", [])) != 4 or q.get("answer_index") not in (0, 1, 2, 3):
            continue
        row = Question(topic_id=topic.id, text=q["text"], options=q["options"], answer_index=q["answer_index"],
                       difficulty=min(max(int(q.get("difficulty", 2)), 1), 3), explanation=q.get("explanation", ""), source="ai")
        db.session.add(row)
        created.append(row)
    db.session.commit()
    return jsonify(created=len(created), questions=[q.to_public() for q in created])
