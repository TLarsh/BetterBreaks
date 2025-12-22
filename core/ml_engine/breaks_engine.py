# # core/ml_engine/breaks_engine.py
# import os
# import pickle
# import numpy as np
# from datetime import date, timedelta

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# # ---- Load models once (with safe fallbacks) ----
# MODELS_AVAILABLE = True
# try:
#     with open(os.path.join(BASE_DIR, "break_length_model.pkl"), "rb") as f:
#         break_length_model = pickle.load(f)

#     with open(os.path.join(BASE_DIR, "seasonal_pref_model.pkl"), "rb") as f:
#         seasonal_pref_model = pickle.load(f)

#     with open(os.path.join(BASE_DIR, "scaler.pkl"), "rb") as f:
#         scaler = pickle.load(f)
# except Exception:
#     MODELS_AVAILABLE = False

#     class IdentityScaler:
#         def transform(self, X):
#             return X

#     scaler = IdentityScaler()


# # ---- Core Business Logic ----#
# # 
# import numpy as np
# from datetime import date, timedelta
# from django.utils import timezone

# from ..models.recommendation_models import UserMetrics
# from ..services.user_metrics_service import UserMetricsService



# def generate_break_recommendation(user):
#     """
#     Generate a system-driven break recommendation.
#     """

#     metrics = UserMetricsService.build(user)

#     work_hours = metrics.work_hours_per_week
#     stress = metrics.stress_level
#     sleep = metrics.sleep_quality
#     travel = 1 if metrics.prefers_travel else 0
#     season_pref = metrics.season_preference

#     # -----------------------------
#     # Feature vector (fixed length)
#     # -----------------------------
#     features = np.zeros((1, 30))
#     features[0, 0] = work_hours
#     features[0, 1] = stress
#     features[0, 2] = sleep
#     features[0, 3] = travel

#     try:
#         scaled = scaler.transform(features)
#     except Exception:
#         scaled = features

#     # -----------------------------
#     # Predict length
#     # -----------------------------
#     if MODELS_AVAILABLE:
#         try:
#             length = int(break_length_model.predict(scaled)[0])
#         except Exception:
#             length = _heuristic_length(stress, sleep, travel)
#     else:
#         length = _heuristic_length(stress, sleep, travel)

#     length = max(3, min(21, length))

#     # -----------------------------
#     # Predict season
#     # -----------------------------
#     if MODELS_AVAILABLE:
#         try:
#             season_raw = seasonal_pref_model.predict(scaled)[0]
#             season = _map_season(season_raw)
#         except Exception:
#             season = _normalize_season(season_pref)
#     else:
#         season = _normalize_season(season_pref)

#     # -----------------------------
#     # Dates
#     # -----------------------------
#     urgency = stress - sleep
#     start = timezone.now().date() + timedelta(days=max(3, 7 - urgency))
#     end = start + timedelta(days=length)

#     # -----------------------------
#     # Message
#     # -----------------------------
#     message = _build_message(stress, length, season)

#     return {
#         "recommended_start_date": start,
#         "recommended_end_date": end,
#         "predicted_length_days": length,
#         "recommended_season": season,
#         "message": message,
#     }


# # ============================
# # Helpers
# # ============================

# def _heuristic_length(stress, sleep, travel):
#     return 7 + (stress - 5) + (5 - sleep) + (2 if travel else 0)


# def _map_season(val):
#     if isinstance(val, (int, float)):
#         if val < 3:
#             return "winter"
#         if val < 6:
#             return "spring"
#         if val < 9:
#             return "summer"
#         return "fall"
#     return _normalize_season(val)


# def _normalize_season(val):
#     val = str(val).lower()
#     if val in {"winter", "spring", "summer", "fall"}:
#         return val
#     return _season_from_calendar()


# def _season_from_calendar():
#     m = date.today().month
#     if m in (12, 1, 2):
#         return "winter"
#     if m in (3, 4, 5):
#         return "spring"
#     if m in (6, 7, 8):
#         return "summer"
#     return "fall"


# def _build_message(stress, days, season):
#     if stress >= 8:
#         prefix = "Given your high stress levels,"
#     elif stress >= 5:
#         prefix = "Based on your recent workload,"
#     else:
#         prefix = "With your current balance,"

