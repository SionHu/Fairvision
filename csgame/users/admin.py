from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, Label, ImageModel

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm

#class ImageMoedlInline(admin.StackedInline):
#    model = ImageModel
#    extra = 1

class ImageModelAdmin(admin.ModelAdmin):
    # inlines = [ImageMoedlInline]
    def save_model(self, request, obj, form, change):
        obj.save()
 
        for afile in request.FILES.getlist('photos_multiple'):
            obj.create(img=afile)

admin.site.register(CustomUser, CustomUserAdmin)
# admin.site.register(Zipfile)
admin.site.register(Label)
admin.site.register(ImageModel, ImageModelAdmin)