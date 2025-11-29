from email.policy import default

from django.db import models

class Resource(models.Model):
    name = models.CharField(max_length=100)
    priority_score = models.IntegerField()
    quantity = models.IntegerField()
    volume = models.IntegerField()
    def __str__(self):
        return self.name

class TransportFlow(models.Model):
    A = models.CharField(max_length=100)
    to = models.CharField(max_length=100)
    max_capacity = models.IntegerField()
    amount_sent = models.IntegerField(null = True, blank = True)

    def __str__(self):
        return f"{self.A} → {self.to}: {self.amount_sent} units"
class supply_max_cap(models.Model):
    A = models.CharField(max_length=100)
    to = models.CharField(max_length=100)
    capacity = models.IntegerField()