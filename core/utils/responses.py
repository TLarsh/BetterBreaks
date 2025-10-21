from rest_framework.response import Response
from rest_framework.exceptions import ErrorDetail


def normalize(value):
    """
    Recursively normalize DRF errors into plain JSON-serializable values.
    - Converts ErrorDetail to string
    - Handles dicts and lists
    - Normalizes empty values to None
    """
    if isinstance(value, dict):
        return {k: normalize(v) for k, v in value.items()} or None
    elif isinstance(value, list):
        return [normalize(v) for v in value] or None
    elif isinstance(value, ErrorDetail):
        return str(value)
    elif value in [None, {}, [], ""]:
        return None
    return value


def success_response(message="", data=None, status_code=200):
    return Response({
        "message": message,
        "status": True,
        "data": normalize(data),
        "errors": None
    }, status=status_code)

def error_response(message="", errors=None, status_code=400):
    # Normalize all field values inside errors dict
    normalized_errors = {
        key: normalize(value)
        for key, value in (errors or {}).items()
    } if errors else None

    return Response({
        "message": message,
        "status": False,
        "data": None,
        "errors": normalized_errors
    }, status=status_code)