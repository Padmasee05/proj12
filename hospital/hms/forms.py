from django import forms
from .models import User, Patient, Doctor


class PatientRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

        # Check if email already exists
        if User.objects.filter(email=cleaned_data.get("email")).exists():
            raise forms.ValidationError(
                "An account with this email already exists.")

        return cleaned_data


# forms.py


class DoctorRegistrationForm(forms.ModelForm):
    email = forms.EmailField(required=True)  # Ensure email is included
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Doctor
        fields = ['title', 'firstname', 'lastname', 'dob', 'specialty', 'phone_number', 'email']  # Include 'email'

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")