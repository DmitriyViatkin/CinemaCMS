from django import forms
from users.models import  User

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model= User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'city', 'address', 'languages', 'phone_number',
            'gender', 'date_of_birth'
        ]