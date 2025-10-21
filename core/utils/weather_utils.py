import requests



def fetch_6day_weather_forecast_openweathermap(latitude, longitude):
    """
    Fetch 6-day daily weather forecast from OpenWeatherMap.
    Returns a list of daily forecast dicts.
    """
    # api_key = "6291107705516e94ac5df05f71e1f5de"  # Replace with your actual API key
    # url = "https://api.openweathermap.org/data/3.0/onecall" 
    # url = "https://api.openweathermap.org/data/2.5/onecall" # Free tier endpoint
    api_key = "dVVfPHo3rD9oENOkcvjKKQSQXoKLVzGn"  # Replace with your actual API key
    url = "https://api.tomorrow.io/v4/weather/forecast"
    params = {
        "location": f"{latitude},{longitude}",
        "timesteps": "1d",
        "apikey": api_key,
        "units": "metric",
    }
    response = requests.get(url, params=params)
    print("Status:", response.status_code)
    print("Response:", response.text)  
    if response.status_code == 200:
        data = response.json()
        # return data.get("daily", [])  # List of 8 daily forecast dicts
        return data.get("timelines", {}).get("daily", [])
    return []

def adjust_score_based_on_weather(score, weather_data):
    """
    Adjust the holiday score based on weather conditions.
    """
    if not weather_data or "daily" not in weather_data:
        return score

    # Example: Penalize bad weather (e.g., rain, extreme temperatures)
    weather_conditions = weather_data["daily"][0]["conditionCode"]
    temperature_max = weather_data["daily"][0]["temperatureMax"]
    temperature_min = weather_data["daily"][0]["temperatureMin"]

    if weather_conditions in ["rain", "thunderstorms"]:
        score -= 20  # Penalize rainy days
    elif temperature_max > 35 or temperature_min < 5:
        score -= 15  # Penalize extreme temperatures

    return max(score, 0)  # Ensure score doesn't go below 0

