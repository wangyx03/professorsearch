
from flask import Flask, jsonify, render_template
from flask_login import login_required, current_user

from config import Config
from auth.auth import auth_bp, login_manager
from services.database import test_connection

from flask import Flask, jsonify, render_template, request, redirect, url_for, flash
from services.student import get_students, create_student, update_student

import json
from services.module import get_modules, create_module, update_module

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Session security settings
    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=False,  # Set True when using HTTPS
        PERMANENT_SESSION_LIFETIME=86400,
    )

    # Initialize Flask-Login
    login_manager.init_app(app)

    # Register authentication routes
    app.register_blueprint(auth_bp)

    # Home page
    @app.route("/")
    @login_required
    def index():
        return render_template("dashboard.html")
         
    # Database connection test (login required)
    @app.route("/health")
    @login_required
    def health():
        try:
            database, tables = test_connection()

            return jsonify({
                "status": "ok",
                "database": database,
                "tables": tables,
            })

        except Exception:
            app.logger.exception("Database health check failed")

            return jsonify({
                "status": "error",
                "message": "Database connection failed",
            }), 503

    # student info
    
    @app.route("/students", methods=["GET", "POST"])
    @login_required
    def students():
        if request.method == "POST":
            try:
                create_student(
                    full_name=request.form.get("full_name", ""),
                    email=request.form.get("email", "").strip(),
                    phone=request.form.get("phone", "").strip(),
                    wechat_id=request.form.get("wechat_id", "").strip(),
                    notes=request.form.get("notes", "").strip(),
                )

                flash("Student created successfully.", "success")

            except ValueError as e:
                flash(str(e), "error")

            return redirect(url_for("students"))

        student_list = get_students()

        return render_template(
            "students.html",
            students=student_list,
        )

    
    @app.route("/students/<int:student_id>/update", methods=["POST"])
    @login_required
    def update_student_route(student_id):
        try:
            updated = update_student(
                student_id=student_id,
                full_name=request.form.get("full_name", ""),
                email=request.form.get("email", "").strip(),
                phone=request.form.get("phone", "").strip(),
                wechat_id=request.form.get("wechat_id", "").strip(),
                notes=request.form.get("notes", "").strip(),
            )

            if not updated:
                return jsonify({
                    "success": False,
                    "message": "Student not found."
                }), 404

            return jsonify({
                "success": True,
                "message": "Student updated successfully."
            })

        except ValueError as e:
            return jsonify({
                "success": False,
                "message": str(e)
            }), 400

    
    @app.route("/modules", methods=["GET", "POST"])
    @login_required
    def modules():
        if request.method == "POST":
            try:
                create_module(
                    module_id=request.form.get("module_id", ""),
                    module_name=request.form.get("module_name", ""),
                    description=request.form.get("description", ""),
                    instructions=request.form.get("instructions", ""),
                    enabled=request.form.get("enabled") == "on",
                    is_core=request.form.get("is_core") == "on",
                    sort_order=int(request.form.get("sort_order", 100)),
                    output_type=request.form.get("output_type", "json"),
                )

                flash("Module created successfully.", "success")

            except (ValueError, TypeError) as e:
                flash(f"Failed to create module: {e}", "error")

            return redirect(url_for("modules"))

        return render_template(
            "modules.html",
            modules=get_modules(),
        )




    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
    )
