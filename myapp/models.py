from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.db import models


# Create your models here.
class Person(models.Model):
    name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    age = models.IntegerField()
    date = models.DateField(auto_now_add=True)
    email = models.EmailField(max_length=254, null=True, blank=True)


    def __str__(self):
        return self.name + ","+str(self.age) 

class Person2(models.Model):
    name2 = models.CharField(max_length=50)
    age2 = models.IntegerField()
    date2 = models.DateField(auto_now_add=True)


    def __str__(self):
        return self.name2 + ","+str(self.age2) 
    
# -------------------------------------------------------------------------------    
    
class Equipment(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.name} - {self.quantity}"

class Booking(models.Model):
    STATUS_CHOICES = [
        ('approved', 'อนุมัติ'),
        ('pending', 'รออนุมัติ'),
        ('cancelled', 'ยกเลิก'),
    ]

    booking_code = models.CharField(max_length=20, unique=True, blank=True)
    room_name = models.CharField(max_length=100)
    n_req = models.CharField(max_length=100)
    n_ph = models.CharField(max_length=10)
    h_pr = models.CharField(max_length=100)
    n_count = models.IntegerField(default=0)
    n_list = models.CharField(max_length=500, blank=True)
    dpm_sd = models.CharField(max_length=100, default='-')
    topic = models.TextField(blank=True)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='approved')
    description = models.TextField()

    # ManyToManyField to link selected equipment
    equipment_list = models.ManyToManyField(Equipment, blank=True)

    def __str__(self):
        return f"{self.booking_code} - {self.room_name} - {self.topic}"

    def save(self, *args, **kwargs):
        if not self.booking_code:
            prefix = 'SDH680'
            last_booking = Booking.objects.order_by('-id').first()
            if last_booking and last_booking.booking_code:
                try:
                    last_number = int(last_booking.booking_code.replace(prefix, ''))
                except ValueError:
                    last_number = 0
            else:
                last_number = 0

            next_number = last_number + 1
            self.booking_code = f"{prefix}{next_number:04d}"
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.booking_code} - {self.room_name} - {self.topic}"


# วันหยุด ลงปฏิทิน
class Holiday(models.Model):
    title = models.CharField(max_length=100)
    date = models.DateField()

    def __str__(self):
        return f"{self.title} ({self.date})"
    

