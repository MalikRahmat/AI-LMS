"""Predicts the probability that a student answers a question of a given topic correctly.
Features: topic accuracy so far, topic attempts, overall accuracy, question difficulty."""
import os
import joblib
import numpy as np
from ..config import Config
from ..models import AnswerLog

MIN_SAMPLES = 60
_cache = {"loaded": False, "kind": None, "model": None}


def feat(tc, tt, uc, ut, difficulty):
    return [(tc + 1) / (tt + 2), min(tt, 50) / 50.0, (uc + 1) / (ut + 2), difficulty / 3.0]


def build_dataset():
    logs = AnswerLog.query.order_by(AnswerLog.created_at, AnswerLog.id).all()
    tstate, ustate, X, y = {}, {}, [], []
    for l in logs:
        tc, tt = tstate.get((l.user_id, l.topic_id), (0, 0))
        uc, ut = ustate.get(l.user_id, (0, 0))
        X.append(feat(tc, tt, uc, ut, l.difficulty or 2))
        y.append(int(l.correct))
        tstate[(l.user_id, l.topic_id)] = (tc + int(l.correct), tt + 1)
        ustate[l.user_id] = (uc + int(l.correct), ut + 1)
    return np.array(X, dtype="float32"), np.array(y, dtype="int32")


def _paths():
    os.makedirs(Config.MODEL_DIR, exist_ok=True)
    return os.path.join(Config.MODEL_DIR, "sk_model.joblib"), os.path.join(Config.MODEL_DIR, "tf_model.keras")


def train():
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    X, y = build_dataset()
    if len(y) < MIN_SAMPLES or len(set(y.tolist())) < 2:
        return {"trained": False, "samples": int(len(y)), "reason": f"Need at least {MIN_SAMPLES} answers with both outcomes"}
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)
    clf = LogisticRegression(max_iter=1000).fit(Xtr, ytr)
    acc = float(clf.score(Xte, yte))
    sk_path, tf_path = _paths()
    joblib.dump(clf, sk_path)
    result = {"trained": True, "samples": int(len(y)), "sklearn_accuracy": round(acc, 3), "backend": "scikit-learn"}
    if Config.USE_TENSORFLOW:
        try:
            from . import tf_model
            tf_model.train(X, y, tf_path)
            result["backend"] = "tensorflow"
        except Exception as e:  # TF not installed or failed -> keep sklearn
            result["tensorflow_error"] = str(e)
    _cache["loaded"] = False
    return result


def get_model():
    if _cache["loaded"]:
        return _cache["kind"], _cache["model"]
    sk_path, tf_path = _paths()
    _cache.update(loaded=True, kind=None, model=None)
    try:
        if Config.USE_TENSORFLOW and os.path.exists(tf_path):
            from . import tf_model
            _cache.update(kind="tf", model=tf_model.load(tf_path))
        elif os.path.exists(sk_path):
            _cache.update(kind="sk", model=joblib.load(sk_path))
    except Exception:
        _cache.update(kind=None, model=None)
    return _cache["kind"], _cache["model"]


def predict_success(x):
    """Returns P(correct) or None when no trained model is available."""
    kind, model = get_model()
    if model is None:
        return None
    if kind == "tf":
        from . import tf_model
        return tf_model.predict(model, x)
    return float(model.predict_proba(np.array([x]))[0][1])
