"""
Configuration Module
Centralizes all configuration, environment validation, and security settings.
Ensures all required environment variables are present on startup.
"""

import os
import sys
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class ConfigValidator:
    """
    Validates all required environment variables on application startup.
    This prevents runtime errors and ensures secure configuration.
    """

    REQUIRED_VARS = {
        # Flask Configuration
        'SECRET_KEY': 'Flask session encryption key (min 32 chars)',
        'FLASK_ENV': 'Environment: production or development',

        # Supabase Configuration
        'SUPABASE_URL': 'Supabase project URL',
        'SUPABASE_KEY': 'Supabase anon key for client requests',
        'SUPABASE_SERVICE_ROLE_KEY': 'Supabase service role key (admin access)',

        # Security Configuration
        'PEPPER': 'Pepper for password hashing (64-char hex string)',

        # Email Configuration
        'SMTP_SERVER': 'SMTP server for sending emails',
        'SMTP_USERNAME': 'SMTP username/email',
        'SMTP_PASSWORD': 'SMTP password or app-specific password',
        'EMAIL_FROM': 'Email address to send from',
    }

    @staticmethod
    def validate():
        """
        Validate all required environment variables.
        Raises SystemExit if any required variable is missing.
        """
        missing_vars = []

        for var_name, description in ConfigValidator.REQUIRED_VARS.items():
            if not os.getenv(var_name):
                missing_vars.append(f"  • {var_name}: {description}")

        if missing_vars:
            print("\n" + "=" * 70)
            print("❌ CONFIGURATION ERROR: Missing Required Environment Variables")
            print("=" * 70)
            print("\nThe following environment variables are required:\n")
            for var in missing_vars:
                print(var)
            print("\n" + "=" * 70)
            print("Please create a .env file with all required variables.")
            print("See .env.example for the complete list.")
            print("=" * 70 + "\n")
            sys.exit(1)

        print("✅ All required environment variables validated")


class Config:
    """
    Base configuration class with security settings.
    This is inherited by production and development configurations.
    """

    # ==================== FLASK CONFIGURATION ====================
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    PERMANENT_SESSION_LIFETIME = timedelta(
        minutes=int(os.getenv('SESSION_TIMEOUT', 30))
    )
    SESSION_COOKIE_SECURE = True  # Only send cookies over HTTPS
    SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to session cookie
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection

    # ==================== SECURITY HEADERS ====================
    # Content Security Policy: Restrict resources to prevent XSS attacks
    CSP_POLICY = {
        'default-src': "'self'",
        'script-src': "'self' 'unsafe-inline'",  # For inline form scripts
        'style-src': "'self' 'unsafe-inline'",  # For inline CSS
        'img-src': "'self' data:",
        'font-src': "'self'",
        'connect-src': "'self'",
    }

    # HSTS (HTTP Strict Transport Security)
    HSTS_MAX_AGE = int(os.getenv('HSTS_MAX_AGE', 31536000))  # 1 year
    HSTS_INCLUDE_SUBDOMAINS = os.getenv('HSTS_INCLUDE_SUBDOMAINS', 'True') == 'True'
    HSTS_PRELOAD = True

    # Prevent clickjacking attacks
    X_FRAME_OPTIONS = 'DENY'

    # Prevent MIME-sniffing attacks
    X_CONTENT_TYPE_OPTIONS = 'nosniff'

    # Referrer Policy
    REFERRER_POLICY = 'strict-origin-when-cross-origin'

    # ==================== SUPABASE CONFIGURATION ====================
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')
    SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

    # ==================== SECURITY CONFIGURATION ====================
    # Pepper: Additional secret for password hashing (should be 64 hex chars)
    PEPPER = os.getenv('PEPPER', '')

    # CSRF Configuration
    CSRF_TOKEN_LENGTH = int(os.getenv('CSRF_TOKEN_LENGTH', 32))

    # Password Requirements
    PASSWORD_MIN_LENGTH = 12
    PASSWORD_REQUIRE_UPPERCASE = True
    PASSWORD_REQUIRE_LOWERCASE = True
    PASSWORD_REQUIRE_DIGIT = True
    PASSWORD_REQUIRE_SPECIAL = True

    # ==================== RATE LIMITING CONFIGURATION ====================
    # Login attempts: max 5 attempts per 15 minutes per IP
    RATELIMIT_LOGIN = os.getenv('RATE_LIMIT_LOGIN', '5 per 15 minutes')

    # Registration: max 3 attempts per 1 hour per IP
    RATELIMIT_REGISTER = os.getenv('RATE_LIMIT_REGISTER', '3 per 1 hour')

    # API requests: max 100 requests per hour per IP
    RATELIMIT_API = os.getenv('RATE_LIMIT_API', '100 per 1 hour')

    # ==================== ACCOUNT LOCKOUT CONFIGURATION ====================
    MAX_LOGIN_ATTEMPTS = int(os.getenv('MAX_LOGIN_ATTEMPTS', 5))
    LOCKOUT_DURATION = int(os.getenv('LOCKOUT_DURATION', 1800))  # 30 minutes

    # ==================== EMAIL CONFIGURATION ====================
    SMTP_SERVER = os.getenv('SMTP_SERVER')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
    EMAIL_FROM = os.getenv('EMAIL_FROM')
    EMAIL_FROM_NAME = os.getenv('EMAIL_FROM_NAME', 'SecureAuth')

    # ==================== TOKEN CONFIGURATION ====================
    VERIFICATION_TOKEN_EXPIRY = int(os.getenv('VERIFICATION_TOKEN_EXPIRY', 24))  # hours
    PASSWORD_RESET_TOKEN_EXPIRY = int(
        os.getenv('PASSWORD_RESET_TOKEN_EXPIRY', 1)
    )  # hours

    # ==================== HTTPS CONFIGURATION ====================
    ENFORCE_HTTPS = os.getenv('ENFORCE_HTTPS', 'True') == 'True'

    # ==================== LOGGING CONFIGURATION ====================
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/auth.log')
    LOG_MAX_BYTES = int(os.getenv('LOG_MAX_BYTES', 10485760))  # 10MB
    LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', 10))


class DevelopmentConfig(Config):
    """Development configuration - less strict security for debugging."""
    DEBUG = True
    TESTING = False
    SESSION_COOKIE_SECURE = False  # Allow HTTP in development
    ENFORCE_HTTPS = False


class ProductionConfig(Config):
    """Production configuration - maximum security enforcement."""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    ENFORCE_HTTPS = True


class TestingConfig(Config):
    """Testing configuration - for unit and integration tests."""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


# Get the appropriate configuration based on environment
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
if FLASK_ENV == 'production':
    config = ProductionConfig()
elif FLASK_ENV == 'testing':
    config = TestingConfig()
else:
    config = DevelopmentConfig()
