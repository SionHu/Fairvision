from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver

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

    
# Class that will not be used right now, but potentially could be expanded in the future
'''
class Requester(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    occupation = models.CharField(verbose_name='Occupation(Optional)', max_length=50, blank=True, null=True)
'''

# Label that returns to the user
class Label(models.Model):
    name = models.CharField(max_length=20, primary_key=True)
    isTaboo = models.BooleanField(default=False)
    # taboo = model.ForeignKey(ImageModel)
    def __str__(self):
        return self.name

# Class not needed right now, but potentially needed to be used in the future
'''
class Zipfile(models.Model):
    # One requester can have multiple uploads, not useful so far
    # uploader = models.ForeignKey(Requester)
    # local repository upload for testing
    zip_upload= models.FileField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    taboo_words_1 = models.CharField(verbose_name='Taboo Word 1', max_length=20, default='N/A')
    taboo_words_2 = models.CharField(verbose_name='Taboo Word 2', max_length=20, default='N/A')
    taboo_words_3 = models.CharField(verbose_name='Taboo Word 3', max_length=20, default='N/A')
    tb = models.ManyToManyField(Label, related_name='taboowords')

    def __str__(self):
        return self.zip_upload.name

# Delete the file on S3 at the same time delete model on Django
@receiver(models.signals.post_delete, sender=Zipfile)
def delete_file(sender, instance, *args, **kwargs):
    """ Deletes image files on `post_delete` """
    instance.zip_upload.delete(save=False)
'''

# Phase 03: attributes that we ask and decide for dataset
class Attribute(models.Model):
    word = models.CharField(max_length=20, primary_key=True)
    count = models.IntegerField(default=0)

class ImageModel(models.Model):
    # name = models.CharField(max_length=64, primary_key=True)
    img = models.ImageField(upload_to="airplanes/")
    label = models.ManyToManyField(Label, related_name='labels', blank=True)
    def __str__(self):
        return self.img.name


# Delete the file on S3 at the same time delete model on Django
@receiver(models.signals.post_delete, sender=ImageModel)
def delete_file(sender, instance, *args, **kwargs):
    """ Deletes image files on `post_delete` """
    instance.img.delete(save=False)

# Instructions on each phase
class Phase01_instruction(models.Model):
    class Meta:
        verbose_name = 'Phase01 Instruction'
        
    instruction = models.CharField(max_length=50, blank=False, null=True)
    imglink = models.CharField(max_length=100, blank=False, null=True)
    order = models.CharField(max_length=10, blank=False, null=True)
    
    def get_queryset(self):
        return Phase01_instruction.objects.all()
    
    def __str__(self):
        return "{0}".format(self.order)
    
class Phase02_instruction(models.Model):
    class Meta:
        verbose_name = 'Phase02 Instruction'
        
    instruction = models.CharField(max_length=50, blank=False, null=True)
    imglink = models.CharField(max_length=100, blank=False, null=True)
    order = models.CharField(max_length=10, blank=False, null=True)
    
    def get_queryset(self):
        return Phase02_instruction.objects.all()
    
    def __str__(self):
        return "{0}".format(self.order)

class Phase03_instruction(models.Model):
    class Meta:
        verbose_name = 'Phase03 Instruction'
        
    instruction = models.CharField(max_length=50, blank=False, null=True)
    imglink = models.CharField(max_length=100, blank=False, null=True)
    order = models.CharField(max_length=10, blank=False, null=True)
    
    def get_queryset(self):
        return Phase03_instruction.objects.all()
    
    def __str__(self):
        return "{0}".format(self.order)

