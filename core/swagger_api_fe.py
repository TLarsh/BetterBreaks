# from rest_framework import permissions
# from drf_yasg.generators import OpenAPISchemaGenerator
# from drf_yasg.views import get_schema_view
# from drf_yasg import openapi
# import os

# class SchemaGenerator(OpenAPISchemaGenerator):
#   def get_schema(self, request=None, public=False):
#     schema = super(SchemaGenerator, self).get_schema(request, public)
#     schema.basePath = os.path.join(schema.basePath, 'v1/')
#     return schema

# schema_view = get_schema_view(
#     openapi.Info(
#         title="BetterBreaks",
#         default_version='v1',
#         description="BetterBreaks Backend",
#         terms_of_service="https://testing.betterbreaks.org",
#         contact=openapi.Contact(email="support@betterbreaks.org"),
#         license=openapi.License(name="Proprietary"),
#     ),
#     url="https://api.betterbreaks.org/",
#     public=True,
#     permission_classes=(permissions.AllowAny,),
#     generator_class=SchemaGenerator,
# )





# swagger_api_fe.py

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import MoodCheckInSerializer, MoodHistorySerializer, LeaveBalanceSerializer, BreakPreferencesSerializer, BreakPlanSerializer, EventSerializer, BookingSerializer, PublicHolidaySerializer, BreakScoreSerializer, OptimizationScoreSerializer, StreakScoreSerializer, BadgeSerializer
from rest_framework import status


# ========== Swagger Docs for GET Schedule ==========
schedule_get_schema = swagger_auto_schema(
    operation_summary="Retrieve user's full schedule",
    tags=["User Schedule"],
    responses={
        200: openapi.Response(
            description="Schedule retrieved successfully.",
        ),
        500: openapi.Response(description="Internal server error.")
    }
)

# ========== Swagger Docs for POST Schedule ==========

schedule_post_schema = swagger_auto_schema(
    operation_summary="Update user's full schedule",
    tags=["User Schedule"],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "working_pattern": openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "pattern_type": openapi.Schema(type=openapi.TYPE_STRING),
                    "days_on": openapi.Schema(type=openapi.TYPE_INTEGER),
                    "days_off": openapi.Schema(type=openapi.TYPE_INTEGER),
                    "start_date": openapi.Schema(type=openapi.TYPE_STRING, format="date"),
                    "rotation_pattern": openapi.Schema(type=openapi.TYPE_STRING),
                    "shift_preview": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Items(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(type=openapi.TYPE_STRING)
                        )
                    )
                }
            ),
            "blackout_dates": openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "start_date": openapi.Schema(type=openapi.TYPE_STRING, format="date-time"),
                        "end_date": openapi.Schema(type=openapi.TYPE_STRING, format="date-time"),
                        "description": openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            "optimization_goals": openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_STRING)
            )
        },
        required=["working_pattern"]
    ),
    responses={
        200: openapi.Response(description="Schedule updated successfully."),
        400: openapi.Response(description="Validation failed."),
        500: openapi.Response(description="Internal server error."),
    }
)






# ----------- GOOGLE LOGIN SCHEMA -----------
google_login_schema = swagger_auto_schema(
    operation_summary="Login with Google",
    operation_description=(
        "Authenticate a user using Google OAuth.\n"
        "- Provide either the `access_token` (from Google) or the `code` (OAuth authorization code).\n"
        "- The callback URL must match the one configured in Google Cloud Console."
    ),
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "access_token": openapi.Schema(type=openapi.TYPE_STRING, description="Google OAuth access token"),
            "code": openapi.Schema(type=openapi.TYPE_STRING, description="Google OAuth authorization code"),
        },
        example={
            "access_token": "ya29.a0AfH6SMBEXAMPLE...",
            "code": "4/0AX4XfWhExampleCodeFromGoogle"
        }
    ),
    responses={
        200: openapi.Response(
            description="Login successful",
            examples={
                "application/json": {
                    "message": "Login successful",
                    "status": True,
                    "data": {
                        "refresh": "your_refresh_token",
                        "access": "your_access_token",
                        "email": "user@example.com",
                        "full_name": "John Doe"
                    },
                    "errors": None
                }
            }
        )
    }
)

