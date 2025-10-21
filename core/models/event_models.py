from django.db import models



class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    capacity = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to="events/", blank=True, null=True)  # NEW field

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title



