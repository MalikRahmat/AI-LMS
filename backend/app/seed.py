import random
from datetime import datetime, timedelta
from .extensions import db
from .models import User, Subject, Topic, Question, Resource, QuizAttempt, AnswerLog

TOPICS = {
    "Python": {
        "Variables and Data Types": ("Variables store values. Python types include int, float, str, bool and None. Python is dynamically typed.", [
            ("Which of these is an immutable type?", ["list", "dict", "tuple", "set"], 2, 1, "Tuples cannot be changed after creation."),
            ("What does type(3.0) return?", ["int", "float", "str", "decimal"], 1, 1, "3.0 is a floating point number."),
            ("What is the result of '3' + '4'?", ["7", "34", "Error", "'7'"], 1, 2, "+ concatenates two strings.")]),
        "Loops and Conditions": ("for loops iterate over sequences, while loops repeat until a condition is false. if/elif/else choose branches.", [
            ("How many times does range(5) loop?", ["4", "5", "6", "Infinite"], 1, 1, "range(5) yields 0 to 4, five values."),
            ("Which keyword stops a loop immediately?", ["stop", "exit", "break", "continue"], 2, 1, "break exits the nearest loop."),
            ("What does 'continue' do?", ["Ends the program", "Skips to the next iteration", "Restarts the loop", "Exits the loop"], 1, 2, "continue skips the rest of the current iteration.")]),
        "Functions": ("Functions are defined with def, take parameters and return values with return. Functions without return give None.", [
            ("Which keyword defines a function?", ["func", "def", "function", "lambda only"], 1, 1, "def starts a function definition."),
            ("What does a function without return give back?", ["0", "''", "None", "Error"], 2, 2, "Python returns None by default."),
            ("What is *args used for?", ["Keyword arguments", "Any number of positional arguments", "Pointers", "Decorators"], 1, 3, "*args collects extra positional arguments into a tuple.")]),
        "Lists and Dictionaries": ("Lists are ordered mutable sequences. Dictionaries map keys to values and have fast lookup.", [
            ("How do you add an item to a list?", ["add()", "append()", "push()", "insert_end()"], 1, 1, "list.append(x) adds to the end."),
            ("Which gets a dict value safely?", ["d[key]", "d.get(key)", "d.find(key)", "d.value(key)"], 1, 2, "get() returns None instead of raising KeyError."),
            ("What is the output of [1,2,3][-1]?", ["1", "2", "3", "Error"], 2, 2, "-1 indexes the last element.")]),
        "Object-Oriented Programming": ("A class is a blueprint for objects. __init__ initialises attributes, self refers to the instance, inheritance reuses code.", [
            ("What is __init__?", ["A destructor", "The constructor method", "A module", "A decorator"], 1, 1, "__init__ runs when an object is created."),
            ("What does inheritance allow?", ["Hiding data", "Reusing a parent class", "Faster loops", "Typing"], 1, 2, "A child class reuses and extends a parent class."),
            ("What does super() do?", ["Calls a parent class method", "Creates a class", "Deletes an object", "Imports a module"], 0, 3, "super() gives access to the parent class.")]),
    },
    "Data Science": {
        "NumPy Basics": ("NumPy provides fast n-dimensional arrays and vectorised math operations without Python loops.", [
            ("Which creates a NumPy array?", ["np.array([1,2])", "np.list([1,2])", "np.make([1,2])", "np.new([1,2])"], 0, 1, "np.array converts a list into an ndarray."),
            ("What is array.shape for a 3x4 matrix?", ["(4,3)", "(3,4)", "12", "(12,)"], 1, 1, "Shape is (rows, columns)."),
            ("What is broadcasting?", ["Sending data over a network", "Operating on arrays of different shapes", "Plotting arrays", "Saving arrays"], 1, 3, "Broadcasting stretches smaller arrays to match larger ones.")]),
        "Pandas Basics": ("Pandas offers DataFrame and Series. Use read_csv to load data, head to preview, groupby to aggregate.", [
            ("Which function reads a CSV file?", ["pd.open_csv", "pd.read_csv", "pd.load_csv", "pd.csv"], 1, 1, "pd.read_csv loads a CSV into a DataFrame."),
            ("A single column of a DataFrame is a:", ["Series", "List", "Array only", "Tuple"], 0, 1, "Selecting one column returns a Series."),
            ("What does groupby do?", ["Sorts data", "Splits data into groups to aggregate", "Deletes duplicates", "Merges tables"], 1, 2, "groupby splits, applies and combines.")]),
        "Machine Learning Basics": ("Machine learning learns patterns from data. Supervised learning uses labels (classification, regression); overfitting means memorising training data.", [
            ("Predicting house prices is:", ["Classification", "Regression", "Clustering", "Reinforcement"], 1, 1, "Predicting a continuous number is regression."),
            ("What is overfitting?", ["Model too simple", "Model memorises training data", "Too little data to load", "Slow training"], 1, 2, "Overfit models do well on training data but poorly on new data."),
            ("Why split data into train and test sets?", ["To save memory", "To evaluate on unseen data", "To speed up loops", "To clean data"], 1, 2, "The test set estimates real-world performance.")]),
    },
}