# ----------- FACEBOOK LOGIN SCHEMA -----------
facebook_login_schema = swagger_auto_schema(
    operation_summary="Login with Facebook",
    operation_description=(
        "Authenticate a user using Facebook OAuth.\n"
        "- Provide the `access_token` obtained from Facebook's OAuth flow.\n"
        "- The callback URL must match the one configured in Facebook Developer Dashboard."
    ),
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "access_token": openapi.Schema(type=openapi.TYPE_STRING, description="Facebook OAuth access token"),
        },
        example={
            "access_token": "EAAJZCwExampleFacebookToken"
        }
    ),
    responses={
        200: openapi.Response(
            description="Login successful",
            examples={
                "application/json": {
                    "message": "Login successful",
                    "status": True,
                    "data": {
                        "refresh": "your_refresh_token",
                        "access": "your_access_token",
                        "email": "user@example.com",
                        "full_name": "John Doe"
                    },
                    "errors": None
                }
            }
        )
    }
)

# ----------- TWITTER LOGIN SCHEMA -----------
twitter_login_schema = swagger_auto_schema(
    operation_summary="Login with Twitter",
    operation_description=(
        "Authenticate a user using Twitter OAuth.\n"
        "- For OAuth 1.0a: Provide `access_token` and `access_token_secret`.\n"
        "- For OAuth 2.0: Provide the `code` from Twitter's OAuth flow."
    ),
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "access_token": openapi.Schema(type=openapi.TYPE_STRING, description="Twitter OAuth access token"),
            "access_token_secret": openapi.Schema(type=openapi.TYPE_STRING, description="Twitter OAuth token secret (OAuth 1.0a only)"),
            "code": openapi.Schema(type=openapi.TYPE_STRING, description="Twitter OAuth authorization code (OAuth 2.0 only)"),
        },
        example={
            "access_token": "ExampleTwitterAccessToken",
            "access_token_secret": "ExampleTwitterTokenSecret",
            "code": "ExampleTwitterOAuthCode"
        }
    ),
    responses={
        200: openapi.Response(
            description="Login successful",
            examples={
                "application/json": {
                    "message": "Login successful",
                    "status": True,
                    "data": {
                        "refresh": "your_refresh_token",
                        "access": "your_access_token",
                        "email": "user@example.com",
                        "full_name": "John Doe"
                    },
                    "errors": None
                }
            }
        )
    }
)




# Swagger for Mood Check-in
mood_checkin_schema = swagger_auto_schema(
    # method="post",
    tags=["Mood Tracking"],
    operation_summary="Mood Check-In",
    operation_description="Record the user's current mood with an optional note.",
    request_body=MoodCheckInSerializer,
    responses={
        status.HTTP_201_CREATED: openapi.Response(
            description="Mood check-in successful",
            schema=MoodCheckInSerializer
        ),
        status.HTTP_400_BAD_REQUEST: "Validation error"
    }
)

# Swagger for Mood History
mood_history_schema = swagger_auto_schema(
    # method="get",
    tags=["Mood Tracking"],
    operation_summary="Retrieve Mood History",
    operation_description="Get the mood history for the authenticated user. Optionally filter by start_date and end_date (YYYY-MM-DD).",
    manual_parameters=[
        openapi.Parameter(
            "start_date",
            openapi.IN_QUERY,
            description="Filter moods from this date (YYYY-MM-DD)",
            type=openapi.TYPE_STRING
        ),
        openapi.Parameter(
            "end_date",
            openapi.IN_QUERY,
            description="Filter moods until this date (YYYY-MM-DD)",
            type=openapi.TYPE_STRING
        ),
    ],
    responses={
        status.HTTP_200_OK: openapi.Response(
            description="Mood history retrieved successfully",
            schema=MoodHistorySerializer(many=True)
        )
    }
)



