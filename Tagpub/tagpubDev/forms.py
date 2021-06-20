from django import forms
# from django.contrib.auth.models import User
from tagpubDev.models import RegistrationApplication
from dal import autocomplete


class ApplicationRegistrationForm(forms.ModelForm):

    class Meta:
        model = RegistrationApplication
        fields = ('name', 'surname', 'email', 'applicationText')


class TagForm(forms.Form):
    wikiLabel = autocomplete.Select2ListChoiceField(
        widget=autocomplete.ListSelect2(url='tag-autocomplete'),
        label="Search Wikidata Entry"
    )


