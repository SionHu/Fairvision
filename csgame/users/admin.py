from django.conf import settings
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.core.files.storage import default_storage
from django.db import transaction

from .fields import ListTextInput
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, ImageModel, Attribute, RoundsNum, PhaseBreak, Phase01_instruction, Phase02_instruction, Phase03_instruction


from django import forms
from natsort import natsorted

import csv, itertools, operator
from django.http import HttpResponse

def sort_uniq(sequence):
    return map(operator.itemgetter(0), itertools.groupby(natsorted(sequence)))

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm

def getFolderChoices():
    #calculate the options for the folder
    setChoices = []
    objChoices = []
    for dataset in default_storage.listdir('')[0]:
        if dataset is not 'unknown':
            setChoices.append(dataset)
            objChoices.extend(object for object in default_storage.listdir(dataset)[0] if object is not 'unknown')
    return natsorted(setChoices), sort_uniq(objChoices)

class ImageModelForm(forms.ModelForm):
    img = forms.ImageField(label='Image', widget=forms.FileInput(attrs={'multiple': True}), help_text=('Images to upload to S3 (%.1f MB or less). We only allow JPG files.' % (settings.DATA_UPLOAD_MAX_MEMORY_SIZE / 1048576,)), required=True)
    set = forms.CharField(required=True)
    object = forms.CharField(required=True)
    
    class Meta:
        Model = ImageModel
        fields = ('img', )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            self.fields['set'].widget = forms.HiddenInput()
            self.fields['object'].widget = forms.HiddenInput()
            self.fields['set'].required = False
            self.fields['object'].required = False

            # get image preview, works now
            self.url = default_storage.url(self.instance.img.name)
        else:

            setChoices, objChoices = getFolderChoices()
            # auto suggestions that pop up when typing in input text field of set or object
            self.fields['set'].widget=ListTextInput(setChoices, 'set')
            self.fields['object'].widget=ListTextInput(objChoices, 'object')
            self.url = None
        
    def save(self, *args, **kwargs):
        if self.fields['set'].required:
            # multiple file upload
            # NB: does not respect 'commit' kwarg
            with transaction.atomic(), default_storage.upload_lock(self.cleaned_data['set'], self.cleaned_data['object']):
                file_list = natsorted(self.files.getlist('img'.format(self.prefix)), key=operator.attrgetter('name'))
                self.instance.img = file_list[0]
                output = super().save(*args, **kwargs)
                # save the rest of the images to the instances
                ImageModel.objects.bulk_create([
                    ImageModel(img=file) for file in file_list[1:]
                ])
            return output
        else:
            return super().save(*args, **kwargs)


# Filter for dataset folder
class ImageModelDatasetListFilter(admin.SimpleListFilter):
    title = 'dataset'
    parameter_name = 'dataset'
    def lookups(self, request, model_admin):
        ''' Get list of all datasets in the database '''
        return [(name, name) for name in getFolderChoices()[0]]
    def queryset(self, request, queryset):
        val = self.value()
        return queryset.filter(img__contains=val+'/') if val else queryset

# Filter for object folder
class ImageModelObjectListFilter(admin.SimpleListFilter):
    title = 'object'
    parameter_name = 'object'
    def lookups(self, request, model_admin):
        ''' Get list of all object types in the database '''
        return [(name, name) for name in getFolderChoices()[1]]
    def queryset(self, request, queryset):
        val = self.value()
        return queryset.filter(img__contains='/'+val+'/') if val else queryset

class ImageModelAdmin(admin.ModelAdmin):
    form = ImageModelForm
    fields = ('img', 'set', 'object')
    list_display = ('img',)
    list_display_links = ('img',)
    list_filter = (ImageModelDatasetListFilter, ImageModelObjectListFilter)
    
    def get_readonly_fields(self, request, obj=None):
        return [] if obj is None else ['img']

def export_csv(filename, field_names):
    def export(self, request, queryset):
        # https://docs.djangoproject.com/en/1.11/howto/outputting-csv/
        # https://stackoverflow.com/questions/18685223/how-to-export-django-model-data-into-csv-file

        # setup csv writer
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment;filename='+filename
        writer = csv.writer(response)

        writer.writerow(field_names)

        # output data
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])
        return response
    export.short_description = "Export selected %(verbose_name_plural)s as csv"
    return export

class AttributeAdmin(admin.ModelAdmin):
    actions = [export_csv('phase3-attributes.csv', ['word','count'])]

    
admin.site.register(CustomUser, CustomUserAdmin)
# admin.site.register(Zipfile)
admin.site.register(PhaseBreak)
admin.site.register(RoundsNum)

admin.site.register(Attribute, AttributeAdmin)
admin.site.register(ImageModel, ImageModelAdmin)

admin.site.register(Phase01_instruction)
admin.site.register(Phase02_instruction)
admin.site.register(Phase03_instruction)
