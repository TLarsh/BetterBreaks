import streamlit as st
from itertools import combinations
import pandas as pd
from datetime import datetime, timedelta
import pickle
from calendar import monthrange

# Bank holidays data
bank_holidays = pd.to_datetime([
    "2025-01-01", "2025-04-18", "2025-04-21", "2025-05-05",
    "2025-05-26", "2025-08-25", "2025-12-25", "2025-12-26"
])
bank_holidays_df = pd.DataFrame({"Bank_Holiday": bank_holidays})
bank_holidays_df["Bank_Holiday_Month"] = bank_holidays_df["Bank_Holiday"].dt.month
bank_holidays_df["Day_of_Week"] = bank_holidays_df["Bank_Holiday"].dt.dayofweek

# Define mappings for single-select fields
AGE_GROUP_MAP = {'25-34': 1, '18-24': 0, '35-44': 2, '45-54': 3, '55+': 4}
WORK_TYPE_MAP = {'Full-time': 1, 'Freelance/Contractor': 0, 'Part-time': 2}
WORK_HOURS_MAP = {'31 - 40 hours': 1, '41 - 50 hours': 2, '20 - 30 hours': 0}
WORK_ENVIRONMENT_MAP = {'Office/site': 2, 'Hybrid (combination of office and remote)': 0, 
                        'Remote (work from home)': 3, 'Occasional working from home when/if required': 1}
YEARS_IN_JOB_MAP = {'4-7 years': 1, '1-3 years': 0, 'Less than 1 year': 3, '8+ years': 2}
VACATION_DAYS_MAP = {'21 - 25 days': 2, 'More than 25 days': 3, '16 - 20 days': 1, '10 - 15 days': 0}
VACATION_USE_MAP = {'Mixed (both long and short breaks)': 4, 
                    'Multiple short breaks (e.g., 1-3 days each)': 5, 
                    'Mid length holidays (e.g. one week at a time)': 3, 
                    'Long holidays (e.g. two or more weeks at once)': 2, 
                    'A mix of Mid and short breaks': 0, 
                    "Just took 3 days off (if you're talking about the current holiday year ending 31st March 2025)": 1, 
                    'mixed - mid and short': 6}
BREAK_FREQ_MAP = {'1 - 2 times a week': 0, 'Daily': 1, 'Less than once a week': 2, 'Several times a day': 3}
IDEAL_BREAK_LENGTH_MAP = {'Short (4 - 7 days)': 2, 'Long (15+ days)': 0, 'Medium (8 - 14 days)': 1, 'Very short (1 - 3 days)': 3}
PRE_HOLIDAY_STRESS_MAP = {'Moderate': 2, 'Very High': 3, 'Low': 1, 'High': 0, 'Very Low': 4}
POST_HOLIDAY_STRESS_MAP = {'Low': 1, 'Moderate': 2, 'Very Low': 4, 'High': 0, 'Very High': 3}
PRE_HOLIDAY_PROD_MAP = {'Low Productivity': 2, 'High Productivity': 1, 'Average Productivity': 0, 
                        'Very Low Productivity': 4, 'Very High Productivity': 3}
POST_HOLIDAY_PROD_MAP = {'High Productivity': 1, 'Low Productivity': 2, 'Average Productivity': 0, 
                         'Very Low Productivity': 4, 'Very High Productivity': 3}
POST_HOLIDAY_REFRESH_MAP = {1: 0, 2: 1, 3: 2, 4: 3, 5: 4}
BREAK_TYPE_PREF_MAP = {'More productive after multiple short breaks': 1, 'No noticeable difference': 2, 
                       'More productive after a single long break': 0}
INTEREST_METRICS_MAP = {'Yes': 2, 'Maybe, if privacy and data protection are ensured': 0, 'No': 1}
BREAK_ADJ_FREQ_MAP = {'Quarterly': 4, 'Monthly': 2, 'Annually': 0, 'Only as needed': 3, 'Biannually': 1}
HOLIDAY_EFFECTIVENESS_MAP = {'Very effective': 4, 'Extremely effective': 0, 'Moderately effective': 1, 
                             'Not effective at all': 2, 'Slightly effective': 3}
