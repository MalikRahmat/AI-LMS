from ..models import Resource

STYLE_TYPES = {"visual": ["video", "pdf"], "auditory": ["audio", "video"],
               "reading": ["article", "pdf"], "kinesthetic": ["exercise"]}


def recommend_resources(user, report, topics=3, per_topic=3):
    prefs = STYLE_TYPES.get(user.learning_style or "reading", [])
    out = []
    for r in report[:topics]:
        items = Resource.query.filter_by(topic_id=r["topic_id"]).all()
        items.sort(key=lambda x: 0 if x.type in prefs else 1)
        out.append({"topic": r["topic"], "weakness": r["weakness"],
                    "resources": [i.to_dict() for i in items[:per_topic]]})
    return out


def study_plan(user, report, days=7):
    weak = report[:3] or []
    if not weak:
        return []
    prefs = STYLE_TYPES.get(user.learning_style or "reading", [])
    plan = []
    for d in range(1, days + 1):
        if d == days:
            plan.append({"day": d, "focus": "Mixed review", "tasks": ["Take a 10-question adaptive quiz across all weak topics"]})
            continue
        t = weak[(d - 1) % len(weak)]
        res = Resource.query.filter_by(topic_id=t["topic_id"]).all()
        res.sort(key=lambda x: 0 if x.type in prefs else 1)
        tasks = [f"Study: {res[(d - 1) // len(weak) % len(res)].title}" if res else f"Review notes for {t['topic']}",
                 f"Practice quiz on {t['topic']} (5 questions)"]
        plan.append({"day": d, "focus": t["topic"], "tasks": tasks})
    return plan
