"""
Middleware Module
Handles security headers, HTTPS enforcement, request logging, and error handling.
"""

import logging
import os
from datetime import datetime
from functools import wraps
from flask import request, redirect, g
from logging.handlers import RotatingFileHandler
from config import config

# ==================== LOGGING SETUP ====================


def setup_logging():
    """
    Configure logging with file rotation and timestamps.
    Creates logs/auth.log with automatic rotation when it exceeds max size.

    Logs all:
    - Authentication events (login, register, logout)
    - Failed login attempts
    - Password changes
    - Email verification events
    - Account lockouts
    - Errors and exceptions
    """
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(config.LOG_FILE) or '.', exist_ok=True)

    # Configure logging format
    log_format = logging.Formatter(
        '[%(asctime)s] %(levelname)s - %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Create rotating file handler (rotates when file exceeds max_bytes)
    file_handler = RotatingFileHandler(
        config.LOG_FILE,
        maxBytes=config.LOG_MAX_BYTES,  # 10MB
        backupCount=config.LOG_BACKUP_COUNT  # Keep 10 rotated files
    )
    file_handler.setFormatter(log_format)
    file_handler.setLevel(logging.INFO)

    # Create console handler for development
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)
    console_handler.setLevel(logging.WARNING)

    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logging.getLogger(__name__)


logger = setup_logging()


# ==================== SECURITY HEADERS MIDDLEWARE ====================


def add_security_headers(response):
    """
    Add security headers to all responses.
    Middleware that attaches security headers to every HTTP response.

    Headers protect against:
    - XSS (Content-Security-Policy, X-Content-Type-Options)
    - Clickjacking (X-Frame-Options)
    - MIME-sniffing (X-Content-Type-Options)
    - Weak HTTPS (Strict-Transport-Security)
    """

    # Prevent MIME-sniffing attacks
    # Forces browser to respect Content-Type header instead of guessing
    response.headers['X-Content-Type-Options'] = 'nosniff'

    # Prevent clickjacking attacks
    # DENY: Page cannot be displayed in frame/iframe from other domain
    response.headers['X-Frame-Options'] = 'DENY'

    # Referrer Policy: Control how much referrer info is shared
    # strict-origin-when-cross-origin: Send referrer only on same-site, origin-only for cross-site
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'

    # Content Security Policy (CSP): Restrict resources to prevent XSS
    # default-src 'self': Only allow resources from same origin by default
    # script-src 'self': Only allow scripts from same origin (prevents injected scripts)
    # style-src 'self' 'unsafe-inline': Allow styles from same origin + inline styles
    # img-src 'self' data:: Allow images from same origin + data URIs
    csp = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "font-src 'self'; "
        "connect-src 'self';"
    )
    response.headers['Content-Security-Policy'] = csp

    # HSTS (HTTP Strict Transport Security)
    # Forces browser to use HTTPS for all future connections
    # max-age: Duration in seconds to enforce HTTPS (31536000 = 1 year)
    # includeSubDomains: Apply to all subdomains
    # preload: Allow submission to HSTS preload list for browsers
    hsts_value = f"max-age={config.HSTS_MAX_AGE}"
    if config.HSTS_INCLUDE_SUBDOMAINS:
        hsts_value += "; includeSubDomains"
    hsts_value += "; preload"
    response.headers['Strict-Transport-Security'] = hsts_value

    # Prevent exposing server info
    response.headers['Server'] = 'SecureAuth'

    # Disable caching for sensitive pages
    if 'dashboard' in request.path or 'reset-password' in request.path:
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'

    return response


# ==================== HTTPS ENFORCEMENT ====================


def enforce_https(f):
    """
    Decorator to enforce HTTPS in production.
    Redirects all HTTP requests to HTTPS.

    Why HTTPS is critical:
    - Encrypts data in transit (prevents man-in-the-middle attacks)
    - Verifies server identity (prevents DNS hijacking)
    - Prevents session hijacking
    - Required for secure cookies (HttpOnly + Secure flags)
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if config.ENFORCE_HTTPS and not request.is_secure:
            # Build HTTPS URL
            url = request.url.replace('http://', 'https://', 1)
            logger.warning(f"Redirecting HTTP request to HTTPS: {request.path}")
            return redirect(url, code=301)
        return f(*args, **kwargs)

    return decorated_function


# ==================== REQUEST LOGGING ====================


def log_request(f):
    """
    Decorator to log authentication-related requests.
    Records IP address, request path, method, and user info if available.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.remote_addr
        method = request.method
        path = request.path

        # Log authentication events
        if 'login' in path or 'register' in path or 'logout' in path:
            if method == 'POST':
                username = request.form.get('username', 'unknown')
                logger.info(f"[{method}] {path} - IP: {client_ip} - Username: {username}")
            else:
                logger.info(f"[{method}] {path} - IP: {client_ip}")

        return f(*args, **kwargs)

    return decorated_function


# ==================== ERROR LOGGING ====================


def log_failed_login(username: str, ip_address: str, reason: str = "Invalid credentials"):
    """
    Log failed login attempts for security monitoring.

    Args:
        username: Username that failed to login
        ip_address: IP address of the attempt
        reason: Reason for failure
    """
    logger.warning(f"Failed login attempt - Username: {username}, IP: {ip_address}, Reason: {reason}")


def log_account_locked(username: str, ip_address: str):
    """
    Log account lockout events.

    Args:
        username: Username of locked account
        ip_address: IP address that triggered lockout
    """
    logger.warning(f"Account locked - Username: {username}, IP: {ip_address}, Lockout Duration: 30 minutes")


def log_email_verification(username: str, email: str, verified: bool):
    """
    Log email verification events.

    Args:
        username: Username
        email: Email address
        verified: Whether email was verified
    """
    status = "VERIFIED" if verified else "SENT"
    logger.info(f"Email verification {status} - Username: {username}, Email: {email}")


def log_password_reset(username: str, method: str):
    """
    Log password reset events.

    Args:
        username: Username
        method: "REQUESTED" or "COMPLETED"
    """
    logger.info(f"Password reset {method} - Username: {username}")


def log_security_event(event_type: str, username: str, details: str):
    """
    Log general security events.

    Args:
        event_type: Type of security event
        username: Username involved
        details: Additional details
    """
    logger.warning(f"Security Event - Type: {event_type}, Username: {username}, Details: {details}")


# ==================== REQUEST CONTEXT ====================


def before_request():
    """
    Store request metadata in Flask's g object for use in route handlers.
    Called before each request.
    """
    g.start_time = datetime.now()
    g.client_ip = request.remote_addr
    g.request_path = request.path


def after_request(response):
    """
    Log request completion and add security headers.
    Called after each request.
    """
    # Calculate request duration
    if hasattr(g, 'start_time'):
        duration = (datetime.now() - g.start_time).total_seconds()
        logger.debug(f"Request completed - Path: {g.request_path}, Duration: {duration:.3f}s, Status: {response.status_code}")

    # Add security headers
    return add_security_headers(response)
