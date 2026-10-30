def register_blueprints(app):
    from .auth import bp as auth
    from .student import bp as student
    from .quiz import bp as quiz
    from .chatbot import bp as chatbot
    from .teacher import bp as teacher
    from .admin import bp as admin
    from .content import bp as content
    from .resources import bp as resources
    from .integrations import bp as integrations
    for b in (auth, student, quiz, chatbot, teacher, admin, content, resources, integrations):
        app.register_blueprint(b)
