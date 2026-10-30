import click
from .extensions import db


def register_cli(app):
    @app.cli.command("seed")
    @click.option("--reset", is_flag=True, help="Drop all tables first")
    def seed_cmd(reset):
        """Create demo users, topics, questions, resources and sample history."""
        from .seed import seed
        if reset:
            db.drop_all()
            db.create_all()
        seed()
        click.echo("Seed complete. Demo logins: admin@demo.com / teacher@demo.com / student@demo.com  (password: Password123)")

    @app.cli.command("train-model")
    def train_cmd():
        """Train the weakness-prediction model from stored answer history."""
        from .ml import predictor
        click.echo(predictor.train())

    @app.cli.command("create-admin")
    @click.option("--name", prompt=True)
    @click.option("--email", prompt=True)
    @click.password_option()
    def create_admin(name, email, password):
        """Create an admin account (use this in production instead of demo seed)."""
        from .models import User
        if User.query.filter_by(email=email.lower()).first():
            raise click.ClickException("Email already exists")
        u = User(name=name, email=email.lower(), role="admin")
        u.set_password(password)
        db.session.add(u)
        db.session.commit()
        click.echo("Admin created.")
