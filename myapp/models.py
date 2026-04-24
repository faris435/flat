from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Room_Table(models.Model):
    floor=models.IntegerField()
    roomnumber=models.CharField(max_length=50)
    image=models.FileField()
    details=models.CharField(max_length=200)

class Category_Table(models.Model):
    category=models.CharField(max_length=100)
    
class Service_Provider(models.Model):
    name=models.CharField(max_length=100)
    email=models.CharField(max_length=100)
    phone=models.BigIntegerField()
    CATEGORY=models.ForeignKey(Category_Table,on_delete=models.CASCADE)
    LOGIN=models.ForeignKey(User,on_delete=models.CASCADE)
    Status=models.CharField(max_length=50)
    place=models.CharField(max_length=100)
    post=models.CharField(max_length=100)
    pin=models.IntegerField()
    photo=models.FileField()
    proof=models.FileField()
    
class User_Table(models.Model):
    name=models.CharField(max_length=100)
    email=models.CharField(max_length=100)
    phone=models.BigIntegerField()
    ROOM=models.ForeignKey(Room_Table,on_delete=models.CASCADE)
    photo=models.FileField()
    LOGIN=models.ForeignKey(User,on_delete=models.CASCADE)
    status=models.CharField(max_length=50,default='pending')
    
class Facility_Table(models.Model):
    name=models.CharField(max_length=100)
    description=models.CharField(max_length=200)
    photo=models.FileField()
    Status=models.CharField(max_length=50)

class Service_Table(models.Model):
    name=models.CharField(max_length=100)
    description=models.CharField(max_length=200)
    photo=models.FileField()
    price=models.IntegerField()
    Status=models.CharField(max_length=50)
    PROVIDER=models.ForeignKey(Service_Provider,on_delete=models.CASCADE)
    
class Booking_Table(models.Model):
    USER=models.ForeignKey(User_Table,on_delete=models.CASCADE)
    SERVICE=models.ForeignKey(Service_Table,on_delete=models.CASCADE)
    date=models.DateField()
    Status=models.CharField(max_length=50)
    
class Food_Table(models.Model):
    item=models.CharField(max_length=300)
    description=models.TextField()
    photo=models.FileField()
    price=models.IntegerField()
    quantity=models.CharField(max_length=50)
    mfg_date=models.DateField()
    SERVICE=models.ForeignKey(Service_Provider,on_delete=models.CASCADE)

class Food_Order_Table(models.Model):
    USER=models.ForeignKey(User_Table,on_delete=models.CASCADE)
    FOOD=models.ForeignKey(Food_Table,on_delete=models.CASCADE)
    date=models.DateField()
    quantity=models.CharField(max_length=50)
    Status=models.CharField(max_length=50)
    
class Rating_Table(models.Model):
    USER=models.ForeignKey(User_Table,on_delete=models.CASCADE)
    SERVICE=models.ForeignKey(Service_Table,on_delete=models.CASCADE)
    rating=models.IntegerField()
    review=models.CharField(max_length=200)
    date=models.DateField()

class Complaint_Table(models.Model):
    USER=models.ForeignKey(User_Table,on_delete=models.CASCADE)
    Complain=models.CharField(max_length=200)
    reply=models.CharField(max_length=200)
    date=models.DateField()
    type=models.CharField(max_length=100)
    
class ChatTable(models.Model):
    SENDER=models.ForeignKey(User,on_delete=models.CASCADE,related_name='sender')
    RECEIVER=models.ForeignKey(User,on_delete=models.CASCADE,related_name='receiver')
    message=models.TextField()
    time=models.TimeField(auto_now_add=True)
    date=models.DateField(auto_now_add=True)
    is_read=models.BooleanField(default=False)


