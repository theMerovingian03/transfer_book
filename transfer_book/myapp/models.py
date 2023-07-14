from django.db import models
from django.contrib.auth.models import User
from datetime import date
from django.utils import timezone

# Create your models here.

class Record(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)
    amount = models.PositiveIntegerField(null=True, blank=True)
    date_added = models.DateField(auto_now_add=True)
    date_payed = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.title
    
    class Meta:
        order_with_respect_to = 'user'

    def save(self, *args, **kwargs):
        if self.date_payed is None:
            self.date_payed = timezone.now().date()
        super().save(*args, **kwargs)