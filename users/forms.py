from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.db import transaction
from django.forms.utils import ValidationError

from users.models import Player, CustomUser, Contact, Feature
from django.contrib.admin.widgets import FilteredSelectMultiple


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('username', 'email')


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = UserChangeForm.Meta.fields


class PlayerSignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        """Validates an email input by checking it against the database of current users
    
        Checks the email addresses of current active users and determines if the given email is in use.

        Returns:
            a cleaned version of the given email address.

        Raises:
            forms.ValidationError: the given email is associated with another user already and cannot be used again
        """
        data = self.cleaned_data['email']
        if CustomUser.objects.filter(email=data).exists():
            raise forms.ValidationError("This email has already been used")
        return data

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_player = True
        user.save()
        player = Player.objects.create(user=user)
        player.score = 0
        player.level = 0
        player.save()
        return user


class PlayerChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email')


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ('name', 'email', 'subject', 'message')

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.TextInput(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control sm-textarea', 'style': 'height: 150px'}),
        }


class featureForm(forms.Form):
    def __init__(self, *args, **kwargs):
        bias_choice = {
            ('common', 'Yes, this is a basic feature'),
            ('uncommon', 'No'),
        }
        super(featureForm, self).__init__(*args, **kwargs)
        featureList = Feature.objects.values('feature')
        alist = []
        for i in featureList:
            for key, value in i.items():
                alist.append(value)
        for i, feature in enumerate(alist):
            self.fields['feature_%s' % i] = forms.ChoiceField(
                choices=bias_choice,
                label=feature,
                widget=forms.RadioSelect(),
            )

    def clean_answers(self):
        for name, value in self.cleaned_data.items():
            if name.startswith('feature_'):
                yield (self.fields[name].label, value)


class MyForm(forms.Form):
    feature = Feature.objects.all().order_by('feature')
    feature_list = list(feature.values_list('feature', flat=True))
    features = forms.ModelMultipleChoiceField(
        widget=FilteredSelectMultiple("Features", is_stacked=False),
        queryset=Feature.objects.all().order_by('feature'))

    class Media:
        css = {
            'all':['admin/css/widgets.css',
                   'css/uid-manage-form.css'],
        }
        # Adding this javascript is crucial
        js = ['/admin/jsi18n/']


'''
class RequesterSignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254) 
    occupation = forms.CharField(label="Your occupation(optional)", required=False)

    fields = ('username', 'email', 'occupation', 'password1,', 'password2')

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        
    def clean_email(self):
        """Validates an email input by checking it against the database of current users
    
        Checks the email addresses of current active users and determines if the given email is in use.

        Returns:
            a cleaned version of the given email address.

        Raises:
            forms.ValidationError: the given email is associated with another user already and cannot be used again
        """
        data = self.cleaned_data['email']
        if CustomUser.objects.filter(email=data).exists():
            raise forms.ValidationError("This email has already been used")
        return data
    
    @transaction.atomic
    def save(self):
        # Requester Saving
        user = super().save(commit=False)
        user.is_requester = True
        user.is_player = False
        user.save()
        requester = Requester.objects.create(user=user)
        requester.occupation = self.cleaned_data['occupation']
        requester.save()
        return user

class RequesterChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email')


class ZipfileForm(forms.ModelForm):
    class Meta:
        model = Zipfile
        fields = ('zip_upload', 'taboo_words_1', 'taboo_words_2', 'taboo_words_3',)

    @transaction.atomic
    def save(self):
        # ZipFile Saving
        zipfile = super().save(commit=False)
        taboo1 =  Label.objects.create(name=self.cleaned_data['taboo_words_1'])
        taboo1.isTaboo=True
        taboo1.save()
        taboo2 = Label.objects.create(name=self.cleaned_data['taboo_words_2'])
        taboo2.isTaboo=True
        taboo2.save()
        taboo3 = Label.objects.create(name=self.cleaned_data['taboo_words_3'])
        taboo3.isTaboo=True
        taboo3.save()

        zipfile.save()
        zipfile.tb.add(taboo1)
        zipfile.tb.add(taboo2)
        zipfile.tb.add(taboo3)
        # zipfile.save()

        return zipfile
'''
