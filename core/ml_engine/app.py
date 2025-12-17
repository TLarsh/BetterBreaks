import streamlit as st
import pandas as pd
from datetime import datetime, date
from leave_optimizer import LeaveOptimizationModel
import pickle

# Page configuration
st.set_page_config(
    page_title="Leave & Break Optimization Model",
    page_icon="🏖️",
    layout="wide"
)

# Load the model
@st.cache_resource
def load_model():
    return LeaveOptimizationModel()

model = load_model()

# Title and description
st.title("🏖️ Leave & Break Optimization Model")


# Create two columns for input and output
col1, col2 = st.columns([1, 1])

with col1:
    st.header(" Input Your Preferences")

    # Country/Region selection
    country_region = st.selectbox(
        "Country / Region",
        ["England and Wales", "Scotland", "Northern Ireland"],
        help="Determines public holiday calendar"
    )

    # Work-related inputs
    st.subheader(" Work Information")
    work_type = st.selectbox(
        "Work_Type",
        ["Full-time", "Part-time", "Freelance/Contractor"]
    )

    work_hours = st.selectbox(
        "Work_Hours",
        ["20 - 30 hours", "31 - 40 hours", "41 - 50 hours"]
    )

    break_frequency = st.selectbox(
        "Break_Frequency",
        ["Less than once a week", "1 - 2 times a week", "Daily", "Several times a day"]
    )

    break_timing = st.selectbox(
        "Break_Timing_Preferences",
        [
            "Based on workload/stress levels",
            "Summer (July - September), End of the year (October - December), Based on workload/stress levels",
            "Start of the year (January - March), Summer (July - September), Based on workload/stress levels",
            "Summer (July - September), End of the year (October - December)",
            "No particular preference"
        ]
    )

    # Stress and break inputs
    st.subheader(" Stress & Break Patterns")
    pre_stress = st.selectbox(
        "Pre-Holiday_Stress",
        ["Very Low", "Low", "Moderate", "High", "Very High"]
    )

    post_stress = st.selectbox(
        "Post-Holiday_Stress",
        ["Very Low", "Low", "Moderate", "High", "Very High"]
    )

    break_stress = st.selectbox(
        "Break_Stress",
        [
            "No, I can take breaks easily.",
            "Sometimes, depending on the workload.",
            "Yes, I often feel guilty or worried about work when taking breaks."
        ]
    )

    break_necessity = st.selectbox(
        "Break_Necessity",
        ["No, I don't need regular breaks", "Not really", "Neutral", "Yes, somewhat", "Yes, very strongly"]
    )

    # Preferences
    st.subheader(" Preferences")
    preferred_break_type = st.selectbox(
        "Preferred_Break_Type",
        [
            "Weekend break suggestions (e.g. taking off Friday or Monday for a long weekend)",
            "Weekend break suggestions (e.g. taking off Friday or Monday for a long weekend), Quarterly longer holiday suggestions (e.g. a full week off)",
            "Quarterly longer holiday suggestions (e.g. a full week off)",
            "Customisable suggestions based on my workload and preferences"
        ]
    )

    holiday_preferences = st.selectbox(
        "Holiday_Preferences",
        [
            "Short, frequent breaks (e.g., multiple times a year)",
            "Quarterly breaks (approximately every 3 months), Flexible depending on workload, It varies based on occasions and responsibilities",
            "Short, frequent breaks (e.g., multiple times a year), Quarterly breaks (approximately every 3 months)",
            "Short, frequent breaks (e.g., multiple times a year), One or two long breaks per year",
            "Quarterly breaks (approximately every 3 months), Flexible depending on workload"
        ]
    )

    seasonal_preferences = st.selectbox(
        "Seasonal_Holiday_Preference",
        [
            "Summer (July - September), End of the year (October - December)",
            "No particular preference",
            "Start of the year (January - March), Summer (July - September), End of the year (October - December)",
            "Summer (July - September)",
            "Mid-year (April - June), End of the year (October - December)"
        ]
    )

    # Dynamic inputs
    st.subheader(" Dynamic Information")
    leave_balance = st.number_input(
        "Leave_Balance",
        min_value=0,
        max_value=50,
        value=25,
        help="Current available leave days"
    )

    # Annual leave refresh date
    annual_refresh_date = st.date_input(
        "Annual_Leave_Refresh_Date",
        value=datetime(datetime.now().year + 1, 1, 1).date() if datetime.now().month >= 10 else datetime(datetime.now().year, 1, 1).date(),
        help="Date when your annual leave balance refreshes (typically January 1st)"
    )

    # Special dates
    st.write("Special_Dates (e.g., birthdays, anniversaries)")
    special_dates_input = st.text_area(
        "Enter dates as YYYY-MM-DD, one per line",
        placeholder="2024-12-25\n2024-05-15",
        height=100
    )

    # Blackout dates
    st.write("Blackout_Dates (public holidays or unavailable days)")
    blackout_dates_input = st.text_area(
        "Enter dates as YYYY-MM-DD, one per line",
        placeholder="2024-12-25\n2024-01-01",
        height=100
    )

    # Year selection
    current_year = datetime.now().year
    selected_year = st.selectbox(
        "Planning Year",
        [current_year, current_year + 1],
        help="Year for which to generate leave recommendations"
    )

    # Generate recommendations button
    generate_button = st.button(" Get Recommendations", type="primary", use_container_width=True)

