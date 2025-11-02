from django.db import models

class Hospital(models.Model):
    name = models.CharField(max_length = 255)
    location = models.CharField(max_length = 255)
    critical_priority_avaiable_beds = models.IntegerField()
    top_priority_avaiable_beds = models.IntegerField()
    mid_priority_avaiable_beds = models.IntegerField()
    low_priority_avaiable_beds = models.IntegerField()
    total_beds = models.IntegerField()

    def __str__(self):
        return self.name
class HospitalTransfer(models.Model):
    from_hospital = models.ForeignKey(
        Hospital,
        on_delete=models.CASCADE,
        related_name='transfers_out'
    )
    to_hospital = models.ForeignKey(
        Hospital,
        on_delete=models.CASCADE,
        related_name='transfers_in'
    )
    capacity = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.from_hospital.name} → {self.to_hospital.name} ({self.capacity})"

class Patient(models.Model):
    levels = [
        (1, "Critical"),
        (2, "High"),
        (3, "Medium"),
        (4, "Low"),
    ]
    name = models.CharField(max_length = 255)
    age = models.IntegerField()
    address = models.CharField(max_length = 255,blank = True)
    email = models.EmailField(max_length = 255, blank = True)
    emergency_contact = models.IntegerField(blank = True)
    priority_level = models.IntegerField(choices = levels,default = 3 )
    hospital_name = models.ForeignKey(Hospital,on_delete = models.SET_NULL,null = True,blank = True)

    def __str__(self):
        return self.name
    
class Doctor(models.Model):
    name = models.CharField(max_length = 255)
    spaciality = models.CharField(max_length = 255)
    avaiable = models.BooleanField(default = True)

    def __str__(self):
        return self.name
    
class Resource(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    priority_score = models.IntegerField()
    
    def __str__(self):
        return self.name

class Supply_center(models.Model):
    name = models.CharField(max_length = 100)
    total_stock = models.IntegerField()
    def __str__(self):
        return self.name

class Disaster_zone(models.Model):
    name = models.CharField(max_length = 100)
    demand = models.IntegerField()
    def __str__(self):
        return self.name

class TransportFlow(models.Model):
    center = models.ForeignKey(Supply_center, on_delete=models.CASCADE)
    zone = models.ForeignKey(Disaster_zone, on_delete=models.CASCADE)
    amount_sent = models.IntegerField()

    def __str__(self):
        return f"{self.center.name} → {self.zone.name}: {self.amount_sent} units"
