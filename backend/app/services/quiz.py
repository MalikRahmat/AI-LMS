import random
from ..extensions import db
from ..models import Question, AnswerLog, QuizAttempt
from ..ml.analytics import weakness_report, user_topic_state


def _target_difficulty(acc):
    if acc is None or acc < 0.4:
        return 1
    return 2 if acc < 0.75 else 3


def generate_quiz(user, num=10, topic_id=None):
    report = weakness_report(user.id)
    if topic_id:
        report = [r for r in report if r["topic_id"] == topic_id]
    seen = {r[0] for r in db.session.query(AnswerLog.question_id).filter_by(user_id=user.id).all()}
    pools, weights = {}, {}
    for r in report:
        qs = Question.query.filter_by(topic_id=r["topic_id"]).all()
        if not qs:
            continue
        target = _target_difficulty(r["accuracy"])
        random.shuffle(qs)
        qs.sort(key=lambda q: (q.id in seen, abs((q.difficulty or 2) - target)))
        pools[r["topic_id"]] = qs
        weights[r["topic_id"]] = max(r["weakness"], 0.05)
    picked = []
    while len(picked) < num and pools:
        tid = random.choices(list(pools), weights=[weights[t] for t in pools])[0]
        picked.append(pools[tid].pop(0))
        if not pools[tid]:
            pools.pop(tid)
    random.shuffle(picked)
    return picked


def grade_quiz(user, answers):
    attempt = QuizAttempt(user_id=user.id, score=0, total=0)
    db.session.add(attempt)
    db.session.flush()
    results = []
    for a in answers:
        q = db.session.get(Question, int(a.get("question_id", 0)))
        if not q:
            continue
        sel = a.get("selected")
        correct = sel is not None and int(sel) == q.answer_index
        db.session.add(AnswerLog(attempt_id=attempt.id, user_id=user.id, question_id=q.id, topic_id=q.topic_id,
                                 selected=sel, correct=correct, difficulty=q.difficulty))
        attempt.total += 1
        attempt.score += int(correct)
        results.append({"question_id": q.id, "topic": q.topic.name, "text": q.text, "options": q.options,
                        "selected": sel, "correct_index": q.answer_index, "correct": correct,
                        "explanation": q.explanation})
    db.session.commit()
    return attempt, results
