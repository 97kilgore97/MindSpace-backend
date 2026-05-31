from django.utils import timezone
from datetime import timedelta


UNLOCK_THRESHOLDS = {
    'chapter_1':    3,
    'chapter_2':    7,
    'chapter_3':    14,
    'second_book':  21,
    'full_library': 30,
}


def compute_streak(user):
    from moods.models import MoodLog
    today = timezone.now().date()
    streak = 0
    grace_active = False
    check_day = today

    while MoodLog.objects.filter(user=user, logged_at__date=check_day).exists():
        streak += 1
        check_day -= timedelta(days=1)

    if streak == 0:
        day_before = today - timedelta(days=2)
        if MoodLog.objects.filter(user=user, logged_at__date=day_before).exists():
            grace_active = True
            check_day = day_before
            while MoodLog.objects.filter(user=user, logged_at__date=check_day).exists():
                streak += 1
                check_day -= timedelta(days=1)

    milestones = [k for k, v in UNLOCK_THRESHOLDS.items() if streak >= v]

    unlock_order = ['chapter_1', 'chapter_2', 'chapter_3', 'second_book', 'full_library']
    next_milestone = None
    days_to_next = 0
    for key in unlock_order:
        if streak < UNLOCK_THRESHOLDS[key]:
            next_milestone = {'key': key, 'days': UNLOCK_THRESHOLDS[key], 'label': key.replace('_', ' ').title()}
            days_to_next = UNLOCK_THRESHOLDS[key] - streak
            break

    return {
        'streak_days':    streak,
        'grace_active':   grace_active,
        'milestones':     milestones,
        'next_milestone': next_milestone,
        'days_to_next':   days_to_next,
    }
