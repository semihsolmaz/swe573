from django import forms
from django.contrib.auth.models import User
from tagpubDev.models import RegistrationApplication


class ApplicationRegistrationForm(forms.ModelForm):
    # password = forms.CharField(widget=forms.PasswordInput())
    # name = forms.CharField(max_length=64)
    # surname = forms.CharField(max_length=64)
    # email = forms.EmailField()
    # applicationText = forms.Textarea()

    class Meta():
        model = RegistrationApplication
        fields = ('name', 'surname', 'email', 'applicationText')
