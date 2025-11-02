# core/ml_engine/breaks_engine.py
import os
import pickle
import numpy as np
from datetime import date, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ---- Load models once ----
with open(os.path.join(BASE_DIR, "break_length_model.pkl"), "rb") as f:
    break_length_model = pickle.load(f)

with open(os.path.join(BASE_DIR, "seasonal_pref_model.pkl"), "rb") as f:
    seasonal_pref_model = pickle.load(f)

with open(os.path.join(BASE_DIR, "scaler.pkl"), "rb") as f:
    scaler = pickle.load(f)


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
    # This handles the mismatch between our current 4 features and what the scaler expects
    default_features = np.zeros((1, 30))
    
    # Place our actual features in the first 4 positions
    default_features[0, 0] = work_hours
    default_features[0, 1] = stress_level
    default_features[0, 2] = sleep_quality
    default_features[0, 3] = prefers_travel
    
    # Transform with scaler
    scaled_features = scaler.transform(default_features)

    # Predict using ML models
    predicted_length = int(break_length_model.predict(scaled_features)[0])
    
    # Map predicted season to actual season names instead of numeric values
    season_value = seasonal_pref_model.predict(scaled_features)[0]
    
    # Map numeric season values to actual season names
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
        predicted_season = str(season_value)
    
    # Generate recommendation dates with some variability
    today = date.today()
    
    # Add some variability based on user inputs to avoid identical recommendations
    # Use stress level and sleep quality to adjust the start date
    stress_factor = user_input.get("stress_level", 5) 
    sleep_factor = user_input.get("sleep_quality", 5)
    
    # Higher stress or lower sleep quality = earlier break
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
    if user_input.get("stress_level", 5) > 7:
        stress_message = "Given your high stress levels, "
    elif user_input.get("stress_level", 5) > 4:
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