IMPROVED_PROD_BREAKS_MAP = {'Yes, somewhat': 4, 'Yes, significantly': 3, 'Neutral': 0, 
                            'No, not really': 2, 'No, not at all': 1}
BREAK_HOLIDAY_PRIORITY_MAP = {'More short breaks throughout the year': 3, 'No change': 4, 
                              'Better alignment with personal and family needs': 0, 
                              'More flexibility based on workload': 2, 'Fewer, longer holidays': 1}
BREAK_STRESS_MAP = {
    'No, I can take breaks easily.': 0,
    'Yes, I often feel guilty or worried about work when taking breaks.': 2,
    'Sometimes, depending on the workload.': 1
}
BREAK_NECESSITY_MAP = {
    'Yes, very strongly': 4,
    'Yes, somewhat': 3,
    'Not really': 2,
    'Neutral': 0,
    'No, I don’t need regular breaks': 1
}
BREAK_RECOMMENDATION_FREQ_MAP = {
    'Monthly': 3,
    'After upcoming busy work periods': 0,
    'Before upcoming busy work periods': 1,
    'Weekly': 4,
    'Daily': 2
}

# Multi-select mappings
HOLIDAY_PREF_OPTIONS = [
    'Short, frequent breaks (e.g., multiple times a year)',
    'Quarterly breaks (approximately every 3 months)',
    'Flexible depending on workload',
    'It varies based on occasions and responsibilities',
    'One or two long breaks per year',
    'No strong preference'
]
HOLIDAY_PREF_MAP = {tuple([option]): i for i, option in enumerate(HOLIDAY_PREF_OPTIONS)}
for i, combo in enumerate(combinations(HOLIDAY_PREF_OPTIONS, 2), len(HOLIDAY_PREF_OPTIONS)):
    HOLIDAY_PREF_MAP[tuple(sorted(combo))] = i

SEASONAL_PREF_OPTIONS = [
    'Start of the year (January - March)',
    'Mid-year (April - June)',
    'Summer (July - September)',
    'End of the year (October - December)',
    'No particular preference'
]
SEASONAL_PREF_MAP = {
    tuple(['End of the year (October - December)']): 0,
    tuple(['Mid-year (April - June)']): 1,
    tuple(['Mid-year (April - June)', 'End of the year (October - December)']): 2,
    tuple(['Mid-year (April - June)', 'Summer (July - September)']): 3,
    tuple(['Mid-year (April - June)', 'Summer (July - September)', 'End of the year (October - December)']): 4,
    tuple(['No particular preference']): 5,
    tuple(['Start of the year (January - March)', 'End of the year (October - December)']): 6,
    tuple(['Start of the year (January - March)', 'Mid-year (April - June)', 'End of the year (October - December)']): 7,
    tuple(['Start of the year (January - March)', 'Mid-year (April - June)', 'Summer (July - September)', 'End of the year (October - December)']): 8,
    tuple(['Start of the year (January - March)', 'Summer (July - September)']): 9,
    tuple(['Start of the year (January - March)', 'Summer (July - September)', 'End of the year (October - December)']): 10,
    tuple(['Summer (July - September)']): 11,
    tuple(['End of the year (October - December)', 'Summer (July - September)']): 12,
    tuple(['Summer (July - September)', 'No particular preference']): 13
}

PREFERRED_BREAK_TYPE_OPTIONS = [
    'Weekend break suggestions (e.g. taking off Friday or Monday for a long weekend)',
    'Quarterly longer holiday suggestions (e.g. a full week off)',
    'Customisable suggestions based on my workload and preferences',
    'End-of-week breaks (e.g., Friday afternoon off)'
]
PREFERRED_BREAK_TYPE_MAP = {tuple([option]): i for i, option in enumerate(PREFERRED_BREAK_TYPE_OPTIONS)}
for i, combo in enumerate(combinations(PREFERRED_BREAK_TYPE_OPTIONS, 2), len(PREFERRED_BREAK_TYPE_OPTIONS)):
    PREFERRED_BREAK_TYPE_MAP[tuple(sorted(combo))] = i

