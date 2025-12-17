import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
import pickle
from typing import List, Dict, Tuple, Optional
import holidays
from collections import defaultdict


class LeaveOptimizationModel:
    """
    Leave & Break Optimization Model that recommends optimal leave dates
    by maximizing consecutive rest days using fewest leave days possible.
    """

    def __init__(self, trained_data_path: str = 'processed_data.pkl'):
        """Initialize the model with trained data"""
        with open(trained_data_path, 'rb') as f:
            data = pickle.load(f)
            self.trained_data = data['data']
            self.encoders = data['encoders']

        # Initialize holiday calendars for different regions
        self.holiday_calendars = {
            'England and Wales': holidays.UK(prov='England'),
            'Scotland': holidays.UK(prov='Scotland'),
            'Northern Ireland': holidays.UK(prov='Northern Ireland')
        }

        # Preference mappings for scoring
        self.stress_mapping = {'Very Low': 1, 'Low': 2, 'Moderate': 3, 'High': 4, 'Very High': 5}
        self.break_stress_mapping = {
            'No, I can take breaks easily.': 1,
            'Sometimes, depending on the workload.': 3,
            'Yes, I often feel guilty or worried about work when taking breaks.': 5
        }
        self.break_necessity_mapping = {
            "No, I don't need regular breaks": 1,
            'Not really': 2,
            'Neutral': 3,
            'Yes, somewhat': 4,
            'Yes, very strongly': 5
        }

    def preprocess_user_input(self, user_data: Dict) -> Dict:
        """Convert user input to numerical scores for optimization"""
        processed = {}

        # Basic user preferences
        processed['work_type'] = user_data.get('Work_Type', 'Full-time')
        processed['work_hours'] = user_data.get('Work_Hours', '31 - 40 hours')
        processed['break_frequency'] = user_data.get('Break_Frequency', '1 - 2 times a week')
        processed['preferred_break_type'] = user_data.get('Preferred_Break_Type', 'Weekend break suggestions')

        # Stress scores
        processed['pre_holiday_stress'] = self.stress_mapping.get(
            user_data.get('Pre-Holiday_Stress', 'Moderate'), 3)
        processed['post_holiday_stress'] = self.stress_mapping.get(
            user_data.get('Post-Holiday_Stress', 'Moderate'), 3)
        processed['break_stress'] = self.break_stress_mapping.get(
            user_data.get('Break_Stress', 'Sometimes, depending on the workload.'), 3)
        processed['break_necessity'] = self.break_necessity_mapping.get(
            user_data.get('Break_Necessity', 'Yes, somewhat'), 4)

        # Overall stress score
        processed['overall_stress'] = (processed['pre_holiday_stress'] +
                                     processed['post_holiday_stress'] +
                                     processed['break_stress']) / 3

        # Preferences
        processed['holiday_preferences'] = user_data.get('Holiday_Preferences', 'Short, frequent breaks')
        processed['seasonal_preferences'] = user_data.get('Seasonal_Holiday_Preference', 'No particular preference')

        # Dynamic inputs
        processed['special_dates'] = user_data.get('SpecialDates', [])
        processed['blackout_dates'] = user_data.get('BlackoutDates', [])
        processed['leave_balance'] = user_data.get('LeaveBalance', 25)
        processed['country_region'] = user_data.get('Country_Region', 'England and Wales')

        # Annual leave refresh date (typically January 1st or anniversary date)
        refresh_date_input = user_data.get('Annual_Leave_Refresh_Date')
        if refresh_date_input is None:
            # Default to January 1st of next year if current date is after October
            # or January 1st of current year if before October
            current_date = datetime.now().date()
            if current_date.month >= 10:  # After October, next refresh is next year
                processed['annual_leave_refresh_date'] = date(current_date.year + 1, 1, 1)
            else:  # Before October, next refresh is this year
                processed['annual_leave_refresh_date'] = date(current_date.year, 1, 1)
        else:
            # Parse the input date if it's a string
            if isinstance(refresh_date_input, str):
                processed['annual_leave_refresh_date'] = datetime.strptime(refresh_date_input, '%Y-%m-%d').date()
            else:
                processed['annual_leave_refresh_date'] = refresh_date_input

        # Calculate derived metrics
        processed['balance_ratio'] = self._calculate_balance_ratio(processed)
        processed['days_until_refresh'] = self._calculate_days_until_refresh(processed['annual_leave_refresh_date'])

        return processed

    def get_optimal_leave_periods(self, year: int, processed_user_data: Dict) -> List[Tuple[datetime.date, datetime.date]]:
        """Determine optimal leave periods based on user preferences"""
        preferred_months = self._extract_preferred_months(processed_user_data['holiday_preferences'])
        preferred_seasons = self._extract_preferred_seasons(processed_user_data['seasonal_preferences'])

        # Get candidate periods based on preferences
        candidate_periods = []

        # Generate periods for preferred seasons/months
        for season_months in preferred_seasons:
            for month in season_months:
                # Generate 2-3 week periods in preferred months
                start_date = datetime(year, month, 1).date()
                end_date = (start_date + timedelta(days=20)).date()

                # Adjust to month boundaries
                if month == 12:
                    end_date = datetime(year, 12, 31).date()
                else:
                    end_date = (datetime(year, month+1, 1) - timedelta(days=1)).date()

                candidate_periods.append((start_date, end_date))

        # If no specific preferences, use year-round distribution
        if not candidate_periods:
            for quarter in range(1, 5):
                month = (quarter - 1) * 3 + 1
                start_date = datetime(year, month, 1).date()
                end_date = (datetime(year, min(month+2, 12), 28) + timedelta(days=3)).date()
                candidate_periods.append((start_date, end_date))

        return candidate_periods

    def _extract_preferred_months(self, holiday_prefs: str) -> List[int]:
        """Extract preferred months from holiday preferences"""
        month_keywords = {
            'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
            'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12
        }

        preferred_months = []
        for month_name, month_num in month_keywords.items():
            if month_name.lower() in holiday_prefs.lower():
                preferred_months.append(month_num)

        return list(set(preferred_months))  # Remove duplicates

    def _extract_preferred_seasons(self, seasonal_prefs: str) -> List[List[int]]:
        """Extract preferred seasons as month ranges"""
        season_mapping = {
            'Start of the year': [1, 2, 3],
            'January - March': [1, 2, 3],
            'Mid-year': [4, 5, 6],
            'April - June': [4, 5, 6],
            'Summer': [7, 8, 9],
            'July - September': [7, 8, 9],
            'End of the year': [10, 11, 12],
            'October - December': [10, 11, 12]
        }

        preferred_seasons = []
        for season_name, months in season_mapping.items():
            if season_name.lower() in seasonal_prefs.lower():
                preferred_seasons.append(months)

        return preferred_seasons if preferred_seasons else [[1,2,3,4,5,6,7,8,9,10,11,12]]

    def _calculate_balance_ratio(self, processed_data: Dict) -> float:
        """Calculate the ratio of remaining balance to total annual allocation"""
        # Assuming standard 25 days annual leave, but use the provided balance as current remaining
        total_annual_allocation = 25  # Could be made configurable
        current_balance = processed_data['leave_balance']

        # If balance is higher than standard, it might include carried over days
        # For ratio calculation, we consider the current balance as the effective remaining
        return min(current_balance / total_annual_allocation, 2.0)  # Cap at 200% to handle carry-over

    def _calculate_days_until_refresh(self, refresh_date: date) -> int:
        """Calculate days until next annual leave refresh"""
        current_date = datetime.now().date()
        if refresh_date >= current_date:
            return (refresh_date - current_date).days
        else:
            # If refresh date has passed this year, calculate for next year
            next_refresh = date(refresh_date.year + 1, refresh_date.month, refresh_date.day)
            return (next_refresh - current_date).days

    def find_optimal_leave_dates(self, year: int, processed_user_data: Dict,
                               plan_type: str = 'balanced') -> Dict:
        """Generate optimal leave dates for a specific plan type"""

        leave_balance = processed_user_data['leave_balance']
        special_dates = processed_user_data['special_dates']
        blackout_dates = processed_user_data['blackout_dates']
        country_region = processed_user_data['country_region']

        # Get public holidays for the region
        public_holidays = self._get_public_holidays(year, country_region)

        # Combine blackout dates with public holidays
        all_blackout_dates = set(blackout_dates + public_holidays)

        # Determine break preferences
        preferred_break_type = processed_user_data['preferred_break_type']
        if 'long' in preferred_break_type.lower() or 'week' in preferred_break_type.lower():
            target_break_length = min(7, leave_balance)  # Long break: 3-7+ days
        else:
            target_break_length = min(3, leave_balance)  # Short break: 1-3 days

        # Adjust based on stress levels
        stress_multiplier = processed_user_data['overall_stress'] / 3.0

        # Adjust based on balance ratio and days until refresh
        balance_ratio = processed_user_data['balance_ratio']
        days_until_refresh = processed_user_data['days_until_refresh']

        # If low balance ratio and refresh is far away, be more conservative
        if balance_ratio < 0.5 and days_until_refresh > 180:
            stress_multiplier *= 0.8  # Reduce recommendation intensity

        # If refresh is soon and balance is adequate, can be more generous
        elif days_until_refresh < 60 and balance_ratio > 0.3:
            stress_multiplier *= 1.2  # Increase recommendation intensity

        target_break_length = int(target_break_length * stress_multiplier)

        if plan_type == 'holiday_extension':
            return self._generate_holiday_extension_plan(
                year, leave_balance, all_blackout_dates, special_dates, target_break_length, processed_user_data)
        elif plan_type == 'special_date_anchored':
            return self._generate_special_date_plan(
                year, leave_balance, all_blackout_dates, special_dates, target_break_length, processed_user_data)
        else:  # seasonally_balanced
            return self._generate_seasonal_plan(
                year, leave_balance, all_blackout_dates, special_dates,
                processed_user_data, target_break_length)

    def _get_public_holidays(self, year: int, country_region: str) -> List[datetime.date]:
        """Get public holidays for the specified region"""
        calendar = self.holiday_calendars.get(country_region, self.holiday_calendars['England and Wales'])
        return [date for date in calendar.get(year, [])]

    def _generate_holiday_extension_plan(self, year: int, leave_balance: int,
                                       blackout_dates: List, special_dates: List,
                                       target_break_length: int, processed_user_data: Dict) -> Dict:
        """Generate plan that maximizes rest around public holidays"""

        # Find periods around public holidays where we can extend with leave
        best_period = None
        max_consecutive_rest = 0
        min_leave_used = float('inf')

        # Check each blackout date for extension opportunities
        for blackout_date in blackout_dates:
            if isinstance(blackout_date, str):
                blackout_date = datetime.strptime(blackout_date, '%Y-%m-%d').date()

            # Look for opportunities to extend before and after
            for extension_days in range(1, min(target_break_length + 1, leave_balance + 1)):
                # Try extending before
                start_date = blackout_date - timedelta(days=extension_days)
                end_date = blackout_date
                leave_dates = [start_date + timedelta(days=i) for i in range(extension_days)]

                # Check if these are valid workdays (not weekends or blackouts)
                valid_leave_dates = [d for d in leave_dates if d.weekday() < 5 and d not in blackout_dates]

                if len(valid_leave_dates) <= leave_balance:
                    consecutive_rest = self._calculate_consecutive_rest(
                        valid_leave_dates, blackout_dates, year)

                    if consecutive_rest > max_consecutive_rest or \
                       (consecutive_rest == max_consecutive_rest and len(valid_leave_dates) < min_leave_used):
                        max_consecutive_rest = consecutive_rest
                        min_leave_used = len(valid_leave_dates)
                        best_period = {
                            'leave_dates': valid_leave_dates,
                            'total_rest_days': consecutive_rest,
                            'leave_days_used': len(valid_leave_dates),
                            'remaining_balance': leave_balance - len(valid_leave_dates),
                            'annual_leave_refresh_date': processed_user_data['annual_leave_refresh_date'],
                            'days_until_refresh': processed_user_data['days_until_refresh'],
                            'balance_ratio': processed_user_data['balance_ratio']
                        }

                # Try extending after
                start_date = blackout_date
                end_date = blackout_date + timedelta(days=extension_days)
                leave_dates = [start_date + timedelta(days=i+1) for i in range(extension_days)]

                valid_leave_dates = [d for d in leave_dates if d.weekday() < 5 and d not in blackout_dates]

                if len(valid_leave_dates) <= leave_balance:
                    consecutive_rest = self._calculate_consecutive_rest(
                        valid_leave_dates, blackout_dates, year)

                    if consecutive_rest > max_consecutive_rest or \
                       (consecutive_rest == max_consecutive_rest and len(valid_leave_dates) < min_leave_used):
                        max_consecutive_rest = consecutive_rest
                        min_leave_used = len(valid_leave_dates)
                        best_period = {
                            'leave_dates': valid_leave_dates,
                            'total_rest_days': consecutive_rest,
                            'leave_days_used': len(valid_leave_dates),
                            'remaining_balance': leave_balance - len(valid_leave_dates),
                            'annual_leave_refresh_date': processed_user_data['annual_leave_refresh_date'],
                            'days_until_refresh': processed_user_data['days_until_refresh'],
                            'balance_ratio': processed_user_data['balance_ratio']
                        }

        return best_period or {
            'leave_dates': [],
            'total_rest_days': 0,
            'leave_days_used': 0,
            'remaining_balance': leave_balance,
            'annual_leave_refresh_date': processed_user_data['annual_leave_refresh_date'],
            'days_until_refresh': processed_user_data['days_until_refresh'],
            'balance_ratio': processed_user_data['balance_ratio']
        }

    def _generate_special_date_plan(self, year: int, leave_balance: int,
                                  blackout_dates: List, special_dates: List,
                                  target_break_length: int, processed_user_data: Dict) -> Dict:
        """Generate plan that includes leave on special dates"""

        if not special_dates:
            # Fallback to holiday extension if no special dates
            return self._generate_holiday_extension_plan(
                year, leave_balance, blackout_dates, special_dates, target_break_length)

        # Convert special dates to date objects
        special_date_objects = []
        for special_date in special_dates:
            if isinstance(special_date, str):
                special_date_objects.append(datetime.strptime(special_date, '%Y-%m-%d').date())
            else:
                special_date_objects.append(special_date)

        # Find best special date to anchor leave around
        best_plan = None
        max_consecutive_rest = 0

        for special_date in special_date_objects:
            # Try different break lengths around the special date
            for break_length in range(1, min(target_break_length + 1, leave_balance + 1)):
                # Center the break around the special date
                start_offset = break_length // 2
                leave_dates = []

                for i in range(break_length):
                    leave_date = special_date - timedelta(days=start_offset - i)
                    if leave_date.weekday() < 5 and leave_date not in blackout_dates:
                        leave_dates.append(leave_date)

                # Ensure special date is included if it's a workday
                if special_date.weekday() < 5 and special_date not in blackout_dates:
                    if special_date not in leave_dates:
                        leave_dates.append(special_date)
                        leave_dates = sorted(leave_dates)
                        if len(leave_dates) > leave_balance:
                            leave_dates = leave_dates[:leave_balance]

                if len(leave_dates) <= leave_balance:
                    consecutive_rest = self._calculate_consecutive_rest(
                        leave_dates, blackout_dates, year)

                    if consecutive_rest > max_consecutive_rest:
                        max_consecutive_rest = consecutive_rest
                        best_plan = {
                            'leave_dates': sorted(leave_dates),
                            'total_rest_days': consecutive_rest,
                            'leave_days_used': len(leave_dates),
                            'remaining_balance': leave_balance - len(leave_dates),
                            'annual_leave_refresh_date': processed_user_data['annual_leave_refresh_date'],
                            'days_until_refresh': processed_user_data['days_until_refresh'],
                            'balance_ratio': processed_user_data['balance_ratio']
                        }

        return best_plan or {
            'leave_dates': [],
            'total_rest_days': 0,
            'leave_days_used': 0,
            'remaining_balance': leave_balance,
            'annual_leave_refresh_date': processed_user_data['annual_leave_refresh_date'],
            'days_until_refresh': processed_user_data['days_until_refresh'],
            'balance_ratio': processed_user_data['balance_ratio']
        }

    def _generate_seasonal_plan(self, year: int, leave_balance: int,
                              blackout_dates: List, special_dates: List,
                              processed_user_data: Dict, target_break_length: int) -> Dict:
        """Generate seasonally balanced leave plan"""

        preferred_seasons = self._extract_preferred_seasons(
            processed_user_data['seasonal_preferences'])

        # Distribute leave across preferred seasons
        total_leave_to_use = min(leave_balance, target_break_length * len(preferred_seasons))

        if not preferred_seasons:
            # Default to quarterly distribution
            preferred_seasons = [[1,2,3], [4,5,6], [7,8,9], [10,11,12]]

        leave_per_season = max(1, total_leave_to_use // len(preferred_seasons))
        remaining_leave = total_leave_to_use

        all_leave_dates = []

        for season_months in preferred_seasons:
            if remaining_leave <= 0:
                break

            season_leave = min(leave_per_season, remaining_leave)
            season_dates = self._find_optimal_dates_in_season(
                year, season_months, season_leave, blackout_dates)

            all_leave_dates.extend(season_dates)
            remaining_leave -= len(season_dates)

        # Sort all dates
        all_leave_dates = sorted(all_leave_dates)

        # Calculate total rest days
        total_rest_days = self._calculate_consecutive_rest(
            all_leave_dates, blackout_dates, year)

        return {
            'leave_dates': all_leave_dates,
            'total_rest_days': total_rest_days,
            'leave_days_used': len(all_leave_dates),
            'remaining_balance': leave_balance - len(all_leave_dates),
            'annual_leave_refresh_date': processed_user_data['annual_leave_refresh_date'],
            'days_until_refresh': processed_user_data['days_until_refresh'],
            'balance_ratio': processed_user_data['balance_ratio']
        }

    def _find_optimal_dates_in_season(self, year: int, season_months: List[int],
                                    leave_days: int, blackout_dates: List) -> List[datetime.date]:
        """Find optimal leave dates within a season"""

        candidate_dates = []

        # Generate candidate dates in the season
        for month in season_months:
            # Get all workdays in the month
            if month == 12:
                days_in_month = 31
            else:
                days_in_month = (datetime(year, month+1, 1) - datetime(year, month, 1)).days

            for day in range(1, days_in_month + 1):
                date = datetime(year, month, day).date()
                if date.weekday() < 5 and date not in blackout_dates:  # Weekday, not blackout
                    candidate_dates.append(date)

        # Select optimal dates that maximize consecutive rest
        if len(candidate_dates) <= leave_days:
            return candidate_dates

        # Find clusters of dates that can give longer breaks
        optimal_dates = []
        remaining_to_select = leave_days

        # Sort by "rest potential" (how many weekend days they connect to)
        date_scores = []
        for date in candidate_dates:
            # Calculate rest potential
            rest_days = 0

            # Check previous days
            check_date = date - timedelta(days=1)
            while check_date.weekday() >= 5 or check_date in blackout_dates:
                rest_days += 1
                check_date -= timedelta(days=1)
                if rest_days > 3:  # Limit check
                    break

            # Check following days
            check_date = date + timedelta(days=1)
            while check_date.weekday() >= 5 or check_date in blackout_dates:
                rest_days += 1
                check_date += timedelta(days=1)
                if rest_days > 6:  # Limit check
                    break

            date_scores.append((date, rest_days))

        # Sort by rest potential (descending)
        date_scores.sort(key=lambda x: x[1], reverse=True)

        # Select top dates, ensuring they're not too close (to distribute leave)
        selected_dates = []
        for date, score in date_scores:
            if remaining_to_select <= 0:
                break

            # Check if too close to already selected dates
            too_close = False
            for selected in selected_dates:
                if abs((date - selected).days) < 7:  # At least a week apart
                    too_close = True
                    break

            if not too_close:
                selected_dates.append(date)
                remaining_to_select -= 1

        return sorted(selected_dates)

    def _calculate_consecutive_rest(self, leave_dates: List[datetime.date],
                                  blackout_dates: List, year: int) -> int:
        """Calculate total consecutive rest days from leave dates"""

        if not leave_dates:
            return 0

        # Combine leave dates with weekends and blackouts to find rest periods
        all_rest_dates = set()

        # Add weekends and blackouts
        for month in range(1, 13):
            if month == 12:
                days_in_month = 31
            else:
                days_in_month = (datetime(year, month+1, 1) - datetime(year, month, 1)).days

            for day in range(1, days_in_month + 1):
                date = datetime(year, month, day).date()
                if date.weekday() >= 5 or date in blackout_dates:  # Weekend or blackout
                    all_rest_dates.add(date)

        # Add leave dates
        for leave_date in leave_dates:
            all_rest_dates.add(leave_date)

        # Find consecutive rest periods
        sorted_rest_dates = sorted(list(all_rest_dates))
        total_rest_days = 0
        current_streak = 1

        for i in range(1, len(sorted_rest_dates)):
            if (sorted_rest_dates[i] - sorted_rest_dates[i-1]).days == 1:
                current_streak += 1
            else:
                total_rest_days += current_streak
                current_streak = 1

        total_rest_days += current_streak

        return total_rest_days

    def generate_all_plans(self, user_data: Dict, year: int = None) -> Dict:
        """Generate all three leave plans for the user"""

        if year is None:
            year = datetime.now().year

        processed_data = self.preprocess_user_input(user_data)

        plans = {}

        # Plan 1: Holiday Extension Opportunity
        plans['holiday_extension'] = self.find_optimal_leave_dates(
            year, processed_data, 'holiday_extension')
        plans['holiday_extension']['description'] = "Maximizes consecutive rest around public holidays"

        # Plan 2: Special-Date Anchored Recommendation
        plans['special_date_anchored'] = self.find_optimal_leave_dates(
            year, processed_data, 'special_date_anchored')
        plans['special_date_anchored']['description'] = "Includes leave on special dates with optimal rest"

        # Plan 3: Seasonally Balanced Alternative
        plans['seasonal_balanced'] = self.find_optimal_leave_dates(
            year, processed_data, 'seasonal_balanced')
        plans['seasonal_balanced']['description'] = "Distributes leave across preferred seasons"

        return plans
