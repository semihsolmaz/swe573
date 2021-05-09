from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
# Create your models here.


class RegistrationApplication(models.Model):
    applicationStatuses = (
        ('1', 'New'),
        ('2', 'Approved'),
        ('3', 'Rejected')
    )

    name = models.CharField(max_length=64)
    surname = models.CharField(max_length=64)
    email = models.EmailField()
    applicationText = models.TextField(max_length=512)
    applicationDate = models.DateTimeField(default=timezone.now)
    applicationStatus = models.CharField(max_length=20, choices=applicationStatuses, default='1')


class UserProfileInfo(models.Model):

    # Create relationship (don't inherit from User!)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Add any additional attributes you want
    adminStatus = models.BooleanField(default=False)
    # pip install pillow to use this!
    # Optional: pip install pillow --global-option="build_ext" --global-option="--disable-jpeg"
    # profile_pic = models.ImageField(upload_to='basic_app/profile_pics',blank=True)
    registrationApplication = models.ForeignKey(RegistrationApplication, on_delete=models.CASCADE)

    def __str__(self):
        # Built-in attribute of django.contrib.auth.models.User !
        return self.user.username



