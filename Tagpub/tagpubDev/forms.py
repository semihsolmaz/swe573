from django import forms
# from django.contrib.auth.models import User
from tagpubDev.models import RegistrationApplication, Tag, Author
from dal import autocomplete
from tagpubDev.wikiManager import getLabelSuggestion


class ApplicationRegistrationForm(forms.ModelForm):

    class Meta:
        model = RegistrationApplication
        fields = ('name', 'surname', 'email', 'applicationText')


class TagForm(forms.Form):
    wikiLabel = autocomplete.Select2ListChoiceField(
        widget=autocomplete.ListSelect2(url='tag-autocomplete')
    )

