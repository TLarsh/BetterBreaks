from django.db import models
from django.conf import settings
import uuid
from django.utils import timezone
from .user_models import User



class Badge(models.Model):
    BADGE_TYPES = [
        ('weekend_breaker', 'Weekend Breaker'),
        ('holiday_master', 'Holiday Master'),
        ('consistent_breaker', 'Consistent Breaker'),
        ('break_pro', 'Break Pro'),
        ('wellness_warrior', 'Wellness Warrior'),
        ('perfect_planner', 'Perfect Planner'),
        ('weekend_recharger', 'Weekend Recharger')
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='badges')
    badge_type = models.CharField(max_length=50, choices=BADGE_TYPES)
    earned_date = models.DateField(auto_now_add=True)
    description = models.TextField()
    requirements_met = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'badge_type')
        ordering = ['badge_type']
    
    def __str__(self):
        return f"{self.user.email}'s {self.get_badge_type_display()} Badge"
    

    @property
    def name(self):
     
        return self.get_badge_type_display()