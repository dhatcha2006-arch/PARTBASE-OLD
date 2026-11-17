import os
from flask import Flask, render_template, request, session, redirect, url_for, flash
from config import Config
from app.extensions import db, migrate, csrf, limiter

def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    # Ensure instance directory exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    limiter.init_app(app)

    # Register blueprints
    from app.blueprints.auth import auth_bp
    from app.blueprints.seeker import seeker_bp
    from app.blueprints.employer import employer_bp
    from app.blueprints.admin import admin_bp
    from app.blueprints.support import support_bp
    from app.blueprints.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(seeker_bp, url_prefix="/seeker")
    app.register_blueprint(employer_bp, url_prefix="/employer")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(support_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    # Global context processor
    @app.context_processor
    def inject_globals():
        from app.models import User, Area
        from app.utils.helpers import mask_phone
        user = None
        user_id = session.get("user_id")
        if user_id:
            user = User.query.get(user_id)
        areas = Area.query.order_by(Area.name).all() if db.engine else []
        return {
            "current_user": user,
            "active_role": session.get("role", "seeker"),
            "is_admin": session.get("is_admin", False),
            "all_areas": areas,
            "mask_phone": mask_phone,
            "pilot_areas": app.config.get("PILOT_AREAS", ["OMR", "Anna Nagar"])
        }

    # User active block check
    @app.before_request
    def check_user_status():
        user_id = session.get("user_id")
        if user_id:
            from app.models import User
            user = User.query.get(user_id)
            if user and user.is_blocked:
                session.clear()
                flash("Your account has been suspended for safety violations. Please contact support.", "danger")
                return redirect(url_for("auth.login"))

    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        if request.path.startswith("/api/"):
            return {"ok": False, "error": "Not Found", "message": "The requested API endpoint was not found."}, 404
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        if request.path.startswith("/api/"):
            return {"ok": False, "error": "Server Error", "message": "An internal server error occurred."}, 500
        return render_template("errors/500.html"), 500

    # Initialize tables automatically for SQLite / local development
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            app.logger.warning(f"Could not auto-create tables: {e}")

    return app
