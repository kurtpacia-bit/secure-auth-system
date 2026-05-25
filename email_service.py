"""
Email Service Module
Handles sending verification emails and password reset emails securely.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from typing import Tuple
from config import config

logger = logging.getLogger(__name__)


class EmailService:
    """
    Handles sending emails for:
    1. Email verification on signup
    2. Password reset notifications
    3. Account locked warnings
    4. Suspicious activity alerts

    Uses SMTP with TLS encryption for secure email transmission.
    """

    @staticmethod
    def send_verification_email(user_email: str, username: str, verification_link: str) -> Tuple[bool, str]:
        """
        Send email verification link to new user.

        Args:
            user_email: Recipient email
            username: User's username
            verification_link: Full URL to verification link

        Returns:
            Tuple of (success, message)
        """
        try:
            subject = "Verify Your Email - SecureAuth"
            
            # HTML email template with verification button
            html_body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; color: #333;">
                    <div style="background-color: #f5f5f5; padding: 20px; border-radius: 8px;">
                        <h2 style="color: #2c3e50;">Welcome to SecureAuth, {username}!</h2>
                        <p>Thank you for signing up. Please verify your email address to activate your account.</p>
                        
                        <p>
                            <a href="{verification_link}" 
                               style="display: inline-block; background-color: #3498db; color: white; 
                                      padding: 12px 24px; text-decoration: none; border-radius: 4px;">
                                Verify Email
                            </a>
                        </p>
                        
                        <p style="color: #7f8c8d; font-size: 12px;">
                            Or copy and paste this link: {verification_link}
                        </p>
                        
                        <p style="color: #e74c3c; font-size: 12px;">
                            <strong>This link expires in 24 hours.</strong>
                        </p>
                        
                        <p style="color: #7f8c8d; font-size: 12px;">
                            If you didn't create this account, please ignore this email.
                        </p>
                    </div>
                </body>
            </html>
            """
            
            # Plain text fallback
            text_body = f"""
Welcome to SecureAuth, {username}!

Thank you for signing up. Please verify your email address to activate your account.

Verification Link: {verification_link}

This link expires in 24 hours.

If you didn't create this account, please ignore this email.
            """

            return EmailService._send_email(user_email, subject, text_body, html_body)

        except Exception as e:
            logger.error(f"Failed to send verification email to {user_email}: {str(e)}")
            return False, "Failed to send verification email. Please try again later."

    @staticmethod
    def send_password_reset_email(user_email: str, username: str, reset_link: str) -> Tuple[bool, str]:
        """
        Send password reset link to user.

        Args:
            user_email: Recipient email
            username: User's username
            reset_link: Full URL to password reset form

        Returns:
            Tuple of (success, message)
        """
        try:
            subject = "Reset Your Password - SecureAuth"
            
            html_body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; color: #333;">
                    <div style="background-color: #f5f5f5; padding: 20px; border-radius: 8px;">
                        <h2 style="color: #2c3e50;">Password Reset Request</h2>
                        <p>Hi {username},</p>
                        <p>We received a request to reset your password. Click the button below to create a new password.</p>
                        
                        <p>
                            <a href="{reset_link}" 
                               style="display: inline-block; background-color: #e74c3c; color: white; 
                                      padding: 12px 24px; text-decoration: none; border-radius: 4px;">
                                Reset Password
                            </a>
                        </p>
                        
                        <p style="color: #7f8c8d; font-size: 12px;">
                            Or copy and paste: {reset_link}
                        </p>
                        
                        <p style="color: #e74c3c; font-size: 12px;">
                            <strong>This link expires in 1 hour.</strong>
                        </p>
                        
                        <p style="color: #7f8c8d; font-size: 12px;">
                            If you didn't request this, please ignore this email. Your password is safe.
                        </p>
                    </div>
                </body>
            </html>
            """
            
            text_body = f"""
Password Reset Request

Hi {username},

We received a request to reset your password. Click the link below to create a new password.

Reset Link: {reset_link}

This link expires in 1 hour.

If you didn't request this, please ignore this email. Your password is safe.
            """

            return EmailService._send_email(user_email, subject, text_body, html_body)

        except Exception as e:
            logger.error(f"Failed to send password reset email to {user_email}: {str(e)}")
            return False, "Failed to send password reset email. Please try again later."

    @staticmethod
    def send_account_locked_email(user_email: str, username: str) -> Tuple[bool, str]:
        """
        Send notification that account has been locked due to suspicious activity.

        Args:
            user_email: Recipient email
            username: User's username

        Returns:
            Tuple of (success, message)
        """
        try:
            subject = "Account Locked - SecureAuth"
            
            html_body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; color: #333;">
                    <div style="background-color: #fff3cd; padding: 20px; border-radius: 8px; border-left: 4px solid #ffc107;">
                        <h2 style="color: #856404;">Account Temporarily Locked</h2>
                        <p>Hi {username},</p>
                        <p>Your account has been temporarily locked after too many failed login attempts.</p>
                        
                        <p style="color: #856404;">
                            <strong>Your account will be unlocked in 30 minutes.</strong>
                        </p>
                        
                        <p>If this wasn't you, please:</p>
                        <ul>
                            <li>Reset your password immediately</li>
                            <li>Enable two-factor authentication</li>
                            <li>Contact our support team</li>
                        </ul>
                        
                        <p style="color: #7f8c8d; font-size: 12px;">
                            Questions? Contact security@secureauth.com
                        </p>
                    </div>
                </body>
            </html>
            """
            
            text_body = f"""
Account Temporarily Locked

Hi {username},

Your account has been temporarily locked after too many failed login attempts.

Your account will be unlocked in 30 minutes.

If this wasn't you, please:
- Reset your password immediately
- Enable two-factor authentication
- Contact our support team

Questions? Contact security@secureauth.com
            """

            return EmailService._send_email(user_email, subject, text_body, html_body)

        except Exception as e:
            logger.error(f"Failed to send account locked email to {user_email}: {str(e)}")
            return False, "Failed to send notification email."

    @staticmethod
    def _send_email(recipient: str, subject: str, text_body: str, html_body: str) -> Tuple[bool, str]:
        """
        Internal method to send email via SMTP.
        Uses TLS encryption for security.

        Args:
            recipient: Recipient email address
            subject: Email subject
            text_body: Plain text email body
            html_body: HTML email body

        Returns:
            Tuple of (success, message)
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{config.EMAIL_FROM_NAME} <{config.EMAIL_FROM}>"
            msg['To'] = recipient

            # Attach both text and HTML versions
            msg.attach(MIMEText(text_body, 'plain'))
            msg.attach(MIMEText(html_body, 'html'))

            # Connect to SMTP server with TLS and timeout
            with smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT, timeout=10) as server:
                server.starttls()  # Encrypt connection
                server.login(config.SMTP_USERNAME, config.SMTP_PASSWORD)
                server.sendmail(config.EMAIL_FROM, recipient, msg.as_string())

            logger.info(f"Email sent successfully to {recipient}")
            return True, "Email sent successfully"

        except smtplib.SMTPAuthenticationError:
            logger.error("SMTP authentication failed. Check SMTP credentials.")
            return False, "Email service temporarily unavailable"
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {str(e)}")
            return False, "Failed to send email. Please try again later."
        except Exception as e:
            logger.error(f"Unexpected error sending email: {str(e)}")
            return False, "Failed to send email. Please try again later."
