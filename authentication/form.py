from django import forms
from users.models import  Profile

class LoginForm (forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label="Password",
                               widget= forms.PasswordInput)
    class Meta:
        model = Profile
        fields = ['username','nickname','email']

        def clean_password2(self):
            cd = self.cleaned_data
            if cd['password']!=cd['password2']:
                raise forms.ValidationError("Passwords don`t match.")
            return cd['password2']