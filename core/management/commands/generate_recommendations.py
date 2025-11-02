from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.services.recommendation_service import RecommendationService

User = get_user_model()

class Command(BaseCommand):
    help = 'Generate break recommendations for all users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=str,
            help='Generate recommendations for a specific user by ID',
        )

    def handle(self, *args, **options):
        user_id = options.get('user_id')
        
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                self.generate_for_user(user)
                self.stdout.write(self.style.SUCCESS(f'Successfully generated recommendation for user {user.email}'))
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'User with ID {user_id} does not exist'))
        else:
            # Generate for all active users
            users = User.objects.filter(is_active=True)
            count = 0
            
            for user in users:
                success = self.generate_for_user(user)
                if success:
                    count += 1
            
            self.stdout.write(self.style.SUCCESS(f'Successfully generated recommendations for {count} users'))
    
    def generate_for_user(self, user):
        try:
            recommendation = RecommendationService.generate_recommendation(user)
            return recommendation is not None
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error generating recommendation for {user.email}: {str(e)}'))
            return False