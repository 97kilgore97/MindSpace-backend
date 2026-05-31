import re
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

# ── Keyword tiers ─────────────────────────────────────────
# Critical  → immediate crisis escalation + counselor SMS
# High      → flagged in moderation queue, counselor notified
# Medium    → flagged for review, no SMS

CRISIS_KEYWORDS = {
    'critical': [
        r'\bkill myself\b', r'\bend my life\b', r'\bsuicide\b', r'\bsuicidal\b',
        r'\bwant to die\b', r'\bno reason to live\b', r'\bcan\'t go on\b',
        r'\bdon\'t want to be here\b', r'\bself.harm\b', r'\bcut myself\b',
        r'\boverdose\b', r'\bhanging\b',
    ],
    'high': [
        r'\bhurt myself\b', r'\bhurting myself\b', r'\bno one cares\b',
        r'\bworthless\b', r'\bhopeless\b', r'\bcan\'t keep going\b',
        r'\bsleep forever\b', r'\bdisappear forever\b',
    ],
    'medium': [
        r'\bdepressed\b', r'\banxiety attack\b', r'\bpanic attack\b',
        r'\bcan\'t cope\b', r'\bbreaking down\b', r'\balone\b',
        r'\bno one understands\b',
    ],
}


def _match_tier(text: str) -> tuple[str | None, str | None]:
    """Return (severity, matched_keyword) or (None, None)."""
    text_lower = text.lower()
    for severity in ('critical', 'high', 'medium'):
        for pattern in CRISIS_KEYWORDS[severity]:
            if re.search(pattern, text_lower):
                return severity, pattern
    return None, None


def check_message_safety(message) -> None:
    """
    Called after a ChatMessage is saved.
    Flags the message and optionally escalates to crisis team.
    """
    severity, keyword = _match_tier(message.content)
    if not severity:
        return

    # Flag message in DB
    message.is_flagged = True
    message.flag_reason = f'{severity.upper()} keyword: {keyword}'
    message.save(update_fields=['is_flagged', 'flag_reason'])

    logger.warning(
        f'Safety flag [{severity}] on message {message.id} '
        f'from user {message.sender_id}: {keyword}'
    )

    if severity in ('critical', 'high'):
        escalate_crisis(
            user=message.sender,
            source='chat',
            source_id=str(message.id),
            trigger_text=message.content,
            severity=severity,
        )


def check_journal_safety(entry) -> None:
    """
    Called after a JournalEntry is saved.
    Journals are private — we only escalate critical flags.
    """
    severity, keyword = _match_tier(entry.content)
    if severity == 'critical':
        escalate_crisis(
            user=entry.user,
            source='journal',
            source_id=str(entry.id),
            trigger_text=entry.content,
            severity=severity,
        )


def escalate_crisis(user, source: str, source_id: str, trigger_text: str, severity: str = 'high') -> None:
    """
    Creates a CrisisFlag record and alerts the on-call counselor via SMS.
    Imported by groups/views.py and called directly for manual escalations.
    """
    from core.models import CrisisFlag  # avoid circular import at module level
    from core.sms import send_crisis_alert_sms

    # Mark user as crisis-flagged
    if user:
        user.status = 'flagged'
        user.save(update_fields=['status'])
        if hasattr(user, 'profile'):
            user.profile.crisis_flag = True
            user.profile.save(update_fields=['crisis_flag'])

    flag = CrisisFlag.objects.create(
        user=user,
        source=source,
        source_id=source_id,
        trigger_text=trigger_text[:500],
        severity=severity,
        status='open',
    )

    # SMS on-call counselor
    on_call_phone = getattr(settings, 'CRISIS_COUNSELOR_PHONE', None)
    if on_call_phone:
        display = user.display_name if user else 'Anonymous'
        send_crisis_alert_sms(
            counselor_phone=on_call_phone,
            user_display=display,
            trigger_text=trigger_text,
        )

    logger.critical(
        f'Crisis flag created: {flag.id} | severity={severity} | '
        f'user={user.id if user else "anon"} | source={source}'
    )
