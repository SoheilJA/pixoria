from app import db
from datetime import datetime


class Setting(db.Model):
    """Site settings model"""

    __tablename__ = "settings"

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    value = db.Column(db.Text, nullable=False)
    description = db.Column(db.String(255))
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self):
        return f"<Setting {self.key}={self.value}>"

    @staticmethod
    def get_value(key, default=None):
        """Get setting value by key"""
        setting = Setting.query.filter_by(key=key).first()
        if setting:
            # Convert string to boolean for boolean settings
            if setting.value.lower() in ("true", "false"):
                return setting.value.lower() == "true"
            return setting.value
        return default

    @staticmethod
    def set_value(key, value, description=None):
        """Set or update setting value"""
        setting = Setting.query.filter_by(key=key).first()
        if setting:
            setting.value = str(value)
            setting.updated_at = datetime.utcnow()
            if description:
                setting.description = description
        else:
            setting = Setting(key=key, value=str(value), description=description)
            db.session.add(setting)
        db.session.commit()
        return setting

    @staticmethod
    def is_recaptcha_enabled():
        """Check if reCAPTCHA is enabled"""
        from flask import current_app

        db_value = Setting.get_value("recaptcha_enabled")
        if db_value is not None:
            return db_value
        return current_app.config.get("RECAPTCHA_ENABLED", True)
