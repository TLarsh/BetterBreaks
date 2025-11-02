from celery import shared_task
from django.contrib.auth import get_user_model
from ..services.recommendation_service import RecommendationService

User = get_user_model()

@shared_task
def generate_recommendations_for_all_users():
    """Generate break recommendations for all active users"""
    users = User.objects.filter(is_active=True)
    success_count = 0
    error_count = 0
    
    for user in users:
        try:
            recommendation = RecommendationService.generate_recommendation(user)
            if recommendation:
                success_count += 1
        except Exception as e:
            error_count += 1
            print(f"Error generating recommendation for user {user.id}: {str(e)}")
    
    return f"Generated recommendations for {success_count} users. Errors: {error_count}"

@shared_task
def generate_recommendation_for_user(user_id):
    """Generate break recommendation for a specific user"""
    try:
        user = User.objects.get(id=user_id)
        recommendation = RecommendationService.generate_recommendation(user)
        return f"Successfully generated recommendation for user {user.id}"
    except User.DoesNotExist:
        return f"User with ID {user_id} does not exist"
    except Exception as e:
        return f"Error generating recommendation: {str(e)}"