import uuid
from django.db import models
from django.contrib.auth.models import User

class Donation(models.Model):
    building = models.CharField(max_length=2)
    flat_number = models.IntegerField()
    phone_number = models.IntegerField()
    amount_paid = models.BooleanField(default=False)
    amount = models.IntegerField(default=0)
    mode = models.CharField(max_length=20)
    committee_member = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    receipt_token = models.CharField(max_length=32, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.receipt_token:
            self.receipt_token = uuid.uuid4().hex
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.building} - {self.flat_number} = {self.amount}' 
    
