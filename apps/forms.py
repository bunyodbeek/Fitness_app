from apps.models import UserProfile, UserProfile
from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.utils.translation import gettext_lazy as _


class UserProfileForm(UserChangeForm):
    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'avatar', 'birth_date', 'language']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _("Ism")
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _("Familiya")
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'birth_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'language': forms.Select(attrs={
                'class': 'form-control'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'password' in self.fields:
            del self.fields['password']

        for field_name in self.fields:
            if field_name not in ['username', 'email']:
                self.fields[field_name].required = False