#     return f"{prefix} a {days}-day break during {season} would be beneficial."


# core/ml_engine/breaks_engine.py

import os
import pickle
import numpy as np
from datetime import date, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# -------------------------------------------------
# Load models safely (pure ML assets)
# -------------------------------------------------
MODELS_AVAILABLE = True
try:
    with open(os.path.join(BASE_DIR, "break_length_model.pkl"), "rb") as f:
        break_length_model = pickle.load(f)

    with open(os.path.join(BASE_DIR, "seasonal_pref_model.pkl"), "rb") as f:
        seasonal_pref_model = pickle.load(f)

    with open(os.path.join(BASE_DIR, "scaler.pkl"), "rb") as f:
        scaler = pickle.load(f)

except Exception:
    MODELS_AVAILABLE = False

    class IdentityScaler:
        def transform(self, X):
            return X

    scaler = IdentityScaler()


# -------------------------------------------------
# PURE ENGINE (NO DJANGO, NO SERVICES)
# -------------------------------------------------
def generate_break_recommendation(user_input: dict) -> dict:
    """
    PURE function.
    Takes system-derived metrics dict.
    Returns recommendation dict.
    """

    work_hours = user_input.get("work_hours_per_week", 40)
    stress = user_input.get("stress_level", 5)
    sleep = user_input.get("sleep_quality", 5)
    travel = 1 if user_input.get("prefers_travel") else 0
    season_pref = user_input.get("season_preference", "no_preference")

    # -----------------------------
    # Feature vector (fixed length)
    # -----------------------------
    features = np.zeros((1, 30))
    features[0, 0] = work_hours
    features[0, 1] = stress
    features[0, 2] = sleep
    features[0, 3] = travel

    try:
        scaled = scaler.transform(features)
    except Exception:
        scaled = features

    # -----------------------------
    # Predict break length
    # -----------------------------
    if MODELS_AVAILABLE:
        try:
            length = int(break_length_model.predict(scaled)[0])
        except Exception:
            length = _heuristic_length(stress, sleep, travel)
    else:
        length = _heuristic_length(stress, sleep, travel)

    length = max(3, min(21, length))

    # -----------------------------
    # Predict season
    # -----------------------------
    if MODELS_AVAILABLE:
        try:
            season_raw = seasonal_pref_model.predict(scaled)[0]
            season = _map_season(season_raw)
        except Exception:
            season = _normalize_season(season_pref)
    else:
        season = _normalize_season(season_pref)

    # -----------------------------
    # Dates (calendar-based, pure)
    # -----------------------------
    urgency = stress - sleep
    start = date.today() + timedelta(days=max(3, 7 - urgency))
    end = start + timedelta(days=length)

    message = _build_message(stress, length, season)

    return {
        "recommended_start_date": start.isoformat(),
        "recommended_end_date": end.isoformat(),
        "predicted_length_days": length,
        "recommended_season": season,
        "message": message,
    }


# -------------------------------------------------
# Helpers (PURE)
# -------------------------------------------------
def _heuristic_length(stress, sleep, travel):
    return 7 + (stress - 5) + (5 - sleep) + (2 if travel else 0)


def _map_season(val):
    if isinstance(val, (int, float)):
        if val < 3:
            return "winter"
        if val < 6:
            return "spring"
        if val < 9:
            return "summer"
        return "fall"
    return _normalize_season(val)


def _normalize_season(val):
    val = str(val).lower()
    if val in {"winter", "spring", "summer", "fall"}:
        return val
    return _season_from_calendar()


def _season_from_calendar():
    m = date.today().month
    if m in (12, 1, 2):
        return "winter"
    if m in (3, 4, 5):
        return "spring"
    if m in (6, 7, 8):
        return "summer"
    return "fall"


def _build_message(stress, days, season):
    if stress >= 8:
        prefix = "Given your high stress levels,"
    elif stress >= 5:
        prefix = "Based on your recent workload,"
    else:
        prefix = "With your current balance,"

    return f"{prefix} a {days}-day break during {season} would be beneficial."
