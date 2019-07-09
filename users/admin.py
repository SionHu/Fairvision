from csgame.storage_backends import mturk

from django.conf import settings
from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.sessions.models import Session
from django.core.files.storage import default_storage
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render
from django.template.defaultfilters import filesizeformat
from django.templatetags.static import static
from django.urls import reverse
from django.utils.html import format_html

from .fields import ListTextInput
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, ImageModel, Attribute, Phase, PhaseBreak, Phase01_instruction, Phase02_instruction, Phase03_instruction, TextInstruction, Answer, Question, HIT


from django import forms
from natsort import natsorted

from ast import literal_eval
import base64
import csv
import itertools
from more_itertools import partition
import operator
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
    img = forms.ImageField(label='Image', widget=forms.FileInput(attrs={'multiple': True}), help_text=(f'Images to upload to S3 ({filesizeformat(settings.DATA_UPLOAD_MAX_MEMORY_SIZE)} or less in total). We only allow JPG files.'), required=True)
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

try:
    from jsoneditor.forms import JSONEditor
    from django.contrib.postgres.forms import JSONField
    JSONField.widget = JSONEditor
except:
    JSONEditor = forms.Textarea

class PhaseForm(forms.ModelForm):
    class Meta:
        model = Phase
        fields = '__all__'
        widgets = {
            'get': JSONEditor,
            'post': JSONEditor
        }
    def save(self, *args, **kwargs):
        obj = self.instance
        obj.get = literal_eval(self.cleaned_data['get'])
        obj.post = literal_eval(self.cleaned_data['post'])
        return super().save(*args, **kwargs)

class PhaseAdmin(admin.ModelAdmin):
#    form = PhaseForm
    readonly_fields = ('phase',)
    fieldsets = (
        (None, {'fields': ('phase', 'get', 'post')}),
    )
    def has_add_permission(self, request):
        return False

class SessionForm(forms.ModelForm):
    decoded_data = forms.CharField(widget=JSONEditor)
    class Meta:
        model = Session
        fields = ('session_key', 'decoded_data', 'expire_date')
        exclude = ("session_data", )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        public, self.private = partition(lambda k: k[0].startswith('_'), self.instance.get_decoded().items())
        self.initial['decoded_data'] = dict(public) if self.instance else '{}'
        self.objects = self._meta.model.objects
    def save(self, *args, **kwargs):
        obj = self.instance
        data = literal_eval(self.cleaned_data['decoded_data'])
        data.update(self.private)
        obj.session_data = self.objects.encode(data)
        return super().save(*args, **kwargs)

class SessionAdmin(admin.ModelAdmin):
    form = SessionForm
    list_display = ('session_key', 'username', 'expire_date')
    readonly_fields = ('session_key', 'username')
    fieldsets = (
        (None, {'fields': ('session_key', 'username', 'decoded_data', 'expire_date')}),
    )
    def has_add_permission(self, request):
        return False
    def username(self, obj):
        id = obj.get_decoded().get('_auth_user_id')
        if id is None: return None
        user = CustomUser.objects.get(id=id)
        #return .username if id else None
        return format_html("<a href={}>{}</a>".format(
            reverse('admin:{}_{}_change'.format(user._meta.app_label, user._meta.model_name),
            args=(user.pk,)),
        user.username))

class HITApprovalForm(forms.Form):
    reason = forms.CharField(label='Reason for Acceptance', max_length=256, required=False, widget=forms.Textarea(attrs={'cols': 80, 'rows': 20}))
    bonus = forms.DecimalField(label='Worker Bonus', max_value=1, min_value=0, decimal_places=2, initial='0.00', widget=forms.NumberInput(attrs={'step': 0.01}))

    def clean(self):
        cleaned_data = super().clean()
        reason = cleaned_data.get("reason")
        bonus = cleaned_data.get("bonus")

        if bonus and not reason:
            raise forms.ValidationError(
                "If bonus is specified, than a reason is also required."
            )
        return cleaned_data

class HITRejectionForm(forms.Form):
    reason = forms.CharField(label='Reason for Rejection (required)', max_length=256, widget=forms.Textarea(attrs={'cols': 80, 'rows': 20, 'maxlength': 256}))