BREAK_TIMING_OPTIONS = [
    'Start of the year (January - March)',
    'Mid-year (April - June)',
    'Summer (July - September)',
    'End of the year (October - December)',
    'Based on workload/stress levels',
    'No particular preference'
]
BREAK_TIMING_MAP = {tuple([option]): i for i, option in enumerate(BREAK_TIMING_OPTIONS)}
for i, combo in enumerate(combinations(BREAK_TIMING_OPTIONS, 2), len(BREAK_TIMING_OPTIONS)):
    BREAK_TIMING_MAP[tuple(sorted(combo))] = i

# Seasonal preference mapping for Holiday_Preference_Alignment
PREFERENCE_MAP = {
    12: [7, 8, 9, 10, 11, 12], 5: list(range(1, 13)), 10: [1, 2, 3, 7, 8, 9, 10, 11, 12], 
    11: [7, 8, 9], 2: [4, 5, 6, 10, 11, 12], 0: [10, 11, 12], 4: [4, 5, 6, 7, 8, 9, 10, 11, 12], 
    3: [4, 5, 6, 7, 8, 9], 1: [4, 5, 6], 6: [1, 2, 3, 10, 11, 12], 13: [7, 8, 9], 
    8: list(range(1, 13)), 9: [1, 2, 3, 7, 8, 9], 7: [1, 2, 3, 4, 5, 6, 10, 11, 12]
}

# Stress mapping for Pre-Holiday_Stress_Score and Need_for_Break
STRESS_MAPPING = {3: 1.0, 0: 0.8, 2: 0.5, 1: 0.2, 4: 0.0}

# Expected feature order from training
FEATURE_ORDER = [
    'Age_Group', 'Work_Type', 'Work_Hours', 'Work_Environment', 'Years_in_Job', 
    'Vacation_Days', 'Vacation_Use', 'Break_Frequency', 'Holiday_Preferences', 
    'Pre-Holiday_Stress', 'Post-Holiday_Stress', 'Pre-Holiday_Productivity', 
    'Post-Holiday_Productivity', 'Post-Holiday_Refreshment', 'Break_Type_Preference', 
    'Break_Stress', 'Break_Necessity', 'Break_Recommendation_Frequency', 
    'Preferred_Break_Type', 'Break_Timing_Preferences', 'Interest_in_Metrics', 
    'Break_Adjustment_Frequency', 'Holiday_Effectiveness', 'Improved_Productivity_with_Breaks', 
    'Break/Holiday_Priorities', 'Holiday_Preference_Alignment', 'Is_Busy_Period', 
    'Holiday_Reduced_Stress', 'Pre-Holiday_Stress_Score', 'Need_for_Break'
]

# Load models and scaler
try:
    with open('break_length_model.pkl', 'rb') as f:
        break_length_model = pickle.load(f)
    with open('seasonal_pref_model.pkl', 'rb') as f:
        seasonal_pref_model = pickle.load(f)
    with open('scaler.pkl', 'rb') as f:
        scaler = pickle.load(f)
except FileNotFoundError as e:
    st.error(f"Error loading files: {e}. Ensure 'break_length_model.pkl', 'seasonal_pref_model.pkl', and 'scaler.pkl' are in the working directory.")
    break_length_model = None
    seasonal_pref_model = None
    scaler = None

def check_preference_match(preference_encoded, holiday_month):
    preferred_months = PREFERENCE_MAP.get(preference_encoded, [])
    return 1 if holiday_month in preferred_months else 0

