from django.db import models

class Hospital(models.Model):
    name = models.CharField(max_length = 255)
    location = models.CharField(max_length = 255)
    top_priority_avaiable_beds = models.IntegerField()
    mid_priority_avaiable_beds = models.IntegerField()
    low_priority_avaiable_beds = models.IntegerField()
    total_beds = models.IntegerField()
class Patient(models.Model):
    levels = [
        (1, "Critical"),
        (2, "High"),
        (3, "Medium"),
        (4, "Low"),
    ]
    name = models.CharField(max_length = 255)
    age = models.IntegerField()
    address = models.CharField(max_length = 255)
    email = models.EmailField(max_length = 255)
    emargency_contact = models.IntegerField()
    priority_level = models.IntegerField(choices = levels,default = 3 )
    hospital_name = models.ForeignKey(Hospital,on_delete = models.SET_NULL,null = True,blank = True)
class Doctor(models.Model):
    name = models.CharField(max_length = 255)
    spaciality = models.CharField(max_length = 255)
    avaiable = models.BooleanField(default = True)
class Resource(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    priority_score = models.IntegerField()

