from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.db import transaction
from django.forms.utils import ValidationError

from users.models import Player, Requester, CustomUser

class PlayerSignUpForm(UserCreationForm):
    
    email = forms.EmailField(max_length=254)
    
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'password')

    
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
        return user
 
class PlayerChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email')

class RequesterSignUpForm(UserCreationForm):
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
        user = super().save(commit=False)
        user.is_requester = True
        if commit:
            user.save()
        return user