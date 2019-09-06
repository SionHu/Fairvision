from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.contrib.postgres.fields import ArrayField, JSONField
from django.contrib.sessions.models import Session
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.core.serializers.json import DjangoJSONEncoder
import os

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
    word = models.CharField(max_length=200, unique=True)
    count = models.IntegerField(default=0)
    answer = models.OneToOneField('Answer', on_delete=models.CASCADE, limit_choices_to={'isFinal': True}, primary_key=True, related_name='rephrased')
    @property
    def weight(self):
        return self.answer.count / self.answer.question.answers.count()

class ImageModel(models.Model):
    class Meta:
        ordering = ('img',)

    def get_upload_path(instance, filename):
        ''' Construct the upload path of the file, including the filename itself'''
        real_path = default_storage.upload_lock.key + filename
        return real_path

    def validate_file_extension(value):
        ''' Check if file was named correctly '''
        ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
        if ext.lower() != '.jpg':
            raise ValidationError(u'Unsupported file extension.')
        try:
            int(value.name[-8:-4])
        except Exception:
            raise ValidationError(u'No ID found on filename. Please give a name in the `image_####.jpg` format')
    # name = models.CharField(max_length=64, primary_key=True)
    img = models.ImageField(verbose_name='Image', upload_to=get_upload_path, unique=True, validators=[validate_file_extension])

    def __str__(self):
        return self.img.name

    #show the detailed dataset
    @property
    def dataset(self):
        return self.img.name.split("/")[0]
    @property
    def obj(self):
        return self.img.name.split("/")[1]
    @property
    def imgid(self):
        return int(self.img.name[-8:-4])
    @property
    def datafolder(self):
        return self.img.name.rsplit("/", 1)[0]

# Delete the file on S3 at the same time delete model on Django
@receiver(models.signals.post_delete, sender=ImageModel)
def delete_file(sender, instance, *args, **kwargs):
    """ Deletes image files on `post_delete` """
    instance.img.delete(save=False)


# Instructions on each phase
class Phase01_instruction(models.Model):
    class Meta:
        verbose_name = 'Phase01 Instruction'

    instruction = models.CharField(max_length=150, blank=False, null=True)
    imglink = models.CharField(max_length=100, blank=False, null=True)
    order = models.CharField(max_length=10, blank=False, null=True)

    def get_queryset(self):
        return Phase01_instruction.objects.all()

    def __str__(self):
        return "{0}".format(self.order)

class Phase02_instruction(models.Model):
    class Meta:
        verbose_name = 'Phase02 Instruction'

    instruction = models.CharField(max_length=150, blank=False, null=True)
    imglink = models.CharField(max_length=100, blank=False, null=True)
    order = models.CharField(max_length=10, blank=False, null=True)

    def get_queryset(self):
        return Phase02_instruction.objects.all()

    def __str__(self):
        return "{0}".format(self.order)

class Phase03_instruction(models.Model):
    class Meta:
        verbose_name = 'Phase03 Instruction'

    instruction = models.CharField(max_length=150, blank=False, null=True)
    imglink = models.CharField(max_length=100, blank=False, null=True)
    order = models.CharField(max_length=10, blank=False, null=True)

    def get_queryset(self):
        return Phase03_instruction.objects.all()

    def __str__(self):
        return "{0}".format(self.order)


# Global variable of round number for phase01 and phase02
class Phase(models.Model):
    phase = models.CharField(max_length=1, primary_key=True)
    get = ArrayField(models.IntegerField(), blank=True, default=list)
    post = ArrayField(models.IntegerField(), blank=True, default=list)
    imgset = ArrayField(models.IntegerField(), blank=True, default=list)
    def __str__(self):
        return self.phase

# Array indices for recursion list of phase02
class listArray(models.Model):
    attrlist = ArrayField(models.IntegerField(), blank=True)
    phase = models.CharField(max_length=10, default='phase02')
    def __str__(self):
        return self.phase

# breaking sign for when to stop the game phase
class PhaseBreak(models.Model):
    phase = models.CharField(max_length=10, default='phase02')
    stop = models.BooleanField(default=False)
    def __str__(self):
        return self.phase

# New design, QA pairs for phase 1 that will be collected from the crowd workers
# It could be redundant, so count will be number of the merged ones after merging (we could make a script to create the models updating)
class Question(models.Model):
    hit = models.ForeignKey('HIT', on_delete=models.CASCADE, db_column='assignmentID', related_name='questions')
    text = models.CharField(max_length=64, blank=False, null=False)
    # Boolean telling where this is the final questions for the rest of the phases
    isFinal = models.BooleanField(default=False)
    # The old question that this question was merged to
    mergeParent = models.IntegerField(default=0)
    # ID for reference which questions are for which image
    imageID = ArrayField(models.CharField(max_length=64))
    def __str__(self):
        return self.text

class Answer(models.Model):
    hit = models.ForeignKey('HIT', on_delete=models.CASCADE, db_column='assignmentID', related_name='answers')
    text = models.CharField(max_length=64, blank=True, null=False, unique=False)
    isFinal = models.BooleanField(default=False)
    count = models.IntegerField(default=1)
    # on_delete set to cascade because we would not delete django models until we export and finalize the data and save.
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    # was the answer created on step 1
    imgset = models.IntegerField(default=-1)
    def __str__(self):
        return self.text

class HIT(models.Model):
    assignment_id = models.CharField(verbose_name="Assignment ID", max_length=255, blank=False, null=False, primary_key=True)
    data = JSONField(blank=True, null=True, encoder=DjangoJSONEncoder)
    @property
    def workerID(self):
        return self.data.get('workerId')
    @property
    def hitID(self):
        return self.data.get('hitId')
    def __str__(self):
        return self.assignment_id

# The word instructions show in the modal before the worker starts
class TextInstruction(models.Model):
    phase=models.CharField(max_length=3)
    instruction = models.TextField(blank=False,null=False,unique=False)
    def __str__(self):
        return self.phase
