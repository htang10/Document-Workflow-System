from datetime import timedelta
from hashlib import sha512
import logging
import secrets
from smtplib import (
    SMTPAuthenticationError,
    SMTPConnectError,
    SMTPException,
)

from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.db import DatabaseError
from django.template.exceptions import TemplateDoesNotExist, TemplateSyntaxError
from django.template.loader import render_to_string
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from authentication.models import User, Token
from authentication.exceptions import (
    EmailVerificationError,
    AlreadyVerifiedError,
)

logger = logging.getLogger(__name__)


def generate_token():
    token = secrets.token_urlsafe(32)
    hashed_token = sha512(token.encode("utf-8")).hexdigest()
    return token, hashed_token


def save_token(hashed_token, user):
    expires_at = timezone.now() + timedelta(hours=24)

    return Token.objects.create(
        user=user,
        token=hashed_token,
        purpose="verification",
        expires_at=expires_at
    )


def send_verification_email(email, token):
    verification_url = f"{settings.FRONTEND_URL}/auth/verify/?token={token}"

    text_content = render_to_string(
        "emails/verification_email.txt",
        context={"verification_url": verification_url}
    )
    html_content = render_to_string(
        "emails/verification_email.html",
        context={"verification_url": verification_url}
    )

    msg = EmailMultiAlternatives(
        subject="Please Activate Your Account",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email],
        body=text_content,
    )
    msg.attach_alternative(html_content, "text/html")

    msg.send()


def handle_email_verification(user):
    # A user may request multiple verification emails
    # Invalidate all previous unused tokens
    Token.objects.filter(
        user=user,
        purpose=Token.Purpose.VERIFICATION,
        used_at__isnull=True
    ).update(expires_at=timezone.now())

    try:
        # The newest token is used for validation
        token, hashed_token = generate_token()
        send_verification_email(user.email, token)
        token_obj = save_token(hashed_token, user)
    except (TemplateDoesNotExist, TemplateSyntaxError) as template_error:
        # Your template is missing or broken
        logger.error(f"Template error: {template_error}")
        raise EmailVerificationError
    except SMTPAuthenticationError as auth_error:
        # Email credentials are wrong
        logger.error(f"Authentication error: {auth_error}")
        raise EmailVerificationError
    except SMTPConnectError as connect_error:
        # Can't reach the mail server
        logger.error(f"Connection error: {connect_error}")
        raise EmailVerificationError
    except SMTPException as unexpected_smtp_error:
        # Catch-all for any other SMTP failure
        logger.error(f"Unexpected error: {unexpected_smtp_error}")
        raise EmailVerificationError
    except DatabaseError as db_error:
        # Token failed to save
        logger.exception(f"Database error: {db_error}")
        raise EmailVerificationError


def resend_verification_email(email):
    user = User.objects.get(email=email)

    if user.email_verified_at:
        raise AlreadyVerifiedError()

    handle_email_verification(user)


def verify_token(token):
    hashed_token = sha512(token.encode("utf-8")).hexdigest()
    token_obj = Token.objects.select_related("user").filter(
        token=hashed_token,
        purpose=Token.Purpose.VERIFICATION,
        used_at__isnull=True,
        expires_at__gt=timezone.now()
    ).first()

    if not token_obj:
        raise ValidationError({"error": "Invalid or expired token."})

    token_obj.used_at = timezone.now()
    token_obj.save()

    token_obj.user.email_verified_at = timezone.now()
    token_obj.user.save()