with col2:
    st.header("📊 Leave Recommendations")

    if generate_button:
        # Process inputs
        user_data = {
        'Country_Region': country_region,
        'Work_Type': work_type,
        'Work_Hours': work_hours,
        'Break_Frequency': break_frequency,
        'Break_Timing_Preferences': break_timing,
        'Pre-Holiday_Stress': pre_stress,
        'Post-Holiday_Stress': post_stress,
        'Break_Stress': break_stress,
        'Break_Necessity': break_necessity,
        'Preferred_Break_Type': preferred_break_type,
        'Holiday_Preferences': holiday_preferences,
        'Seasonal_Holiday_Preference': seasonal_preferences,
        'LeaveBalance': leave_balance,
        'Annual_Leave_Refresh_Date': annual_refresh_date,
        'SpecialDates': [d.strip() for d in special_dates_input.split('\n') if d.strip()],
        'BlackoutDates': [d.strip() for d in blackout_dates_input.split('\n') if d.strip()]
        }

        # Generate recommendations
        with st.spinner("Analyzing your preferences and generating optimal leave plans..."):
            try:
                plans = model.generate_all_plans(user_data, selected_year)

                # Display results
                plan_names = {
                    'holiday_extension': ' Holiday Extension Opportunity',
                    'special_date_anchored': ' Special-Date Anchored Recommendation',
                    'seasonal_balanced': ' Seasonally Balanced Alternative'
                }

                for plan_key, plan_data in plans.items():
                    with st.expander(f"Plan {list(plans.keys()).index(plan_key) + 1}", expanded=True):
                        col_a, col_b, col_c, col_d = st.columns(4)

                        with col_a:
                            st.metric("Total Rest Days", plan_data['total_rest_days'])

                        with col_b:
                            st.metric("Leave Days Used", plan_data['leave_days_used'])

                        with col_c:
                            st.metric("Remaining Balance", plan_data['remaining_balance'])

                        with col_d:
                            balance_ratio_pct = f"{plan_data['balance_ratio']*100:.1f}%"
                            st.metric("Balance Ratio", balance_ratio_pct,
                                    help=f"Current balance as % of annual allocation")

                        # Additional metrics
                        col_e, col_f = st.columns(2)

                        with col_e:
                            refresh_date = plan_data['annual_leave_refresh_date']
                            if isinstance(refresh_date, str):
                                refresh_date = datetime.strptime(refresh_date, '%Y-%m-%d').date()
                            st.metric("Next Refresh", refresh_date.strftime('%Y-%m-%d'))

                        with col_f:
                            days_until = plan_data['days_until_refresh']
                            st.metric("Days Until Refresh", f"{days_until} days")

                        # Recommended dates
                        if plan_data['leave_dates']:
                            dates_str = ", ".join([d.strftime('%Y-%m-%d (%A)') for d in plan_data['leave_dates']])
                            st.write(f"**Recommended dates:** {dates_str}")
                        else:
                            st.info("No leave dates recommended for this plan.")

            except Exception as e:
                st.error(f"Error generating recommendations: {str(e)}")
                st.info("Please check your input data and try again.")

    else:
        st.info("👈 Fill in your preferences and click 'Get Recommendations' to see optimal leave plans.")

# Footer
st.markdown("---")

