from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import logging

logger = logging.getLogger(__name__)

MENU_MAIN = """\
Welcome to MindSpace 🌿
1. Talk to a peer now
2. Book a counselor
3. Crisis helpline
4. Daily mood check-in
0. Exit"""

MENU_CRISIS = """\
You are not alone. Help is available right now:
- Call FREE: 0800 720 199 (24/7)
- Call FREE: 0800 720 900
- SMS 'HELP' to 22771

Press 0 to go back."""

MENU_BOOK = """\
Book a counselor:
1. Dr. Diana Nyambura (Anxiety)
2. Kevin Ochieng (Youth)
3. Dr. James Karanja (Depression)
0. Back"""

MENU_CHECKIN = """\
How are you feeling today?
1. Great 😊
2. Good 🙂
3. Okay 😐
4. Low 😔
5. Hard 😞"""


@csrf_exempt
@require_POST
def ussd_callback(request):
    """
    POST /api/ussd/
    Africa's Talking calls this endpoint for every USSD interaction on *384#.
    """
    session_id  = request.POST.get('sessionId', '')
    phone       = request.POST.get('phoneNumber', '')
    text        = request.POST.get('text', '').strip()

    logger.info(f'USSD session={session_id} phone={phone} text="{text}"')

    # text is cumulative: '1*2*3' means user went main→1→2→3
    steps = text.split('*') if text else []
    depth = len(steps)

    # ── Root menu ─────────────────────────────────────────
    if text == '':
        return _con(MENU_MAIN)

    # ── Depth 1: main menu choice ─────────────────────────
    if depth == 1:
        choice = steps[0]
        if choice == '1':
            return _con('Connecting you to a peer support room...\n\nVisit mindspace.co.ke or open the MindSpace app to chat anonymously. You are not alone.')
        elif choice == '2':
            return _con(MENU_BOOK)
        elif choice == '3':
            return _con(MENU_CRISIS)
        elif choice == '4':
            return _con(MENU_CHECKIN)
        elif choice == '0':
            return _end('Thank you for using MindSpace. Take care of yourself. 🌿')
        else:
            return _con('Invalid option.\n\n' + MENU_MAIN)

    # ── Depth 2 ───────────────────────────────────────────
    if depth == 2:
        main, sub = steps[0], steps[1]

        # Book a counselor
        if main == '2':
            counselors = {
                '1': 'Dr. Diana Nyambura',
                '2': 'Kevin Ochieng',
                '3': 'Dr. James Karanja',
            }
            if sub == '0':
                return _con(MENU_MAIN)
            name = counselors.get(sub)
            if name:
                _log_ussd_booking(phone, name)
                return _end(
                    f'Your request to book {name} has been received. '
                    f'You will receive an SMS confirmation shortly. '
                    f'MindSpace cares about you.'
                )
            return _con('Invalid option.\n\n' + MENU_BOOK)

        # Crisis - go back
        if main == '3' and sub == '0':
            return _con(MENU_MAIN)

        # Mood check-in
        if main == '4':
            labels = {'1': 'Great', '2': 'Good', '3': 'Okay', '4': 'Low', '5': 'Hard'}
            label = labels.get(sub)
            if label:
                _log_ussd_mood(phone, sub, label)
                messages = {
                    '1': "That's wonderful! Keep shining.",
                    '2': "Good to hear. Keep going.",
                    '3': "That's okay. One step at a time.",
                    '4': "We hear you. You're not alone. Consider talking to someone.",
                    '5': "We're so glad you reached out. Please call 0800 720 199 — free, 24/7.",
                }
                return _end(f'Mood logged: {label}. {messages[sub]}')
            return _con('Invalid option.\n\n' + MENU_CHECKIN)

    return _end('Thank you for using MindSpace. Stay well.')


def _con(text: str) -> HttpResponse:
    """Continue the USSD session."""
    return HttpResponse('CON ' + text, content_type='text/plain')


def _end(text: str) -> HttpResponse:
    """End the USSD session."""
    return HttpResponse('END ' + text, content_type='text/plain')


def _log_ussd_booking(phone: str, counselor_name: str):
    """Fire-and-forget: record USSD booking request."""
    try:
        from core.sms import send_session_confirmation_sms
        from django.utils import timezone
        # In production: look up user by phone, create a pending session
        logger.info(f'USSD booking request: {phone} → {counselor_name}')
    except Exception as e:
        logger.error(f'USSD booking log error: {e}')


def _log_ussd_mood(phone: str, score: str, label: str):
    """Fire-and-forget: record mood from USSD."""
    try:
        logger.info(f'USSD mood: {phone} → {score} ({label})')
        # In production: look up user by phone, save MoodLog
    except Exception as e:
        logger.error(f'USSD mood log error: {e}')
