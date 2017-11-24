from django import forms
import re
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist


class RegistrationForm(forms.Form):
    username = forms.CharField(label="Username", max_length=50)
    email = forms.EmailField(label="Email")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())
    password_confirm = forms.CharField(label="Confirm Password", widget=forms.PasswordInput())
    firstname = forms.CharField(label="First Name", max_length=30)
    lastname = forms.CharField(label="Last Name", max_length=20, required=False)
    profileurl = forms.URLField(label="Profile Picture URL", required=False)

    def password_validation(self):
        if 'password' in self.cleaned_data:
            password1 = self.cleaned_data['password']
            password2 = self.cleaned_data['password_confirm']
            if password1 == password2:
                return password2
        self._errors['password_confirm'] = ['Passwords must match.']
        raise forms.ValidationError("Passwords do not match.")

    def check_username(self):
        if 'username' in self.cleaned_data:
            username = self.cleaned_data['username']
            if not re.search(r'^\w+$', username):
                raise forms.ValidationError("Username can only contain alphanumeric characters and the underscore.")
                self._errors['username'] = ['Username can only contain alphanumeric characters and the underscore.']
            try:
                User.objects.get(username=username)
            except ObjectDoesNotExist:
                return username
            self._errors['username'] = ['Username is already taken.']
            raise forms.ValidationError('Username is already taken.')
        else:
            self._errors['username'] = ['Username key is not exist.']
            forms.ValidationError("Please key is not exist.")
        return self.cleaned_data


