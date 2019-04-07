from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, Label, ImageModel, Attribute, RoundsNum, listArray, PhaseBreak
from django import forms
from natsort import natsorted

import csv
from django.http import HttpResponse


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
    list_display = ('img', 'allLabel')

class LabelAdmin(admin.ModelAdmin):
    list_filter=('isTaboo', 'name')


def export_csv(self, request, queryset):
    # https://docs.djangoproject.com/en/1.11/howto/outputting-csv/
    # https://stackoverflow.com/questions/18685223/how-to-export-django-model-data-into-csv-file

    # setup csv writer
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment;filename=phase3-attributes.csv'
    writer = csv.writer(response)

    required_field_names = ['word','count']

    field_names = required_field_names.copy()

    writer.writerow(field_names)

    # output data 
    for obj in queryset:
        writer.writerow([getattr(obj, field) for field in field_names])
    return response
export_csv.short_description = "Export selected attributes as csv"

class AttributeAdmin(admin.ModelAdmin):
    actions = [export_csv]
    
admin.site.register(CustomUser, CustomUserAdmin)
# admin.site.register(Zipfile)
admin.site.register(Label, LabelAdmin)
admin.site.register(PhaseBreak)
admin.site.register(RoundsNum)

admin.site.register(listArray)
admin.site.register(Attribute, AttributeAdmin)
#admin.site.register(Attribute)
admin.site.register(ImageModel, ImageModelAdmin)