first_login_setup_docs = swagger_auto_schema(
    operation_summary="First Login Setup",
    operation_description="Initial setup for LeaveBalance, Preferences, and optional BreakPlan.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "LeaveBalance": openapi.Schema(
                type=openapi.TYPE_OBJECT, 
                properties={
                    "anual_leave_balance": openapi.Schema(type=openapi.TYPE_INTEGER, example=60),
                    "anual_leave_refresh_date": openapi.Schema(type=openapi.FORMAT_DATE, example="2025-01-01"),
                    "already_used_balance": openapi.Schema(type=openapi.TYPE_INTEGER, example=0)
                },
                required=["anual_leave_balance", "anual_leave_refresh_date", "already_used_balance"]
            ),
            "Preferences": openapi.Schema(
                type=openapi.TYPE_OBJECT, 
                properties={
                    "preference": openapi.Schema(type=openapi.TYPE_STRING, example="long_weekends"),
                    "weather_based_recommendation": openapi.Schema(type=openapi.TYPE_BOOLEAN, example=False),
                    "to_be_confirmed": openapi.Schema(type=openapi.TYPE_BOOLEAN, example=False)
                },
                required=["preference"]
            ),
            "BreakPlan": openapi.Schema(
                type=openapi.TYPE_OBJECT, 
                properties={
                    "startDate": openapi.Schema(type=openapi.FORMAT_DATETIME, example="2025-08-10T09:00:00Z"),
                    "endDate": openapi.Schema(type=openapi.FORMAT_DATETIME, example="2025-08-15T18:00:00Z"),
                    "description": openapi.Schema(type=openapi.TYPE_STRING, example="Summer vacation"),
                    "status": openapi.Schema(type=openapi.TYPE_STRING, example="planned"),
                    "type": openapi.Schema(type=openapi.TYPE_STRING, example="vacation")
                },
                required=["startDate", "endDate"]
            ),
        }
    ),
    responses={
        status.HTTP_201_CREATED: openapi.Response(
            description="Setup completed successfully",
        ),
        status.HTTP_400_BAD_REQUEST: "Validation error"
    }
)




# ---- Events ----
event_list_docs = swagger_auto_schema(
    operation_summary="List all events",
    operation_description="Retrieve all events with optional filters for title, location, and date range.",
    manual_parameters=[
        openapi.Parameter("title", openapi.IN_QUERY, description="Filter by title", type=openapi.TYPE_STRING),
        openapi.Parameter("location", openapi.IN_QUERY, description="Filter by location", type=openapi.TYPE_STRING),
        openapi.Parameter("start_date", openapi.IN_QUERY, description="Filter by start date (YYYY-MM-DD)", type=openapi.TYPE_STRING),
        openapi.Parameter("end_date", openapi.IN_QUERY, description="Filter by end date (YYYY-MM-DD)", type=openapi.TYPE_STRING),
    ],
    responses={200: EventSerializer(many=True)}
)


# ---- Bookings ----
book_event_docs = swagger_auto_schema(
    operation_summary="Book an event",
    operation_description="Authenticated users can book an event by providing the event ID in the URL.",
    responses={201: BookingSerializer()}
)


# ---- Payments ----
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

# --- Payment Annotations ---

initiate_payment_docs = swagger_auto_schema(
    operation_summary="Initiate Payment",
    operation_description="Starts a payment process for a booking using Paystack.",
    responses={
        200: openapi.Response(
            description="Payment initiation successful",
            examples={
                "application/json": {
                    "message": "Payment initiated successfully",
                    "status": True,
                    "data": {
                        "authorization_url": "https://checkout.paystack.com/xyz123",
                        "access_code": "xyz123",
                        "reference": "ref123"
                    },
                    "errors": None
                }
            },
        ),
        404: openapi.Response(description="Booking not found"),
    }
)

verify_payment_docs = swagger_auto_schema(
    operation_summary="Verify Payment",
    operation_description="Verifies a Paystack payment and updates booking/payment status.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "reference": openapi.Schema(type=openapi.TYPE_STRING, description="Paystack payment reference"),
        },
        required=["reference"],
    ),
    responses={
        200: openapi.Response(
            description="Payment verification successful",
            examples={
                "application/json": {
                    "message": "Payment verified successfully",
                    "status": True,
                    "data": {"status": "success"},
                    "errors": None
                }
            },
        ),
        400: openapi.Response(description="Missing or invalid reference"),
        404: openapi.Response(description="Booking not found"),
    }
)


