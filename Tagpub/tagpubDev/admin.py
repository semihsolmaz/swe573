from django.contrib import admin
from .models import UserProfileInfo, RegistrationApplication

# Register your models here.
admin.site.register(UserProfileInfo)
admin.site.register(RegistrationApplication)
