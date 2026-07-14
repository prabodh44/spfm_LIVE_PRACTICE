"""
Notification helpers.

These functions notify the business owner whenever a new Quote Request or
Contact Message comes in, and send the visitor a confirmation email back.
They are written to fail *safely* in development (no crash if email
credentials aren't configured yet) but genuine send failures are logged and
recorded against the submission (US-6.2 AC: "Delivery failure is logged").

EMAIL
-----
Configured via Django's standard EMAIL_* settings (see settings.py / .env).
Uses Django's send_mail, so any SMTP provider works (Gmail, Zoho, SES, etc).

SMS
---
Uses Twilio (the simplest way to send a real SMS from Django). To enable:
    1. pip install twilio   (already in requirements.txt)
    2. Create a free/paid Twilio account: https://www.twilio.com
    3. Add these to your .env file:
           TWILIO_ACCOUNT_SID=...
           TWILIO_AUTH_TOKEN=...
           TWILIO_FROM_NUMBER=+61...
           OWNER_SMS_NUMBER=+61...
    If these aren't set, SMS sending is simply skipped (logged, not sent) -
    the website will keep working normally either way.
"""

import logging

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def notify_new_quote_request(quote):
    subject = f"New Quote Request from {quote.name}"
    body = (
        f"A new free quote request has been submitted on the website.\n\n"
        f"Name: {quote.name}\n"
        f"Company: {quote.company_name or '(not provided)'}\n"
        f"Phone: {quote.phone or '(not provided)'}\n"
        f"Email: {quote.email or '(not provided)'}\n\n"
        f"Message:\n{quote.message or '(none provided)'}\n"
    )
    sent = _send_owner_email(subject, body)
    if not sent:
        quote.email_send_failed = True
        quote.save(update_fields=["email_send_failed"])

    _send_owner_sms(f"New quote request from {quote.name}. Check your email/admin for details.")

    if quote.email:
        _send_visitor_confirmation(
            to_email=quote.email,
            visitor_name=quote.name,
            subject="We've received your quote request — SP Facilities Management",
            intro="Thanks for requesting a free quote from SP Facilities Management.",
        )


def notify_new_contact_message(message):
    subject = f"New Website Enquiry from {message.name}"
    body = (
        f"A new contact form enquiry has been submitted on the website.\n\n"
        f"Name: {message.name}\n"
        f"Email: {message.email or '(not provided)'}\n"
        f"Phone: {message.phone or '(not provided)'}\n\n"
        f"Message:\n{message.message}\n"
    )
    sent = _send_owner_email(subject, body)
    if not sent:
        message.email_send_failed = True
        message.save(update_fields=["email_send_failed"])

    _send_owner_sms(f"New website enquiry from {message.name}. Check your email/admin.")

    if message.email:
        _send_visitor_confirmation(
            to_email=message.email,
            visitor_name=message.name,
            subject="We've received your message — SP Facilities Management",
            intro="Thanks for getting in touch with SP Facilities Management.",
        )


def _send_owner_email(subject, body):
    """Returns True if the email was sent (or skipped because no recipient
    is configured — that's not a failure). Returns False only on a genuine
    send failure, so callers can flag the submission for manual follow-up.
    """
    recipient = getattr(settings, "OWNER_NOTIFICATION_EMAIL", None)
    if not recipient:
        logger.info("OWNER_NOTIFICATION_EMAIL not set - skipping email notification.")
        return True
    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            fail_silently=False,
        )
        return True
    except Exception:
        logger.exception("Failed to send owner notification email for '%s'.", subject)
        return False


def _send_visitor_confirmation(to_email, visitor_name, subject, intro):
    from .models import SiteSettings

    site = SiteSettings.get_solo()
    body = (
        f"Hi {visitor_name},\n\n"
        f"{intro} We'll be in touch shortly — our typical reply time is within "
        f"one business day.\n\n"
        f"If anything is urgent, call us on {site.phone_display}.\n\n"
        f"— {site.site_name}\n"
    )
    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to_email],
            fail_silently=False,
        )
    except Exception:
        # A failed *confirmation* email to the visitor shouldn't block or
        # alarm anyone — the lead is already saved and the owner has been
        # (or will be) notified. Just log it for visibility.
        logger.exception("Failed to send visitor confirmation email to %s.", to_email)


def _send_owner_sms(text):
    sid = getattr(settings, "TWILIO_ACCOUNT_SID", None)
    token = getattr(settings, "TWILIO_AUTH_TOKEN", None)
    from_number = getattr(settings, "TWILIO_FROM_NUMBER", None)
    to_number = getattr(settings, "OWNER_SMS_NUMBER", None)

    if not all([sid, token, from_number, to_number]):
        logger.info("Twilio SMS not configured - skipping SMS notification.")
        return

    try:
        from twilio.rest import Client  # imported lazily so Twilio is optional

        client = Client(sid, token)
        client.messages.create(body=text, from_=from_number, to=to_number)
    except Exception:
        logger.exception("Failed to send owner notification SMS.")
