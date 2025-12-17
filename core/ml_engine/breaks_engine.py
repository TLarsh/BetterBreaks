# core/ml_engine/breaks_engine.py
import os
import pickle
import numpy as np
from datetime import date, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ---- Load models once (with safe fallbacks) ----
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


# ---- Core Business Logic ----
def generate_break_recommendation(user_input: dict):
    """
    Generate personalized vacation and break recommendations.
    user_input: dict of user preferences and metrics.
    Example:
        {
          "work_hours_per_week": 45,
          "stress_level": 7,
          "sleep_quality": 6,
          "prefers_travel": True,
          "season_preference": "summer"
        }
    """

    # Convert boolean and categorical to numeric encodings
    work_hours = user_input.get("work_hours_per_week", 40)
    stress_level = user_input.get("stress_level", 5)
    sleep_quality = user_input.get("sleep_quality", 5)
    prefers_travel = 1 if user_input.get("prefers_travel", False) else 0

    # Create a default feature array with zeros that matches the expected 30 features
    # This handles the mismatch between our current 4 features and what the scaler may expect
    default_features = np.zeros((1, 30))

    # Place our actual features in the first 4 positions
    default_features[0, 0] = work_hours
    default_features[0, 1] = stress_level
    default_features[0, 2] = sleep_quality
    default_features[0, 3] = prefers_travel

    # Transform with scaler
    try:
        scaled_features = scaler.transform(default_features)
    except Exception:
        # If scaler.transform fails for any reason, fall back to identity
        scaled_features = default_features

    # Predict using ML models or heuristic fallback
    if MODELS_AVAILABLE:
        try:
            predicted_length = int(break_length_model.predict(scaled_features)[0])
        except Exception:
            # Fallback length if model prediction fails
            base_length = 7
            predicted_length = max(3, min(21, base_length + (stress_level - 5) + (5 - sleep_quality) + (2 if prefers_travel else 0)))

        try:
            season_value = seasonal_pref_model.predict(scaled_features)[0]
        except Exception:
            season_value = user_input.get("season_preference", "no_preference")
    else:
        # Heuristic predictions
        base_length = 7
        predicted_length = max(3, min(21, base_length + (stress_level - 5) + (5 - sleep_quality) + (2 if prefers_travel else 0)))
        season_value = user_input.get("season_preference", "no_preference")

    # Map predicted season to actual season names if numeric
    if isinstance(season_value, (int, float)):
        if season_value < 3:
            predicted_season = "winter"
        elif season_value < 6:
            predicted_season = "spring"
        elif season_value < 9:
            predicted_season = "summer"
        else:
            predicted_season = "fall"
    else:
        # If string provided, normalize basic options
        normalized = str(season_value).strip().lower()
        if normalized in {"winter", "spring", "summer", "fall"}:
            predicted_season = normalized
        elif normalized in {"no_preference", "none", "any"}:
            # Choose a season based on stress: higher stress -> sooner season in calendar
            # This is a simplistic heuristic
            month = date.today().month
            if month in (12, 1, 2):
                predicted_season = "winter"
            elif month in (3, 4, 5):
                predicted_season = "spring"
            elif month in (6, 7, 8):
                predicted_season = "summer"
            else:
                predicted_season = "fall"
        else:
            predicted_season = "summer"

    # Generate recommendation dates with some variability
    today = date.today()

    # Add some variability based on user inputs to avoid identical recommendations
    # Higher stress or lower sleep quality = earlier break
    stress_factor = stress_level
    sleep_factor = sleep_quality
    days_adjustment = 7 + (5 - stress_factor) + (sleep_factor - 5)
    recommended_start = today + timedelta(days=max(3, days_adjustment))
    recommended_end = recommended_start + timedelta(days=predicted_length)

    # Create recommendation message with more descriptive content
    season_descriptions = {
        "winter": "during the winter months, which might offer a cozy retreat or winter sports opportunities",
        "spring": "in spring, when nature is blooming and temperatures are mild",
        "summer": "during summer, perfect for outdoor activities and longer daylight hours",
        "fall": "in autumn, with beautiful foliage and comfortable temperatures"
    }

    season_description = season_descriptions.get(predicted_season, f"during {predicted_season}")

    # Create personalized message based on user metrics
    if stress_level > 7:
        stress_message = "Given your high stress levels, "
    elif stress_level > 4:
        stress_message = "Based on your moderate stress levels, "
    else:
        stress_message = "With your current stress profile, "

    message = f"{stress_message}you may benefit from a {predicted_length}-day break {season_description}."

    return {
        "recommended_start_date": recommended_start.isoformat(),
        "recommended_end_date": recommended_end.isoformat(),
        "predicted_length_days": predicted_length,
        "recommended_season": predicted_season,
        "message": message
    }