class HITStatusFilter(admin.SimpleListFilter):
    title = 'status'
    parameter_name = 'status'
    def lookups(self, request, model_admin):
        return [('*', 'All'), ('None', 'None'), ('Submitted', 'Submitted'), ('Approved', 'Approved'), ('Rejected', 'Rejected')]
    def queryset(self, request, queryset):
        val = self.value()
        if val == '*':
            return queryset
        if val == 'None':
            return queryset.filter(~Q(data__has_key='status') | Q(data__status=''))
        return queryset.filter(data__status=val)
    def value(self):
        value = super().value()
        return 'Submitted' if value is None else value
    def choices(self, changelist):
        yield from ({
            'selected': self.value() == str(lookup),
            'query_string': changelist.get_query_string({self.parameter_name: lookup}),
            'display': title,
        } for lookup, title in self.lookup_choices)

class HITWorkerFilter(admin.SimpleListFilter):
    title = 'Worker ID'
    parameter_name = 'workerID'
    def lookups(self, request, model_admin):
        return []
    def queryset(self, request, queryset):
        val = self.value()
        if val is None:
            return queryset
        return queryset.filter(data__workerID=val)

class HITAdmin(admin.ModelAdmin):
    list_display = ['assignment_id', 'status', 'questions', 'workerID']#('assignment_id', 'hitId', 'workerId', 'data')workerID
    readonly_fields = ('assignment_id', 'hitID', 'workerID')
    fieldsets = (
        (None, {'fields': ('assignment_id', 'data')}),
    )
    list_filter = (HITStatusFilter,)
    def has_add_permission(self, request):
        return False
    def questions(self, obj):
        return format_html('<br>'.join("<a href={}>{}</a>".format(
            reverse('admin:{}_{}_change'.format(img._meta.app_label, img._meta.model_name),
            args=(img.id,)),
        img.text) for img in obj.questions))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.registerAutoField('Feedback', 'RequesterFeedback')

    def changelist_view(self, request, extra_context=None):
        # Update assignment statuses of any new assignments
        try:
            self.assignments = {
                assignment['AssignmentId']: assignment
                for hit in mturk.list_hits()['HITs']
                for assignment in mturk.list_assignments_for_hit(HITId=hit['HITId']).get('Assignments', [])
            }
            for obj in HIT.objects.filter(Q(data__has_key='hitId') &~ Q(data__has_key='status')):
                obj.data['status'] = self.assignments.get(obj.assignment_id, {}).get('AssignmentStatus', '')
                obj.save()
        except Exception as e:
            self.message_user(request, f'Unable to retrieve assignment statuses. {e}', messages.ERROR)
        return super().changelist_view(request, extra_context=None)
    def status(self, obj):
        if '__' in obj.assignment_id:
            return None
        if 'hitId' not in obj.data:
            return None
        #try:
        #    assignmentStatus = mturk.get_assignment(AssignmentId=obj.assignment_id).get('Assignment', {}).get('AssignmentStatus', '')
        #    obj.data['status'] = assignmentStatus
        #    obj.save()
        #except Exception as e:
        #    return None
        assignmentStatus = self.assignments.get(obj.assignment_id, {}).get('AssignmentStatus', '')
        # Update assignment statuses of any old assignments
        if 'status' in obj.data:
            if assignmentStatus == '':
                assignmentStatus = obj.data['status']
            elif obj.data['status'] != assignmentStatus:
                obj.data['status'] = assignmentStatus
                obj.save()
        else:
            obj.data['status'] = assignmentStatus
            obj.save()
        if assignmentStatus is '':
            return None
        icon_url = static('admin/img/icon-%s.svg' % {'Rejected': 'no', 'Approved': 'yes', 'Submitted': 'unknown'}[assignmentStatus])
        return format_html('<img src="{}" alt="{}">', icon_url, assignmentStatus)
    status.short_description = 'Assignment Status'

    def registerAutoField(self, humanFieldName, fieldName):
        def field(obj):
            return self.assignments.get(obj.assignment_id, {}).get(fieldName, '')
        field.short_description = humanFieldName
        if not hasattr(self, fieldName):
            setattr(self, fieldName, field)
        self.list_display.append(fieldName)

    #self.list_display.remove(fieldName)

    def approve(self, request, queryset):
        for obj in queryset:
            try:
                mturk.approve_assignment(
                    AssignmentId=obj.assignment_id,
                    OverrideRejection=True
                )
            except Exception as e:
                self.message_user(request, f'Unable to approve the assignment {obj.assignment_id}. {e}', messages.ERROR)
    approve.short_description = 'Approve selected hits'
    def bonus(self, request, queryset):
        if request.POST.get('post'):
            form = HITApprovalForm(request.POST)
            if form.is_valid():
                for obj in queryset:
                    try:
                        #print('successful fake acceptance of ' + str(obj))
                        if form.cleaned_data['reason']:
                            mturk.approve_assignment(
                                AssignmentId=obj.assignment_id,
                                RequesterFeedback=form.cleaned_data['reason'],
                                OverrideRejection=True
                            )
                        else:
                            mturk.approve_assignment(
                                AssignmentId=obj.assignment_id,
                                OverrideRejection=True
                            )
                        obj.data['__cached_status'] = 'Approved'
                        obj.save()
                        if form.cleaned_data['bonus']:
                            #print('successful fake bonus of '+str(form.cleaned_data['bonus']))
                            mturk.send_bonus(
                                WorkerId=obj.workerID,
                                BonusAmount=str(form.cleaned_data['bonus']),
                                AssignmentId=obj.assignment_id,
                                Reason=form.cleaned_data['reason'],
                                UniqueRequestToken=obj.assignment_id
                            )
                    except Exception as e:
                        self.message_user(request, f'Unable to approve the assignment {obj.assignment_id}. {e}', messages.ERROR)
                return None
        else:
            form = HITApprovalForm()
        return render(request, 'admin/users/hit/hit_form.html', {
            'items': queryset.order_by('pk'),
            'form': form,
            'title': 'Approve selected hits',
            'action': 'bonus',
            'button': 'Approve',
        })
    bonus.short_description = 'Approve selected hits and send bonus'
    def reject(self, request, queryset):
        if request.POST.get('post'):
            form = HITRejectionForm(request.POST)
            if form.is_valid():
                for obj in queryset:
                    try:
                        #print('successful fake rejection of ' + str(obj))
                        mturk.reject_assignment(
                            AssignmentId=obj.assignment_id,
                            RequesterFeedback=form.cleaned_data['reason']
                        )
                        obj.data['__cached_status'] = 'Rejected'
                        obj.save()
                    except Exception as e:
                        self.message_user(request, f'Unable to reject the assignment {obj.assignment_id}. {e}', messages.ERROR)
                return None
        else:
            form = HITRejectionForm()
        return render(request, 'admin/users/hit/hit_form.html', {
            'items': queryset.order_by('pk'),
            'form': form,
            'title': 'Reject selected hits',
            'action': 'reject',
            'button': 'Reject',
        })
    reject.short_description = 'Reject selected hits'
    actions=[approve, bonus, reject]

