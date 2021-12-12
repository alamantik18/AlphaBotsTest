from django import forms
from .models import Profile

#Изменяем форму для ввдо даных в админке
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = (
            'external_id',
            'username',
            'name',
            'phoneNumber',
            'answers',
        )
        widgets = {
            'username': forms.TextInput,
            'name': forms.TextInput,
            'phoneNumber': forms.TextInput,
            'answers': forms.TextInput,
        }
