"""NLP fallback tutor (no API key needed): TF-IDF retrieval over topic notes and question explanations."""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from ..models import Topic, Question, Resource


def _corpus():
    docs, meta = [], []
    for t in Topic.query.all():
        expl = " ".join(q.explanation or "" for q in Question.query.filter_by(topic_id=t.id).all())
        docs.append(f"{t.name}. {t.description} {expl}")
        meta.append(t)
    return docs, meta


def fallback_answer(message):
    docs, meta = _corpus()
    if not docs:
        return "No learning content is available yet. Ask your teacher to add topics."
    vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    matrix = vec.fit_transform(docs + [message])
    sims = cosine_similarity(matrix[-1], matrix[:-1]).flatten()
    best = int(sims.argmax())
    if sims[best] < 0.05:
        return ("I could not match that to a topic in your course. Try naming a topic, for example: "
                + ", ".join(t.name for t in meta[:4]) + ".")
    topic = meta[best]
    res = Resource.query.filter_by(topic_id=topic.id).limit(2).all()
    out = f"**{topic.name}** ({topic.subject.name})\n\n{topic.description}"
    if res:
        out += "\n\nStudy next: " + "; ".join(r.title for r in res)
    out += "\n\nTip: take an adaptive quiz on this topic to check your understanding."
    return out