##### Weather Forecast Swagger #####


weather_forecast_params = [
    openapi.Parameter(
        'lat', openapi.IN_QUERY, description="Latitude", type=openapi.TYPE_NUMBER, required=True
    ),
    openapi.Parameter(
        'lon', openapi.IN_QUERY, description="Longitude", type=openapi.TYPE_NUMBER, required=True
    ),
]

weather_forecast_response = openapi.Response(
    description="8-day weather forecast",
    examples={
        "application/json": [
            {
                "dt": 1692979200,
                "sunrise": 1692957600,
                "sunset": 1693004400,
                "temp": {"day": 28.5, "min": 24.0, "max": 30.0},
                "weather": [{"id": 500, "main": "Rain", "description": "light rain"}],
                # ...other fields...
            },
            # ... up to 8 items ...
        ]
    }
)

weather_forecast_schema = swagger_auto_schema(
    manual_parameters=weather_forecast_params,
    responses={200: weather_forecast_response},
    operation_description="Get 8-day weather forecast for a given latitude and longitude."
)





# --- HolidayDetailView Swagger decorators ---

holiday_detail_get = swagger_auto_schema(
    operation_summary="Get a specific holiday",
    operation_description="Retrieve details of a holiday by its ID, only if it belongs to the logged-in user's holiday calendar.",
    responses={
        200: PublicHolidaySerializer,
        404: "Holiday not found",
    },
)

holiday_detail_put = swagger_auto_schema(
    operation_summary="Update a specific holiday",
    operation_description="Update details of an existing holiday by ID, only if it belongs to the logged-in user's holiday calendar.",
    request_body=PublicHolidaySerializer,
    responses={
        200: PublicHolidaySerializer,
        400: "Validation error",
        404: "Holiday not found",
    },
)

holiday_detail_delete = swagger_auto_schema(
    operation_summary="Delete a specific holiday",
    operation_description="Delete a holiday by its ID, only if it belongs to the logged-in user's holiday calendar.",
    responses={
        204: "Holiday deleted successfully",
        404: "Holiday not found",
    },
)



# --- UpcomingHolidaysView Swagger decorator ---

upcoming_holidays_get = swagger_auto_schema(
    operation_summary="Get upcoming holidays",
    operation_description=(
        "Retrieve the next 10 upcoming holidays from the logged-in user's holiday calendar. "
        "Results are ordered by date in ascending order."
    ),
    responses={200: PublicHolidaySerializer(many=True)},
)


# --- BreakLogListCreateView Swagger decorators ---

break_log_list = swagger_auto_schema(
    operation_summary="Get all break logs",
    operation_description="Retrieve all break logs (BreakScore records) for the currently logged-in user.",
    responses={200: BreakScoreSerializer(many=True)},
)

break_log_create = swagger_auto_schema(
    operation_summary="Log a new break",
    operation_description=(
        "Create a new BreakScore entry for the logged-in user. "
        "Also updates streak data and the user's total break score."
    ),
    request_body=BreakScoreSerializer,
    responses={201: BreakScoreSerializer},
)


# --- BreakLogDetailView Swagger ---

break_log_retrieve = swagger_auto_schema(
    operation_summary="Get a specific break log",
    operation_description="Retrieve a BreakScore entry by its ID (must belong to the logged-in user).",
    responses={200: BreakScoreSerializer},
)

break_log_update = swagger_auto_schema(
    operation_summary="Update a specific break log",
    operation_description="Update an existing BreakScore entry by ID (must belong to the logged-in user).",
    request_body=BreakScoreSerializer,
    responses={200: BreakScoreSerializer},
)

break_log_delete = swagger_auto_schema(
    operation_summary="Delete a specific break log",
    operation_description="Delete an existing BreakScore entry by ID (must belong to the logged-in user).",
    responses={204: "Deleted successfully"},
)



# --- OptimizationListCreateView ---
optimization_list = swagger_auto_schema(
    operation_summary="Get all optimization scores",
    operation_description="Retrieve all optimization scores for the logged-in user.",
    responses={200: OptimizationScoreSerializer(many=True)},
)

