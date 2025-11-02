from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

# Documentation for UserMetrics API
user_metrics_get_docs = swagger_auto_schema(
    operation_description="Get user metrics for recommendation engine",
    responses={
        200: openapi.Response(
            description="User metrics retrieved successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID),
                    'work_hours_per_week': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'stress_level': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'sleep_quality': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'prefers_travel': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'season_preference': openapi.Schema(type=openapi.TYPE_STRING),
                    'break_type_preference': openapi.Schema(type=openapi.TYPE_STRING),
                    'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                    'updated_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                }
            )
        ),
        404: openapi.Response(description="User metrics not found")
    }
)

user_metrics_post_docs = swagger_auto_schema(
    operation_description="Create or update user metrics for recommendation engine",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['work_hours_per_week', 'stress_level', 'sleep_quality'],
        properties={
            'work_hours_per_week': openapi.Schema(type=openapi.TYPE_INTEGER),
            'stress_level': openapi.Schema(type=openapi.TYPE_INTEGER, description="Scale of 1-10"),
            'sleep_quality': openapi.Schema(type=openapi.TYPE_INTEGER, description="Scale of 1-10"),
            'prefers_travel': openapi.Schema(type=openapi.TYPE_BOOLEAN),
            'season_preference': openapi.Schema(
                type=openapi.TYPE_STRING,
                enum=['winter', 'spring', 'summer', 'fall', 'no_preference']
            ),
            'break_type_preference': openapi.Schema(
                type=openapi.TYPE_STRING,
                enum=['short_frequent', 'long_infrequent', 'mixed']
            ),
        }
    ),
    responses={
        201: openapi.Response(description="User metrics created or updated successfully"),
        400: openapi.Response(description="Invalid input")
    }
)

# Documentation for BreakRecommendation API
break_recommendation_get_docs = swagger_auto_schema(
    operation_description="Get user's break recommendations",
    responses={
        200: openapi.Response(
            description="Break recommendations retrieved successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID),
                        'recommended_start_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
                        'recommended_end_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
                        'predicted_length_days': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'recommended_season': openapi.Schema(type=openapi.TYPE_STRING),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'is_viewed': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'is_accepted': openapi.Schema(type=openapi.TYPE_BOOLEAN, nullable=True),
                        'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                    }
                )
            )
        )
    }
)

break_recommendation_post_docs = swagger_auto_schema(
    operation_description="Generate a new break recommendation",
    manual_parameters=[
        openapi.Parameter(
            name='force',
            in_=openapi.IN_QUERY,
            description='Force generation of a new recommendation even if a recent one exists',
            type=openapi.TYPE_BOOLEAN,
            required=False,
            default=False
        ),
    ],
    responses={
        201: openapi.Response(
            description="Break recommendation generated successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID),
                    'recommended_start_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
                    'recommended_end_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
                    'predicted_length_days': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'recommended_season': openapi.Schema(type=openapi.TYPE_STRING),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'is_viewed': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'is_accepted': openapi.Schema(type=openapi.TYPE_BOOLEAN, nullable=True),
                    'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                }
            )
        ),
        500: openapi.Response(description="Failed to generate recommendation")
    }
)

# Documentation for BreakRecommendationDetail API
break_recommendation_detail_get_docs = swagger_auto_schema(
    operation_description="Get a specific break recommendation",
    responses={
        200: openapi.Response(
            description="Break recommendation retrieved successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID),
                    'recommended_start_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
                    'recommended_end_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
                    'predicted_length_days': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'recommended_season': openapi.Schema(type=openapi.TYPE_STRING),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'is_viewed': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'is_accepted': openapi.Schema(type=openapi.TYPE_BOOLEAN, nullable=True),
                    'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                }
            )
        ),
        404: openapi.Response(description="Recommendation not found")
    }
)

break_recommendation_detail_patch_docs = swagger_auto_schema(
    operation_description="Update a specific recommendation (mark as viewed/accepted)",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'is_viewed': openapi.Schema(type=openapi.TYPE_BOOLEAN),
            'is_accepted': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        }
    ),
    responses={
        200: openapi.Response(description="Recommendation updated successfully"),
        400: openapi.Response(description="Invalid input"),
        404: openapi.Response(description="Recommendation not found")
    }
)

# Documentation for convert_to_break_plan API
convert_to_break_plan_docs = swagger_auto_schema(
    operation_description="Convert a recommendation to a break plan",
    responses={
        201: openapi.Response(
            description="Break plan created successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'break_plan_id': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID),
                }
            )
        ),
        404: openapi.Response(description="Recommendation not found")
    }
)