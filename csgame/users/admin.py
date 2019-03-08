from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from natsort import natsorted

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, Label, ImageModel
from django import forms

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    
class ImageModelForm(forms.ModelForm):
    
    img = forms.ImageField(widget=forms.FileInput(attrs={'multiple': True}), help_text=('Optional image (2.5 MB or less)'), required=True)
    
    class Meta:
        Model = ImageModel
        fields = ('img', 'label')
        
    def save(self, *args, **kwargs):
        # multiple file upload
        # NB: does not respect 'commit' kwarg
        # idk why but seems like the last index in the file_list will be saved automatically. 
        # if not specify the length there will be a ValueError: I/O operation on closed file. And images will be uploaded but no model exists.
        
        file_list = natsorted(self.files.getlist('img'.format(self.prefix)), key=lambda file: file.name)
        self.instance.image = file_list[0]
        # print("self instance image:", self.instance.image)
        length = len(file_list) - 1
        for file in file_list[0: length]:
            # print("I got file: ", file)
            ImageModel.objects.create(
                img=file,
            )
        return super().save(*args, **kwargs)


class ImageModelAdmin(admin.ModelAdmin):
    model = ImageModel
    form = ImageModelForm
    
admin.site.register(CustomUser, CustomUserAdmin)
# admin.site.register(Zipfile)
admin.site.register(Label)
admin.site.register(ImageModel, ImageModelAdmin)