class AnswerAdmin(admin.ModelAdmin):
    actions = [export_csv('phase1-answers.csv', ['id','text','isFinal','question','assignmentID'])]
    list_filter = ('isFinal',)

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0

class QuestionAdmin(admin.ModelAdmin):
    actions = [export_csv('phase1-questions.csv', ['id','text','isFinal','skipCount','assignmentID'])]
    inlines = [
        AnswerInline,
    ]

    readonly_fields = ('image_id',)
    exclude = ('imageID',)
    def image_id(self, obj):
        id = obj.imageID
        imgs = ImageModel.objects.filter(img__in=id)
        return format_html('<br>'.join("<a href={}>{}</a>".format(
            reverse('admin:{}_{}_change'.format(img._meta.app_label, img._meta.model_name),
            args=(img.pk,)),
        img.img) for img in imgs))
    image_id.short_description = 'Image ID'
    list_filter = ('isFinal', 'assignmentID')


admin.site.register(CustomUser, CustomUserAdmin)
# admin.site.register(Zipfile)
admin.site.register(PhaseBreak)
admin.site.register(Phase, PhaseAdmin)

admin.site.register(Attribute, AttributeAdmin)
admin.site.register(ImageModel, ImageModelAdmin)

admin.site.register(Phase01_instruction)
admin.site.register(Phase02_instruction)
admin.site.register(Phase03_instruction)
admin.site.register(TextInstruction)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(Session, SessionAdmin)
admin.site.register(HIT, HITAdmin)
