from django.core.cache import cache

OTP_COOLDOWN_SECONDS = 60


def can_resend_otp(user):
    key = f"otp_cooldown:{user.id}"
    return cache.get(key) is None


def set_otp_cooldown(user):
    key = f"otp_cooldown:{user.id}"
    cache.set(key, True, timeout=OTP_COOLDOWN_SECONDS)

# from django.utils import timezone
# from datetime import timedelta

# OTP_COOLDOWN_SECONDS = 60  # adjust as needed


# def can_resend_otp(user) -> bool:
#     if not user.otp_created_at:
#         return True

#     elapsed = timezone.now() - user.otp_created_at
#     return elapsed.total_seconds() >= OTP_COOLDOWN_SECONDS