from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # bools to keep track of types of users
    is_player = models.BooleanField(default=False)
    is_requester = models.BooleanField(default=False)
    
    def __str__(self):
        return self.email
    
class Player(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    score = models.IntegerField(default=0)
    # age = models.IntegerField(verbose_name='Age(Optional', blank=True, null=True)
    #level = models.IntegerField(default=0, max)
    #pic = models.ImageField(upload_to="PlayerProfile", blank=True, null=True)

    

class Requester(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    occupation = models.CharField(verbose_name='Occupation(Optional)', max_length=50, blank=True, null=True)


# Label that returns to the user
''' class Label(models.Model):
    name = models.CharField(max_length=20, primary_key=True)
    isTaboo = models.BooleanField(default=False)
    taboo = models.ForeignKey(Zipfile)

 
# class Zipfile(models.Model):
    #One requester can have multiple uploads
    uploader = models.ForeignKey(Requester)
    zip_upload= models.FileField(blank=True, upload_to="hello")


# class Image(models.Model):
'''
class Document(models.Model):
    description = models.CharField(max_length=255, blank=True)
    document = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
