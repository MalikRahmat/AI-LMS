from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db

ROLES = ("student", "teacher", "admin")
STYLES = ("visual", "auditory", "reading", "kinesthetic")


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(190), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="student")
    learning_style = db.Column(db.String(20), default="reading")
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, pw):
        self.password_hash = generate_password_hash(pw)

    def check_password(self, pw):
        return check_password_hash(self.password_hash, pw)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "email": self.email, "role": self.role,
                "learning_style": self.learning_style, "active": self.active,
                "created_at": self.created_at.isoformat()}


class Subject(db.Model):
    __tablename__ = "subjects"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    topics = db.relationship("Topic", backref="subject", lazy=True)


class Topic(db.Model):
    __tablename__ = "topics"
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id"), nullable=False)
    name = db.Column(db.String(160), nullable=False)
    description = db.Column(db.Text, default="")

    def to_dict(self):
        return {"id": self.id, "name": self.name, "subject": self.subject.name,
                "subject_id": self.subject_id, "description": self.description}


class Question(db.Model):
    __tablename__ = "questions"
    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey("topics.id"), nullable=False, index=True)
    text = db.Column(db.Text, nullable=False)
    options = db.Column(db.JSON, nullable=False)
    answer_index = db.Column(db.Integer, nullable=False)
    difficulty = db.Column(db.Integer, default=2)  # 1 easy, 2 medium, 3 hard
    explanation = db.Column(db.Text, default="")
    source = db.Column(db.String(20), default="manual")  # manual | ai
    topic = db.relationship("Topic")

    def to_public(self):
        return {"id": self.id, "topic_id": self.topic_id, "topic": self.topic.name, "text": self.text,
                "options": self.options, "difficulty": self.difficulty}


class QuizAttempt(db.Model):
    __tablename__ = "quiz_attempts"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    score = db.Column(db.Integer, default=0)
    total = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class AnswerLog(db.Model):
    __tablename__ = "answer_logs"
    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey("quiz_attempts.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey("topics.id"), nullable=False, index=True)
    selected = db.Column(db.Integer)
    correct = db.Column(db.Boolean, nullable=False)
    difficulty = db.Column(db.Integer, default=2)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Resource(db.Model):
    __tablename__ = "resources"
    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey("topics.id"), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(20), default="article")  # video | audio | article | pdf | exercise
    url = db.Column(db.String(500), default="")
    storage_key = db.Column(db.String(300), default="")
    description = db.Column(db.Text, default="")
    uploaded_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    topic = db.relationship("Topic")

    def to_dict(self):
        return {"id": self.id, "topic_id": self.topic_id, "topic": self.topic.name if self.topic else None,
                "title": self.title, "type": self.type, "url": self.url,
                "has_file": bool(self.storage_key), "description": self.description}


class ChatMessage(db.Model):
    __tablename__ = "chat_messages"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    role = db.Column(db.String(10), nullable=False)  # user | assistant
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
