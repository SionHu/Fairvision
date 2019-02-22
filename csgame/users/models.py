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
    age = models.IntegerField(verbose_name='Age(Optional', blank=True, null=True)
    level = models.IntegerField(default=0)
    pic = models.ImageField(upload_to="PlayerProfile/", blank=True, null=True)

    
# Class that will not be used right now
class Requester(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    occupation = models.CharField(verbose_name='Occupation(Optional)', max_length=50, blank=True, null=True)

# Label that returns to the user
class Label(models.Model):
    name = models.CharField(max_length=20, primary_key=True)
    isTaboo = models.BooleanField(default=False)
    # taboo = model.ForeignKey(ImageModel)

class Zipfile(models.Model):
    # One requester can have multiple uploads, not useful so far
    # uploader = models.ForeignKey(Requester)
    # local repository upload for testing
    zip_upload= models.FileField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    taboo1 = models.ManyToManyField(Label, related_name='first_taboo')
    taboo2 = models.ManyToManyField(Label, related_name='second_taboo')
    taboo3 = models.ManyToManyField(Label, related_name='third_taboo')

    def __str__(self):
        return self.zip_upload.name


# Document testing for local upload
class Document(models.Model):
    description = models.CharField(max_length=255, blank=True)
    document = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)


