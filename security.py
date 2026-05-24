"""
Security Utilities Module
Provides cryptographic functions, input validation, CSRF protection, and sanitization.
"""

import os
import re
import secrets
import hashlib
import bcrypt
from datetime import datetime, timedelta
from typing import Tuple, Dict, Optional
import json

# ==================== CSRF TOKEN PROTECTION ====================


class CSRFToken:
    """
    Manages CSRF (Cross-Site Request Forgery) tokens.
    CSRF tokens prevent unauthorized form submissions from other websites.

    How it works:
    1. User loads a page with a form → server generates unique CSRF token
    2. Token is stored in session (server-side)
    3. Form includes the token (client-side)
    4. When form submitted → server validates token matches session
    5. Attacker cannot forge token without access to session
    """

    @staticmethod
    def generate(token_length: int = 32) -> str:
        """
        Generate a cryptographically secure random CSRF token.

        Args:
            token_length: Length of token in bytes (default 32 = 64 hex chars)

        Returns:
            Secure random hex string
        """
        return secrets.token_hex(token_length)

    @staticmethod
    def validate(token: str, session_token: str) -> bool:
        """
        Validate CSRF token against session token using constant-time comparison.
        Uses timing-safe comparison to prevent timing attacks.

        Args:
            token: Token from form submission
            session_token: Token stored in session

        Returns:
            True if tokens match, False otherwise
        """
        return secrets.compare_digest(token, session_token)


# ==================== PASSWORD HASHING WITH SALT & PEPPER ====================


class PasswordSecurity:
    """
    Handles secure password hashing using bcrypt with salt and pepper.

    Security layers:
    1. Salt (16 random bytes): Different for each user, prevents rainbow tables
    2. Pepper (64-char server secret): Not stored in DB, additional protection
    3. Bcrypt (adaptive cost): Stretches hashing time, resists GPU attacks

    Formula: bcrypt(password + salt + pepper)
    """

    @staticmethod
    def hash_password(password: str, pepper: str, salt: Optional[bytes] = None) -> Tuple[str, str]:
        """
        Hash password with bcrypt, salt, and pepper.

        Args:
            password: Plain text password
            pepper: Server-side secret (from config)
            salt: Optional salt (generates new if None)

        Returns:
            Tuple of (hashed_password, salt_hex)
        """
        if not salt:
            salt = os.urandom(16)
        else:
            salt = bytes.fromhex(salt)

        # Combine password + salt + pepper before hashing
        combined = f"{password}{salt.hex()}{pepper}".encode('utf-8')

        # Hash with bcrypt (cost=12 = ~100ms on modern hardware)
        hashed = bcrypt.hashpw(combined, bcrypt.gensalt(rounds=12))

        return hashed.decode('utf-8'), salt.hex()

    @staticmethod
    def verify_password(password: str, hashed: str, salt_hex: str, pepper: str) -> bool:
        """
        Verify password against stored hash.

        Args:
            password: Plain text password to verify
            hashed: Stored bcrypt hash
            salt_hex: Stored salt (hex string)
            pepper: Server-side secret

        Returns:
            True if password matches, False otherwise
        """
        try:
            salt = bytes.fromhex(salt_hex)
            combined = f"{password}{salt_hex}{pepper}".encode('utf-8')
            return bcrypt.checkpw(combined, hashed.encode('utf-8'))
        except Exception:
            return False


# ==================== INPUT VALIDATION & SANITIZATION ====================


