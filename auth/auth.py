
from datetime import datetime, timezone

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from sqlalchemy import text
from werkzeug.security import check_password_hash

from services.database import SessionLocal


auth_bp = Blueprint("auth", __name__)
login_manager = LoginManager()
login_manager.login_view = "auth.login"


class User(UserMixin):
    def __init__(self, user_id, username, is_active=True):
        self.id = str(user_id)
        self.username = username
        self.active = bool(is_active)

    @property
    def is_active(self):
        return self.active


@login_manager.user_loader
def load_user(user_id):
    with SessionLocal() as db:
        row = db.execute(
            text("""
                SELECT user_id, username, is_active
                FROM users
                WHERE user_id = :user_id
            """),
            {"user_id": user_id},
        ).mappings().first()

    if not row or not row["is_active"]:
        return None

    return User(
        row["user_id"],
        row["username"],
        row["is_active"],
    )


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        with SessionLocal() as db:
            row = db.execute(
                text("""
                    SELECT user_id, username, password_hash, is_active
                    FROM users
                    WHERE username = :username
                """),
                {"username": username},
            ).mappings().first()

            if (
                row
                and row["is_active"]
                and check_password_hash(row["password_hash"], password)
            ):
                user = User(
                    row["user_id"],
                    row["username"],
                )

                login_user(user)

                db.execute(
                    text("""
                        UPDATE users
                        SET last_login_at = :login_time
                        WHERE user_id = :user_id
                    """),
                    {
                        "login_time": datetime.now(timezone.utc).replace(
                            tzinfo=None
                        ),
                        "user_id": row["user_id"],
                    },
                )
                db.commit()

                return redirect(url_for("index"))

        flash("Invalid username or password.", "error")

    return render_template("login.html")


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
