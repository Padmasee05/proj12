from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator, RegexValidator
import re
from .models import User, Patient, Doctor, Appointment
from django.utils import timezone


class PatientRegistrationForm(forms.ModelForm):
    email = forms.EmailField(required=True, validators=[
        EmailValidator(message="Enter a valid email address.")])
    password = forms.CharField(widget=forms.PasswordInput(),
                               validators=[validate_password])
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = Patient
        fields = ['title', 'firstname', 'lastname', 'dob',
                  'disease_description', 'phone_number', 'email', 'password']

    dob = forms.DateField(
        widget=forms.TextInput(attrs={'id': 'id_dob'}),
        input_formats=['%Y-%m-%d'],
    )

    phone_number = forms.CharField(
        max_length=10,
        min_length=10,
        validators=[
            RegexValidator(
                r'^\d{10}$',
                'Enter a valid 10-digit phone number.'
            )
        ],
    )

    firstname = forms.CharField(
        validators=[
            RegexValidator(
                r'^[A-Za-z]+$',
                'First name should contain only letters.'
            )
        ],
    )

    lastname = forms.CharField(
        validators=[
            RegexValidator(
                r'^[A-Za-z]+$',
                'Last name should contain only letters.'
            )
        ],
    )

    disease_description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
    )

    def clean_disease_description(self):
        disease_description = self.cleaned_data.get('disease_description')

        # Check if the description is not empty or just whitespace
        if not disease_description.strip():
            raise ValidationError("Disease description cannot be empty.")

        # Check if the description is not just numbers
        if disease_description.isdigit():
            raise ValidationError(
                "Disease description cannot contain only numbers.")

        # Check for meaningful text (not just random symbols or letters)
        if not re.search(r'[A-Za-z]', disease_description):
            raise ValidationError("Disease description must contain letters.")

        if re.search(r'^[^A-Za-z0-9\s]+$', disease_description):
            raise ValidationError(
                "Disease description cannot contain only symbols.")

        # Check for random gibberish - basic check (you can customize it)
        if len(set(disease_description.lower())) < 5:
            raise ValidationError(
                "Please enter a meaningful description.")

        return disease_description

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                "Password must contain at least one uppercase letter.")
        if not re.search(r'[0-9]', password):
            raise ValidationError("Password must contain at least one digit.")
        if not re.search(r'[@$!%*?&]', password):
            raise ValidationError(
                "Password must contain at least one special character.")
        if len(password) < 8:
            raise ValidationError(
                "Password must be at least 8 characters long.")
        try:
            validate_password(password)
        except ValidationError as e:
            self.add_error('password', e)
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")

        # Check if email already exists
        if User.objects.filter(email=cleaned_data.get("email")).exists():
            self.add_error('email', "An account with this email already "
                                    "exists.")

        return cleaned_data


# forms.py

class DoctorRegistrationForm(forms.ModelForm):
    email = forms.EmailField(required=True)  # Ensure email is included
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    title = forms.ChoiceField(choices=Doctor.TITLE_CHOICES, required=True)
    specialty = forms.ChoiceField(choices=Doctor.speciality_choice,
                                  required=True)
    dob = forms.DateField(widget=forms.TextInput(attrs={'id': 'id_dob'}))
    phone_number = forms.CharField(required=True)

    class Meta:
        model = Doctor
        fields = ['title', 'firstname', 'lastname', 'dob', 'specialty',
                  'phone_number', 'email', 'password']  # Include 'email'

    def clean_firstname(self):
        firstname = self.cleaned_data.get('firstname')
        if not firstname.isalpha():
            raise forms.ValidationError(
                "First name should contain only letters.")
        return firstname

    def clean_lastname(self):
        lastname = self.cleaned_data.get('lastname')
        if not lastname.isalpha():
            raise forms.ValidationError(
                "Last name should contain only letters.")
        return lastname

    def clean_dob(self):
        dob = self.cleaned_data.get('dob')
        today = timezone.now().date()
        age = (today.year - dob.year) - int(
            (today.month, today.day) < (dob.month, dob.day))

        if age < 18:
            raise forms.ValidationError("You must be at least 18 years old.")
        if dob >= today:
            raise forms.ValidationError(
                "Date of birth must be a valid date in the past.")

        return dob

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not re.match(r'^\d{10}$', phone_number):
            raise forms.ValidationError(
                "Phone number must be a valid 10-digit number.")
        return phone_number

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise forms.ValidationError(
                "Password should be at least 8 characters long.")
        if not re.search(r'[A-Z]', password):
            raise forms.ValidationError(
                "Password should contain at least one uppercase letter.")
        if not re.search(r'[a-z]', password):
            raise forms.ValidationError(
                "Password should contain at least one lowercase letter.")
        if not re.search(r'[0-9]', password):
            raise forms.ValidationError(
                "Password should contain at least one digit.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise forms.ValidationError(
                "Password should contain at least one special character.")

        # Validate the password using Django's built-in validators
        try:
            validate_password(password)
        except ValidationError as e:
            self.add_error('password', e)
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

        # Check if email already exists
        if User.objects.filter(email=cleaned_data.get("email")).exists():
            raise forms.ValidationError("An account with this "
                                        "email already exists.")

        return cleaned_data


class AvailabilityForm(forms.Form):
    # Example predefined slots
    SLOTS = [
        ('09:00-10:00', '09:00 AM - 10:00 AM'),
        ('10:00-11:00', '10:00 AM - 11:00 AM'),
        ('11:00-12:00', '11:00 AM - 12:00 PM'),
        ('12:00-13:00', '12:00 PM - 01:00 PM'),
        ('13:00-14:00', '01:00 PM - 02:00 PM'),
        ('14:00-15:00', '02:00 PM - 03:00 PM'),
        ('15:00-16:00', '03:00 PM - 04:00 PM'),
        ('16:00-17:00', '04:00 PM - 05:00 PM'),
    ]

    dates = forms.CharField(widget=forms.Textarea(
        attrs={'rows': 5, 'placeholder': 'Enter dates (one per line)'}))
    slots = forms.MultipleChoiceField(choices=SLOTS,
                                      widget=forms.CheckboxSelectMultiple)


class AppointmentForm(forms.Form):
    specialty = forms.ChoiceField(choices=[])
    doctor = forms.ModelChoiceField(queryset=Doctor.objects.none())
    date = forms.DateField(widget=forms.SelectDateWidget)
    time_slot = forms.ChoiceField(choices=[])

    class Meta:
        fields = ['specialty', 'doctor', 'date', 'time_slot']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Fetch distinct specialties
        specialties = Doctor.objects.values_list('specialty',
                                                 flat=True).distinct()
        self.fields['specialty'].choices = [(specialty, specialty) for
                                            specialty in specialties]

        if 'specialty' in self.data:
            try:
                specialty = self.data.get('specialty')
                self.fields['doctor'].queryset = Doctor.objects.filter(
                    specialty=specialty)
            except (ValueError, TypeError):
                pass