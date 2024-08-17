from django import forms
from .models import User, Patient, Doctor, Appointment


class PatientRegistrationForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = Patient
        fields = ['title', 'firstname', 'lastname', 'dob',
                  'disease_description', 'phone_number', 'email', 'password']

    dob = forms.DateField(widget=forms.TextInput(attrs={'id': 'id_dob'}))

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
        fields = ['title', 'firstname', 'lastname', 'dob', 'specialty',
                  'phone_number', 'email', 'password']  # Include 'email'

    title = forms.ChoiceField(choices=Doctor.TITLE_CHOICES, required=True)
    specialty = forms.ChoiceField(choices=Doctor.speciality_choice,
                                  required=True)
    dob = forms.DateField(widget=forms.TextInput(attrs={'id': 'id_dob'}))

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
        ('09:00', '09:00 AM'),
        ('10:00', '10:00 AM'),
        ('11:00', '11:00 AM'),
        ('12:00', '12:00 PM'),
        ('13:00', '01:00 PM'),
        ('14:00', '02:00 PM'),
        ('15:00', '03:00 PM'),
        ('16:00', '04:00 PM'),
        ('17:00', '05:00 PM'),
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