optimization_create = swagger_auto_schema(
    operation_summary="Create a new optimization score",
    operation_description="Create a new optimization score entry for the logged-in user.",
    request_body=OptimizationScoreSerializer,
    responses={201: OptimizationScoreSerializer},
)

# --- OptimizationDetailView ---
optimization_retrieve = swagger_auto_schema(
    operation_summary="Get a specific optimization score",
    operation_description="Retrieve a single optimization score by its ID.",
    responses={200: OptimizationScoreSerializer},
)

optimization_update = swagger_auto_schema(
    operation_summary="Update a specific optimization score",
    operation_description="Update a single optimization score by its ID.",
    request_body=OptimizationScoreSerializer,
    responses={200: OptimizationScoreSerializer},
)

optimization_delete = swagger_auto_schema(
    operation_summary="Delete a specific optimization score",
    operation_description="Delete a single optimization score by its ID.",
    responses={204: "Deleted successfully"},
)

# --- OptimizationCalculateView ---
optimization_calculate = swagger_auto_schema(
    operation_summary="Calculate optimization score",
    operation_description="Calculate the user's optimization score based on break preferences and working pattern. "
                          "If a score exists for today, it will be updated.",
    responses={200: OptimizationScoreSerializer},
)



# --- Score Summary ---
score_summary = swagger_auto_schema(
    operation_summary="Get user's score summary",
    operation_description="Retrieve the user's total break score, highest streak, recent breaks, streak history, "
                          "and latest optimization score.",
    responses={200: "Summary with scores and streaks"}
)

# --- StreakListCreateView ---
streak_list = swagger_auto_schema(
    operation_summary="Get all streak scores",
    operation_description="Retrieve all streak scores for the logged-in user.",
    responses={200: StreakScoreSerializer(many=True)},
)

streak_create = swagger_auto_schema(
    operation_summary="Create a new streak score",
    operation_description="Create a new streak score entry for the logged-in user.",
    request_body=StreakScoreSerializer,
    responses={201: StreakScoreSerializer},
)

# --- StreakDetailView ---
streak_retrieve = swagger_auto_schema(
    operation_summary="Get a specific streak score",
    operation_description="Retrieve a single streak score by its ID.",
    responses={200: StreakScoreSerializer},
)

streak_update = swagger_auto_schema(
    operation_summary="Update a specific streak score",
    operation_description="Update a single streak score by its ID.",
    request_body=StreakScoreSerializer,
    responses={200: StreakScoreSerializer},
)

streak_delete = swagger_auto_schema(
    operation_summary="Delete a specific streak score",
    operation_description="Delete a single streak score by its ID.",
    responses={204: "Deleted successfully"},
)



# --- BadgeListCreateView ---
badge_list = swagger_auto_schema(
    operation_summary="Get all badges",
    operation_description="Retrieve all badges earned by the logged-in user.",
    responses={200: BadgeSerializer(many=True)},
)

badge_create = swagger_auto_schema(
    operation_summary="Create a new badge",
    operation_description="Manually create a badge for the logged-in user.",
    request_body=BadgeSerializer,
    responses={201: BadgeSerializer},
)

# --- BadgeDetailView ---
badge_retrieve = swagger_auto_schema(
    operation_summary="Get a specific badge",
    operation_description="Retrieve details of a badge by its ID.",
    responses={200: BadgeSerializer},
)

badge_update = swagger_auto_schema(
    operation_summary="Update a specific badge",
    operation_description="Update a badge by its ID.",
    request_body=BadgeSerializer,
    responses={200: BadgeSerializer},
)

badge_delete = swagger_auto_schema(
    operation_summary="Delete a specific badge",
    operation_description="Delete a badge by its ID.",
    responses={204: "Deleted successfully"},
)

# --- BadgeEligibilityView ---
badge_eligibility = swagger_auto_schema(
    operation_summary="Check and award eligible badges",
    operation_description="Check if the logged-in user qualifies for new badges based on activity "
                          "and award them if eligible.",
    responses={200: BadgeSerializer(many=True)},
)