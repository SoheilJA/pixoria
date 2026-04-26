import os
from datetime import timedelta
from dotenv import load_dotenv


# load environment variables
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


class Config:
    """Base configuration"""

    # Flask
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key-change-in-production"

    # SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # تصحیح typo
    SQLALCHEMY_ECHO = False

    # JWT
    JWT_SECRET_KEY = (
        os.environ.get("JWT_SECRET_KEY") or "jwt-secret-key-change-in-production"
    )
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_COOKIE_SECURE = False  # true in production with HTTPS
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_COOKIE_SAMESITE = "Lax"
    JWT_ACCESS_COOKIE_NAME = "access_token"
    JWT_REFRESH_COOKIE_NAME = "refresh_token"

    # reCAPTCHA
    RECAPTCHA_SITE_KEY = os.environ.get("RECAPTCHA_SITE_KEY")
    RECAPTCHA_SECRET_KEY = os.environ.get("RECAPTCHA_SECRET_KEY")
    # Default از env می‌خونه، ولی در runtime از دیتابیس چک می‌شه
    RECAPTCHA_ENABLED = os.environ.get("RECAPTCHA_ENABLED", "True").lower() == "true"

    # Rate Limiting
    RATELIMIT_STORAGE_URL = os.environ.get("RATELIMIT_STORAGE_URL", "memory://")
    RATELIMIT_DEFAULT = "200 per day, 50 per hour"
    RATELIMIT_HEADERS_ENABLED = True  # تصحیح typo

    # Upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join(basedir, "app/static/uploads")
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

    # Pagination
    ITEMS_PER_PAGE = 20

    # Admin
    SUPER_ADMIN_USERNAME = os.environ.get("SUPER_ADMIN_USERNAME", "admin")
    SUPER_ADMIN_PASSWORD = os.environ.get(
        "SUPER_ADMIN_PASSWORD", "change-this-password"
    )


class DevelopmentConfig(Config):
    """Development configuration"""

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DEV_DATABASE_URL")
        or f'sqlite:///{os.path.join(basedir, "instance", "seo_ran_dev.db")}'
    )
    SQLALCHEMY_ECHO = True
    JWT_COOKIE_SECURE = False


class ProductionConfig(Config):
    """Production configuration"""

    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")  # تصحیح typo
    SQLALCHEMY_ECHO = False
    JWT_COOKIE_SECURE = True
    JWT_COOKIE_SAMESITE = "Strict"

    # Production must have these set
    @classmethod
    def init_app(cls, app):
        # Ensure critical settings are configured
        assert os.environ.get("SECRET_KEY"), "SECRET_KEY must be set in production"
        assert os.environ.get(
            "JWT_SECRET_KEY"
        ), "JWT_SECRET_KEY must be set in production"
        assert os.environ.get("DATABASE_URL"), "DATABASE_URL must be set in production"


class TestingConfig(Config):
    """Testing configuration"""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    RECAPTCHA_ENABLED = False


# Configuration dictionary
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
