from django.utils import timezone
from datetime import timedelta


def verify_email_otp(user, otp_input, expiry_minutes=10):
    """
    Reusable OTP verification logic
    Returns: (bool, message)
    """

    if not user.email_otp:
        return False, "No OTP found. Request a new one."

    if user.email_otp != otp_input:
        return False, "Invalid OTP"

    if not user.otp_created_at:
        return False, "OTP timestamp missing"

    if timezone.now() > user.otp_created_at + timedelta(minutes=expiry_minutes):
        return False, "OTP has expired"

    
    user.is_verified = True
    user.email_otp = None  
    user.save()

    return True, "Email verified successfully"