RESOURCES = [("Python Variables Explained", "video"), ("Variables Cheat Sheet", "article"), ("Loop Practice Problems", "exercise"),
             ("Functions Audio Lesson", "audio"), ("Intro to Pandas", "video"), ("ML Basics Reading", "article")]


def _user(name, email, role, style="reading"):
    u = User.query.filter_by(email=email).first()
    if not u:
        u = User(name=name, email=email, role=role, learning_style=style)
        u.set_password("Password123")
        db.session.add(u)
    return u


def seed():
    _user("Admin", "admin@demo.com", "admin")
    _user("Ms. Teacher", "teacher@demo.com", "teacher")
    _user("Demo Student", "student@demo.com", "student", "visual")
    db.session.commit()
    if Subject.query.count():
        return
    topics = []
    for sname, tdict in TOPICS.items():
        s = Subject(name=sname)
        db.session.add(s)
        db.session.flush()
        for tname, (desc, qs) in tdict.items():
            t = Topic(subject_id=s.id, name=tname, description=desc)
            db.session.add(t)
            db.session.flush()
            topics.append(t)
            for text, opts, ans, diff, expl in qs:
                db.session.add(Question(topic_id=t.id, text=text, options=opts, answer_index=ans, difficulty=diff, explanation=expl))
    teacher = User.query.filter_by(email="teacher@demo.com").first()
    for i, (title, rtype) in enumerate(RESOURCES):
        db.session.add(Resource(title=title, type=rtype, topic_id=topics[i % len(topics)].id, uploaded_by=teacher.id,
                                url="https://docs.python.org/3/tutorial/", description="Demo resource"))
    db.session.commit()

    # Synthetic history for 8 students so the ML model has data to learn from
    rnd = random.Random(7)
    styles = ["visual", "auditory", "reading", "kinesthetic"]
    questions = Question.query.all()
    students = [User.query.filter_by(email="student@demo.com").first()]
    for i in range(8):
        students.append(_user(f"Student {i + 1}", f"student{i + 1}@demo.com", "student", styles[i % 4]))
    db.session.commit()
    for st in students:
        skill = {t.id: rnd.uniform(0.25, 0.9) for t in topics}
        for a in range(6):
            when = datetime.utcnow() - timedelta(days=30 - a * 4)
            att = QuizAttempt(user_id=st.id, created_at=when)
            db.session.add(att)
            db.session.flush()
            for q in rnd.sample(questions, 10):
                p = max(0.05, min(0.95, skill[q.topic_id] + a * 0.02 - (q.difficulty - 2) * 0.15))
                ok = rnd.random() < p
                db.session.add(AnswerLog(attempt_id=att.id, user_id=st.id, question_id=q.id, topic_id=q.topic_id,
                                         selected=q.answer_index if ok else (q.answer_index + 1) % 4, correct=ok,
                                         difficulty=q.difficulty, created_at=when))
                att.total += 1
                att.score += int(ok)
    db.session.commit()
    from .ml import predictor
    predictor.train()