def derive_features(form_data):
    pref_encoded = form_data["Seasonal_Holiday_Preference"]
    holiday_preference_alignment = int(any(
        check_preference_match(pref_encoded, month) for month in bank_holidays_df["Bank_Holiday_Month"]
    ))
    is_busy_period = int((form_data["Work_Hours"] >= 2) | 
                         (form_data["Pre-Holiday_Stress"] == 0) | 
                         (form_data["Pre-Holiday_Stress"] == 3))
    holiday_reduced_stress = int((form_data["Post-Holiday_Stress"] == 4) | 
                                 (form_data["Post-Holiday_Stress"] == 1))
    pre_holiday_stress_score = STRESS_MAPPING[form_data["Pre-Holiday_Stress"]]
    work_hours_max = 2
    need_for_break = (
        (form_data["Work_Hours"] / work_hours_max) * 0.4 +
        pre_holiday_stress_score * 0.3 +
        is_busy_period * 0.2 +
        (form_data["Break_Necessity"] / 4) * 0.1
    )
    return {
        'Holiday_Preference_Alignment': holiday_preference_alignment,
        'Is_Busy_Period': is_busy_period,
        'Holiday_Reduced_Stress': holiday_reduced_stress,
        'Pre-Holiday_Stress_Score': pre_holiday_stress_score,
        'Need_for_Break': need_for_break
    }

def recommend_vacation_days(user_data, break_length_model, seasonal_pref_model):
    user_data_df = pd.DataFrame([user_data])
    user_data_df = user_data_df[FEATURE_ORDER]
    user_data_df[FEATURE_ORDER] = scaler.transform(user_data_df[FEATURE_ORDER])
    
    pred_break_length = int(round(break_length_model.predict(user_data_df)[0]))
    pred_seasonal_pref = int(round(seasonal_pref_model.predict(user_data_df)[0]))
    
    break_length_map = {2: 7, 0: 15, 1: 10, 3: 3}
    seasonal_pref_months = {
        12: [7, 8, 9], 5: [], 10: [1, 7, 12], 11: [7, 8, 9], 2: [6, 12], 0: [12], 
        4: [6, 7, 12], 3: [6, 7], 1: [6], 6: [1, 12], 13: [7], 8: list(range(1, 13)), 
        9: [1, 7], 7: [1, 6, 12]
    }

    recommended_days = []
    break_days_needed = break_length_map.get(pred_break_length, 7)
    preferred_months = seasonal_pref_months.get(pred_seasonal_pref, [])
    
    current_year = datetime.now().year
    
    for month in preferred_months:
        num_days = monthrange(current_year, month)[1]
        for day in range(1, num_days + 1):
            date = datetime(current_year, month, day)
            if date.weekday() < 5:
                recommended_days.append(date)
                if len(recommended_days) >= break_days_needed:
                    break
        if len(recommended_days) >= break_days_needed:
            break
    
    leave_days = sorted(set(recommended_days))[:break_days_needed]
    leave_days = [day.strftime('%Y-%m-%d') for day in leave_days]
    
    return {
        "Model_Predicted_Leave_Days": leave_days,
        "Vacation_Period": f"{leave_days[0]} to {leave_days[-1]}" if leave_days else "No specific recommendation"
    }

