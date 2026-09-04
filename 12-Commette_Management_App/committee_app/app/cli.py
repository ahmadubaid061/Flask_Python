import click
from app.extensions import db
from app.models.admin import Admin


def register_commands(app):
    """Register CLI commands for the Flask app."""

    @app.cli.command()
    @click.option("--username", prompt="Admin username", help="Username for the admin account")
    @click.option("--email", prompt="Admin email", help="Email for the admin account")
    @click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True, help="Password for the admin account")
    def create_admin(username, email, password):
        """Create a new admin user manually."""
        with app.app_context():
            # Check if admin already exists
            existing = Admin.query.filter_by(username=username).first()
            if existing:
                click.echo(f"❌ Admin with username '{username}' already exists!")
                return

            existing_email = Admin.query.filter_by(email=email).first()
            if existing_email:
                click.echo(f"❌ Admin with email '{email}' already exists!")
                return

            # Create new admin
            admin = Admin(username=username, email=email)
            admin.set_password(password)
            
            db.session.add(admin)
            db.session.commit()
            
            click.echo(f"✅ Admin '{username}' created successfully!")
            click.echo(f"   Email: {email}")
            click.echo(f"   ID: {admin.id}")

    @app.cli.command()
    def list_admins():
        """List all admin users in database."""
        with app.app_context():
            admins = Admin.query.all()
            if not admins:
                click.echo("❌ No admin users found in database!")
                return
            
            click.echo("\n📋 Registered Admins:")
            click.echo("─" * 70)
            for admin in admins:
                click.echo(f"  ID:       {admin.id}")
                click.echo(f"  Username: {admin.username}")
                click.echo(f"  Email:    {admin.email}")
                click.echo(f"  Created:  {admin.created_at}")
                click.echo("─" * 70)

    @app.cli.command()
    @click.option("--username", prompt="Admin username to delete", help="Username to remove")
    def delete_admin(username):
        """Delete an admin user."""
        with app.app_context():
            admin = Admin.query.filter_by(username=username).first()
            if not admin:
                click.echo(f"❌ Admin '{username}' not found!")
                return

            if click.confirm(f"⚠️  Delete admin '{username}'? This cannot be undone."):
                db.session.delete(admin)
                db.session.commit()
                click.echo(f"✅ Admin '{username}' deleted successfully!")
            else:
                click.echo("❌ Deletion cancelled.")

    @app.cli.command()
    @click.option("--username", prompt="Admin username", help="Username to reset password for")
    @click.option("--new-password", prompt=True, hide_input=True, confirmation_prompt=True, help="New password")
    def reset_password(username, new_password):
        """Reset an admin's password."""
        with app.app_context():
            admin = Admin.query.filter_by(username=username).first()
            if not admin:
                click.echo(f"❌ Admin '{username}' not found!")
                return

            admin.set_password(new_password)
            db.session.commit()
            click.echo(f"✅ Password for '{username}' reset successfully!")

    @app.cli.command()
    def init_admin_from_env():
        """Manually initialize admin from .env file."""
        with app.app_context():
            username = app.config.get("ADMIN_USERNAME")
            password = app.config.get("ADMIN_PASSWORD")
            email = app.config.get("ADMIN_EMAIL_FOR_LOGIN")
            
            if not all([username, password, email]):
                click.echo("❌ Missing credentials in .env file!")
                click.echo("   Required: ADMIN_USERNAME, ADMIN_PASSWORD, ADMIN_EMAIL_FOR_LOGIN")
                return
            
            existing = Admin.query.filter_by(username=username).first()
            if existing:
                click.echo(f"❌ Admin '{username}' already exists!")
                return
            
            admin = Admin(username=username, email=email)
            admin.set_password(password)
            db.session.add(admin)
            db.session.commit()
            
            click.echo(f"✅ Admin initialized from .env!")
            click.echo(f"   Username: {username}")
            click.echo(f"   Email: {email}")