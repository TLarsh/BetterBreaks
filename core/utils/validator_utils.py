def validate_password(password):
    from django.core.exceptions import ValidationError
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    if not any(c.isupper() for c in password):
        raise ValueError("Password must contain uppercase letters")
    if not any(c.islower() for c in password):
        raise ValueError("Password must contain lowercase letters")
    if not any(c.isdigit() for c in password):
        raise ValueError("Password must contain numbers")


from datetime import date
from rest_framework import serializers


def validate_leave_balance(data):
    if data.get('annual_leave_balance', 60) < 0:
        raise serializers.ValidationError("Annual leave balance cannot be negative.")
    if data.get('already_used_balance', 0) < 0:
        raise serializers.ValidationError("Already used balance cannot be negative.")
    if 'annual_leave_refresh_date' in data and data['annual_leave_refresh_date'] < date.today():
        raise serializers.ValidationError("Annual leave refresh date cannot be in the past.")
    return data


def validate_preferences(data):
    valid_choices = ['long_weekends', 'extended_breaks', 'mix_of_both']
    if data.get('preference') and data['preference'] not in valid_choices:
        raise serializers.ValidationError(f"Preference must be one of {valid_choices}.")
    return data


def validate_break_plan(data):
    if not data.get('startDate') or not data.get('endDate'):
        raise serializers.ValidationError("startDate and endDate are required.")
    if data['startDate'] > data['endDate']:
        raise serializers.ValidationError("startDate cannot be after endDate.")
    return data