def suggest_optimal_holidays(bank_holidays_df):
    recommended_holidays = []
    
    for holiday in bank_holidays_df["Bank_Holiday"]:
        weekday = holiday.weekday()
        leave_days = []
        holiday_start = holiday
        holiday_end = holiday
        
        if weekday == 3:  # Thursday
            leave_days.append(holiday + timedelta(days=1))  # Friday
            holiday_end = holiday + timedelta(days=3)  # Until Sunday
        elif weekday == 1:  # Tuesday
            leave_days.append(holiday - timedelta(days=1))  # Monday
            holiday_start = holiday - timedelta(days=2)  # Start from Saturday
        elif weekday == 4:  # Friday
            leave_days.append(holiday - timedelta(days=1))  # Thursday
            holiday_start = holiday - timedelta(days=1)  # Start from Thursday
            holiday_end = holiday + timedelta(days=2)  # Until Sunday
        elif weekday == 0:  # Monday
            leave_days.append(holiday - timedelta(days=3))  # Friday before
            leave_days.append(holiday + timedelta(days=1))  # Tuesday after
            holiday_start = holiday - timedelta(days=3)  # Start from Friday
            holiday_end = holiday + timedelta(days=1)  # Until Tuesday
        elif weekday == 2:  # Wednesday
            leave_days.append(holiday + timedelta(days=1))  # Thursday
            leave_days.append(holiday + timedelta(days=2))  # Friday
            holiday_end = holiday + timedelta(days=4)  # Until Sunday
        
        leave_days_str = ", ".join(day.strftime('%A (%Y-%m-%d)') for day in leave_days)
        holiday_period = f"{holiday_start.strftime('%A (%Y-%m-%d)')} to {holiday_end.strftime('%A (%Y-%m-%d)')}"
        recommended_holidays.append(f"Take leave on {leave_days_str} → Holiday period: {holiday_period}")
    
    return recommended_holidays
def load_weather_data(file_path='weather_data.csv'):
    try:
        weather_df = pd.read_csv(file_path)
        weather_df['datetime'] = pd.to_datetime(weather_df['datetime'])
        weather_df['day_of_year'] = weather_df['datetime'].dt.strftime('%m-%d')  # MM-DD format
        return weather_df[['datetime', 'day_of_year', 'conditions', 'description', 'temp', 'humidity']]
    except FileNotFoundError:
        st.warning("⚠️ `weather_data.csv` not found. Weather analysis is skipped.")
        return None

def get_weather_analysis(recommended_dates, weather_df):
    if weather_df is None:
        return []

    result = []
    for date_str in recommended_dates:
        date_obj = pd.to_datetime(date_str)
        mm_dd = date_obj.strftime('%m-%d')  # Match only month and day

        match_row = weather_df[weather_df['day_of_year'] == mm_dd]

        if not match_row.empty:
            row = match_row.iloc[0]
            conditions = str(row["conditions"]).lower()
            desc = str(row["description"]).lower()
            humidity = row["humidity"]

            is_sunny = any(kw in conditions or kw in desc for kw in ["sunny", "clear", "partly cloudy"])
            is_humid = humidity > 70

            result.append({
                "date": date_str,
                "weather_description": row["description"],
                "temperature_c": row["temp"],
                "humidity_percent": humidity,
                "suitability": "Sunny" if is_sunny else ("Humid" if is_humid else "Not suitable")
            })
        else:
            result.append({
                "date": date_str,
                "error": "No historical weather data found for this MM-DD"
            })
    return result

