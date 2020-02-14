from django.db import models
from django.core.files.storage import default_storage
import os
from django.dispatch import receiver
from django.core.exceptions import ValidationError


# Sample image models, might need some update
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
        if ext.lower() != '.jpg' and ext.lower() != '.png':
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
