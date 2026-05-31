import africastalking
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

# Initialise Africa's Talking once at module load
africastalking.initialize(
    username=settings.AT_USERNAME,
    api_key=settings.AT_API_KEY,
)
sms = africastalking.SMS


def _send(phone: str, message: str, sms_type: str = 'alert') -> dict:
    """Low-level send. Logs to sms_logs table and returns AT response."""
    from core.models import SMSLog  # avoid circular import
    log = SMSLog.objects.create(
        recipient=phone,
        message=message,
        type=sms_type,
        status='pending',
    )
    try:
        response = sms.send(message, [phone], sender_id=settings.AT_SENDER_ID)
        recipients = response.get('SMSMessageData', {}).get('Recipients', [])
        at_id = recipients[0].get('messageId', '') if recipients else ''
        log.at_message_id = at_id
        log.status = 'sent'
        log.save(update_fields=['at_message_id', 'status'])
        logger.info(f'SMS sent to {phone} [{sms_type}]')
        return response
    except Exception as e:
        log.status = 'failed'
        log.save(update_fields=['status'])
        logger.error(f'SMS failed to {phone}: {e}')
        return {}


def send_session_confirmation_sms(phone: str, counselor_name: str, scheduled_at) -> None:
    """Sent to a user after they book a counseling session."""
    formatted = scheduled_at.strftime('%A %d %b at %I:%M %p')
    message = (
        f"MindSpace: Your session with {counselor_name} is confirmed "
        f"for {formatted}. "
        f"Reply CANCEL to cancel. We're here for you."
    )
    _send(phone, message, sms_type='confirmation')


def send_crisis_alert_sms(counselor_phone: str, user_display: str, trigger_text: str) -> None:
    """Sent to the on-call counselor when a crisis flag is raised."""
    snippet = trigger_text[:80] + ('...' if len(trigger_text) > 80 else '')
    message = (
        f"[MindSpace CRISIS ALERT] User '{user_display}' needs immediate support. "
        f"Trigger: \"{snippet}\" "
        f"Log in to the admin dashboard now."
    )
    _send(counselor_phone, message, sms_type='crisis')


def send_daily_checkin_sms(phone: str, display_name: str) -> None:
    """Optional daily wellness nudge."""
    message = (
        f"Hi {display_name}, MindSpace here. "
        f"How are you feeling today? "
        f"Log your mood at mindspace.co.ke or dial *384# — we care about you."
    )
    _send(phone, message, sms_type='reminder')


def send_ussd_response(session_id: str, response_text: str, end_session: bool = False) -> dict:
    """
    Handle USSD menu responses via Africa's Talking gateway.
    Called from the USSD webhook view.
    """
    from django.http import HttpResponse
    prefix = 'END ' if end_session else 'CON '
    return HttpResponse(prefix + response_text, content_type='text/plain')