class InputValidation:
    """
    Validates and sanitizes user input to prevent:
    - SQL Injection (via parameterized queries + validation)
    - XSS (Cross-Site Scripting) via HTML encoding
    - Command Injection via character whitelisting
    - LDAP Injection via character restrictions
    """

    # Regex patterns for validation
    USERNAME_PATTERN = r'^[a-zA-Z0-9_\-]{3,32}$'  # 3-32 chars, alphanumeric + underscore/dash
    EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'  # RFC 5322 simplified
    PASSWORD_PATTERN = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[a-zA-Z\d@$!%*?&]{12,}$'

    @staticmethod
    def sanitize_string(value: str, max_length: int = 255) -> str:
        """
        Sanitize string input to prevent XSS attacks.
        - Strips whitespace
        - Limits length
        - Encodes HTML special characters

        Args:
            value: Input string
            max_length: Maximum allowed length

        Returns:
            Sanitized string
        """
        # Strip whitespace and limit length
        sanitized = str(value).strip()[:max_length]

        # HTML encode special characters to prevent XSS
        html_escape_table = {
            "&": "&amp;",
            '"': "&quot;",
            "'": "&#x27;",
            ">": "&gt;",
            "<": "&lt;",
        }
        return "".join(html_escape_table.get(c, c) for c in sanitized)

    @staticmethod
    def validate_username(username: str) -> Tuple[bool, str]:
        """
        Validate username format.

        Args:
            username: Username to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not username:
            return False, "Username is required"

        if len(username) < 3:
            return False, "Username must be at least 3 characters"

        if len(username) > 32:
            return False, "Username must be at most 32 characters"

        if not re.match(InputValidation.USERNAME_PATTERN, username):
            return False, "Username can only contain letters, numbers, underscores, and dashes"

        return True, ""

    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """
        Validate email format.

        Args:
            email: Email to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not email:
            return False, "Email is required"

        email = email.lower().strip()

        if len(email) > 254:
            return False, "Email is too long"

        if not re.match(InputValidation.EMAIL_PATTERN, email):
            return False, "Invalid email format"

        return True, ""

    @staticmethod
    def validate_password(password: str) -> Dict[str, any]:
        """
        Validate password strength.

        Requirements:
        - Minimum 12 characters
        - At least one lowercase letter
        - At least one uppercase letter
        - At least one digit
        - At least one special character (@$!%*?&)

        Args:
            password: Password to validate

        Returns:
            Dictionary with validation status and requirements
        """
        result = {
            'is_valid': True,
            'score': 0,
            'requirements': {
                'min_length': len(password) >= 12,
                'uppercase': bool(re.search(r'[A-Z]', password)),
                'lowercase': bool(re.search(r'[a-z]', password)),
                'digit': bool(re.search(r'\d', password)),
                'special_char': bool(re.search(r'[@$!%*?&]', password)),
            }
        }

        # Calculate score
        result['score'] = sum(result['requirements'].values())

        # Validate all requirements met
        result['is_valid'] = all(result['requirements'].values())

        return result


# ==================== RATE LIMITING ====================


class RateLimitTracker:
    """
    Tracks request attempts per IP address for rate limiting.
    Uses in-memory storage (for production, use Redis).

    Why rate limiting matters:
    - Prevents brute force login attacks
    - Prevents account enumeration
    - Prevents email enumeration
    - Protects against DDoS attacks

    This implementation is suitable for small-scale apps.
    For production, integrate with Redis for distributed rate limiting.
    """

    _attempt_tracker: Dict[str, list] = {}  # {ip: [timestamp1, timestamp2, ...]}

    @staticmethod
    def check_rate_limit(
        key: str, max_attempts: int, time_window_seconds: int
    ) -> Tuple[bool, int]:
        """
        Check if request exceeds rate limit.

        Args:
            key: Identifier (IP address for login/register)
            max_attempts: Maximum attempts allowed
            time_window_seconds: Time window in seconds

        Returns:
            Tuple of (is_allowed, attempts_remaining)
        """
        now = datetime.now()
        cutoff_time = now - timedelta(seconds=time_window_seconds)

        # Initialize tracker for this key if needed
        if key not in RateLimitTracker._attempt_tracker:
            RateLimitTracker._attempt_tracker[key] = []

        # Remove old attempts outside time window
        RateLimitTracker._attempt_tracker[key] = [
            timestamp
            for timestamp in RateLimitTracker._attempt_tracker[key]
            if timestamp > cutoff_time
        ]

        # Check if limit exceeded
        current_attempts = len(RateLimitTracker._attempt_tracker[key])
        is_allowed = current_attempts < max_attempts

        return is_allowed, max_attempts - current_attempts

    @staticmethod
    def record_attempt(key: str) -> None:
        """
        Record an attempt for rate limiting.

        Args:
            key: Identifier (IP address)
        """
        if key not in RateLimitTracker._attempt_tracker:
            RateLimitTracker._attempt_tracker[key] = []

        RateLimitTracker._attempt_tracker[key].append(datetime.now())

    @staticmethod
    def reset_attempts(key: str) -> None:
        """
        Reset attempts for an identifier (e.g., after successful login).

        Args:
            key: Identifier (IP address)
        """
        if key in RateLimitTracker._attempt_tracker:
            RateLimitTracker._attempt_tracker[key] = []


# ==================== SECURE TOKEN GENERATION ====================


class TokenGenerator:
    """
    Generates secure tokens for email verification and password reset.
    Tokens include timestamp and are cryptographically secure.
    """

    @staticmethod
    def generate_token() -> str:
        """
        Generate a cryptographically secure random token.
        Used for email verification and password reset links.

        Returns:
            Secure random token
        """
        return secrets.token_urlsafe(32)

    @staticmethod
    def generate_token_hash(token: str) -> str:
        """
        Hash a token for secure storage in database.
        Always hash tokens before storing!

        Args:
            token: Plain text token

        Returns:
            SHA-256 hash of token
        """
        return hashlib.sha256(token.encode()).hexdigest()

    @staticmethod
    def verify_token_hash(token: str, token_hash: str) -> bool:
        """
        Verify token against stored hash using constant-time comparison.

        Args:
            token: Plain text token to verify
            token_hash: Stored token hash

        Returns:
            True if token matches hash
        """
        computed_hash = TokenGenerator.generate_token_hash(token)
        return secrets.compare_digest(computed_hash, token_hash)