def main():
    st.title("BetterBreaksAI")
    st.write("Please fill out the following form about your work and break preferences (select up to 2 options where applicable)")

    with st.form(key='work_life_form'):
        st.subheader("Personal & Work Information")
        age_group = st.selectbox("Age Group", list(AGE_GROUP_MAP.keys()))
        work_type = st.selectbox("Work Type", list(WORK_TYPE_MAP.keys()))
        work_hours = st.selectbox("Weekly Work Hours", list(WORK_HOURS_MAP.keys()))
        work_environment = st.selectbox("Work Environment", list(WORK_ENVIRONMENT_MAP.keys()))
        years_in_job = st.selectbox("Years in Current Job", list(YEARS_IN_JOB_MAP.keys()))

        st.subheader("Vacation Preferences")
        vacation_days = st.selectbox("Annual Vacation Days", list(VACATION_DAYS_MAP.keys()))
        vacation_use = st.selectbox("Vacation Use Pattern", list(VACATION_USE_MAP.keys()))
        holiday_prefs = st.multiselect("Holiday Preferences (select up to 2)", HOLIDAY_PREF_OPTIONS, max_selections=2)
        seasonal_prefs = st.multiselect("Preferred Holiday Season (select up to 2)", SEASONAL_PREF_OPTIONS, max_selections=2)

        st.subheader("Stress & Productivity Metrics")
        pre_holiday_stress = st.selectbox("Pre-Holiday Stress", list(PRE_HOLIDAY_STRESS_MAP.keys()))
        post_holiday_stress = st.selectbox("Post-Holiday Stress", list(POST_HOLIDAY_STRESS_MAP.keys()))
        pre_holiday_prod = st.selectbox("Pre-Holiday Productivity", list(PRE_HOLIDAY_PROD_MAP.keys()))
        post_holiday_prod = st.selectbox("Post-Holiday Productivity", list(POST_HOLIDAY_PROD_MAP.keys()))
        post_holiday_refresh = st.slider("Post-Holiday Refreshment (1-5)", 1, 5, 3)
        holiday_effectiveness = st.selectbox("Holiday Effectiveness", list(HOLIDAY_EFFECTIVENESS_MAP.keys()))

        st.subheader("Break Preferences")
        break_freq = st.selectbox("Break Frequency", list(BREAK_FREQ_MAP.keys()))
        ideal_break_length = st.selectbox("Ideal Break Length", list(IDEAL_BREAK_LENGTH_MAP.keys()))
        break_type_pref = st.selectbox("Break Type Preference", list(BREAK_TYPE_PREF_MAP.keys()))
        preferred_break_type = st.multiselect("Preferred Break Type (select up to 2)", PREFERRED_BREAK_TYPE_OPTIONS, max_selections=2)
        break_timing = st.multiselect("Break Timing Preferences (select up to 2)", BREAK_TIMING_OPTIONS, max_selections=2)
        break_stress = st.selectbox("Do you feel stressed about taking breaks?", list(BREAK_STRESS_MAP.keys()))
        break_necessity = st.selectbox("Do you feel a need for regular breaks?", list(BREAK_NECESSITY_MAP.keys()))
        break_recommendation_freq = st.selectbox("How often would you like break recommendations?", list(BREAK_RECOMMENDATION_FREQ_MAP.keys()))

        st.subheader("Additional Preferences")
        interest_metrics = st.selectbox("Interest in Metrics", list(INTEREST_METRICS_MAP.keys()))
        break_adj_freq = st.selectbox("Break Adjustment Frequency", list(BREAK_ADJ_FREQ_MAP.keys()))
        improved_prod_breaks = st.selectbox("Improved Productivity with Breaks", list(IMPROVED_PROD_BREAKS_MAP.keys()))
        break_holiday_priority = st.selectbox("Break/Holiday Priorities", list(BREAK_HOLIDAY_PRIORITY_MAP.keys()))

        submit_button = st.form_submit_button(label='Submit')

    if submit_button:
        if not holiday_prefs or not seasonal_prefs or not preferred_break_type or not break_timing:
            st.error("Please make at least one selection for each multi-select field.")
        elif break_length_model is None or seasonal_pref_model is None or scaler is None:
            st.error("Required files (models or scaler) could not be loaded.")
        else:
            form_data_numeric = {
                'Age_Group': AGE_GROUP_MAP[age_group],
                'Work_Type': WORK_TYPE_MAP[work_type],
                'Work_Hours': WORK_HOURS_MAP[work_hours],
                'Work_Environment': WORK_ENVIRONMENT_MAP[work_environment],
                'Years_in_Job': YEARS_IN_JOB_MAP[years_in_job],
                'Vacation_Days': VACATION_DAYS_MAP[vacation_days],
                'Vacation_Use': VACATION_USE_MAP[vacation_use],
                'Holiday_Preferences': HOLIDAY_PREF_MAP[tuple(sorted(holiday_prefs))],
                'Seasonal_Holiday_Preference': SEASONAL_PREF_MAP[tuple(sorted(seasonal_prefs))],
                'Pre-Holiday_Stress': PRE_HOLIDAY_STRESS_MAP[pre_holiday_stress],
                'Post-Holiday_Stress': POST_HOLIDAY_STRESS_MAP[post_holiday_stress],
                'Pre-Holiday_Productivity': PRE_HOLIDAY_PROD_MAP[pre_holiday_prod],
                'Post-Holiday_Productivity': POST_HOLIDAY_PROD_MAP[post_holiday_prod],
                'Post-Holiday_Refreshment': POST_HOLIDAY_REFRESH_MAP[post_holiday_refresh],
                'Break_Frequency': BREAK_FREQ_MAP[break_freq],
                'Ideal_Break_Length': IDEAL_BREAK_LENGTH_MAP[ideal_break_length],
                'Break_Type_Preference': BREAK_TYPE_PREF_MAP[break_type_pref],
                'Preferred_Break_Type': PREFERRED_BREAK_TYPE_MAP[tuple(sorted(preferred_break_type))],
                'Break_Timing_Preferences': BREAK_TIMING_MAP[tuple(sorted(break_timing))],
                'Break_Stress': BREAK_STRESS_MAP[break_stress],
                'Break_Necessity': BREAK_NECESSITY_MAP[break_necessity],
                'Break_Recommendation_Frequency': BREAK_RECOMMENDATION_FREQ_MAP[break_recommendation_freq],
                'Interest_in_Metrics': INTEREST_METRICS_MAP[interest_metrics],
                'Break_Adjustment_Frequency': BREAK_ADJ_FREQ_MAP[break_adj_freq],
                'Holiday_Effectiveness': HOLIDAY_EFFECTIVENESS_MAP[holiday_effectiveness],
                'Improved_Productivity_with_Breaks': IMPROVED_PROD_BREAKS_MAP[improved_prod_breaks],
                'Break/Holiday_Priorities': BREAK_HOLIDAY_PRIORITY_MAP[break_holiday_priority]
            }

            # Step 1: Derive features
            derived_features = derive_features(form_data_numeric)
            form_data_numeric.update(derived_features)

            # Step 2: Drop specified features
            form_data_numeric.pop('Ideal_Break_Length', None)
            form_data_numeric.pop('Seasonal_Holiday_Preference', None)

            # Step 3: Generate vacation recommendations
            
            try:
                model_recommendation = recommend_vacation_days(form_data_numeric, break_length_model, seasonal_pref_model)
                bank_holiday_recommendations = suggest_optimal_holidays(bank_holidays_df)

                # Combine basic recommendations
                combined_recommendations = {
                    "Long Vacation Recommendation": model_recommendation,
                    "Bank Holiday Optimized Suggestions": bank_holiday_recommendations
                }

                # Weather-based additions
                weather_df = load_weather_data()

                model_leave_days = model_recommendation.get("Model_Predicted_Leave_Days", [])
                weather_for_model_days = get_weather_analysis(model_leave_days, weather_df)

                bank_leave_days = []
                for h in bank_holiday_recommendations:
                    try:
                        # Extract date from "Take leave on Friday (2025-04-18), Monday (2025-04-21)"
                        start_idx = h.find('(') + 1
                        end_idx = h.find(')')
                        if start_idx > 0 and end_idx > start_idx:
                            first_date_str = h[start_idx:end_idx]
                            bank_leave_days.append(
                                pd.to_datetime(first_date_str).strftime('%Y-%m-%d')
                            )
                    except Exception as e:
                        st.warning(f"Failed to parse date from holiday suggestion: {h} | Error: {e}")
                weather_for_bank_days = get_weather_analysis(bank_leave_days, weather_df)

                # Add weather-based recommendations to the result
                combined_recommendations["Weather-Based Suitability"] = {
                    "For Model-Predicted Days": weather_for_model_days,
                    "For Bank Holiday Suggested Days": weather_for_bank_days
                }

                st.success("Form submitted successfully!")
                st.write("Enhanced Vacation Plan:")
                st.json(combined_recommendations)

            except ValueError as e:
                st.error(f"Prediction error: {e}. Check feature alignment with training data.")
if __name__ == '__main__':
    main()

    