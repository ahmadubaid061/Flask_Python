import click
from flask.cli import with_appcontext

from app.extensions import db
from app.models.admin import Admin


@click.command("create-admin")
@click.option("--username", prompt=True)
@click.option("--email", prompt=True)
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
@with_appcontext
def create_admin(username, email, password):
    """Create an admin account: flask create-admin"""
    if Admin.query.filter((Admin.username == username) | (Admin.email == email)).first():
        click.echo("An admin with that username or email already exists.")
        return

    admin = Admin(username=username, email=email)
    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()
    click.echo(f"Admin '{username}' created.")


def register_commands(app):
    app.cli.add_command(create_admin)
