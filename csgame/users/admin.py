from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.core.files.storage import default_storage
from django.db import transaction

from .fields import ListTextInput
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, Label, ImageModel, Attribute, RoundsNum, listArray, PhaseBreak, Phase01_instruction, Phase02_instruction, Phase03_instruction, NotSameVote


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

class ImageModelForm(forms.ModelForm):
    img = forms.ImageField(label='Image', widget=forms.FileInput(attrs={'multiple': True}), help_text=('Images to upload to S3 (2.5 MB or less)'), required=True)
    set = forms.CharField(required=True)
    object = forms.CharField(required=True)
    
    class Meta:
        Model = ImageModel
        fields = ('img', 'label', 'dataset', 'obj')

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
            self.fields['label'].widget = forms.HiddenInput()

            #calculate the options for the folder
            setChoices = []
            objChoices = []
            for dataset in default_storage.listdir('')[0]:
                if dataset is not 'unknown':
                    setChoices.append(dataset)
                    objChoices.extend(object for object in default_storage.listdir(dataset)[0] if object is not 'unknown')
            self.fields['set'].widget=ListTextInput(natsorted(setChoices), 'set')
            self.fields['object'].widget=ListTextInput(sort_uniq(objChoices), 'object')
            self.url = None
        
    def save(self, *args, **kwargs):
        if self.fields['set'].required:
            # multiple file upload
            # NB: does not respect 'commit' kwarg
            with transaction.atomic(), default_storage.upload_lock(self.cleaned_data['set'], self.cleaned_data['object']):
                file_list = natsorted(self.files.getlist('img'.format(self.prefix)), key=lambda file: file.name)
                self.instance.img = file_list[0]
                self.instance.dataset = self.cleaned_data['set']
                self.instance.obj = self.cleaned_data['object']
                output = super().save(*args, **kwargs)

                # save the rest of the images to the instances
                for index, file in enumerate(file_list[1:]):
                    print("I got file: ", file)
                    ImageModel.objects.create(
                        img=file,
                        dataset=self.cleaned_data['set'],
                        obj=self.cleaned_data['object'],
                    )
            return output
        else:
            return super().save(*args, **kwargs)


class ImageModelAdmin(admin.ModelAdmin):
    form = ImageModelForm
    fields = ('img', 'label', 'set', 'object')
    list_display = ('img', 'allLabel', 'showdataset')
    # filter_horizontal = ('label',)
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

class LabelAdmin(admin.ModelAdmin):
    list_filter=('isTaboo', 'name')
    actions = [export_csv('phase1-labels.csv', ['name'])]

    
admin.site.register(CustomUser, CustomUserAdmin)
# admin.site.register(Zipfile)
admin.site.register(Label, LabelAdmin)
admin.site.register(PhaseBreak)
admin.site.register(RoundsNum)

admin.site.register(listArray)
admin.site.register(Attribute, AttributeAdmin)
admin.site.register(NotSameVote)
admin.site.register(ImageModel, ImageModelAdmin)

admin.site.register(Phase01_instruction)
admin.site.register(Phase02_instruction)
admin.site.register(Phase03_instruction)
