import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "localvelai-production-super-secret-key-chennai-2025")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Database URL with SQLite fallback
    DATABASE_URL = os.environ.get("DATABASE_URL")
    if DATABASE_URL and DATABASE_URL.startswith("mysql"):
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        basedir = os.path.abspath(os.path.dirname(__file__))
        instance_path = os.path.join(basedir, "instance")
        os.makedirs(instance_path, exist_ok=True)
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(instance_path, 'localvelai.db')}"

    # Admin configuration
    raw_admin = os.environ.get("ADMIN_PHONES", "+919876500000")
    ADMIN_PHONES = [p.strip() for p in raw_admin.split(",") if p.strip()]

    # OTP Provider: 'console', 'msg91', 'twilio'
    OTP_PROVIDER = os.environ.get("OTP_PROVIDER", "console").lower()
    
    # Security & Sessions
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None

    # Application constants
    PILOT_AREAS = ["OMR", "Anna Nagar"]
    MAX_SEARCH_RADIUS_KM = 3.0
    BOOST_PRICE_INR = 49
    BOOST_DURATION_HOURS = 24
    REPORTS_AUTO_HIDE_THRESHOLD = 3
    OTP_EXPIRY_MINUTES = 5
    OTP_RESEND_COOLDOWN_SECONDS = 30
    OTP_MAX_ATTEMPTS = 3
    OTP_LOCKOUT_MINUTES = 10

class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    OTP_PROVIDER = "console"
