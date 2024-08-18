from django.contrib import admin
from django import forms
from .models import User, Appointment, Patient, Doctor

admin.site.register(Appointment)



class PatientAdminForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = Patient
        fields = ['title', 'firstname', 'lastname', 'dob', 'disease_description', 'phone_number', 'email', 'password']

    def save(self, commit=True):
        user = User.objects.create_user(
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password']
        )
        self.instance.user = user
        return super().save(commit=commit)


class DoctorAdminForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = Doctor
        fields = ['title', 'firstname', 'lastname', 'dob', 'specialty', 'phone_number', 'email', 'password']

    def save(self, commit=True):
        user = User.objects.create_user(
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password']
        )
        self.instance.user = user
        return super().save(commit=commit)


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    form = PatientAdminForm
    list_display = (
    'title', 'firstname', 'lastname', 'dob', 'disease_description',
    'phone_number', 'user')
    ordering = ('lastname', 'firstname')
    search_fields = ('firstname', 'lastname', 'disease_description')
    list_filter = ('title',)


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    form = DoctorAdminForm
    list_display = (
    'title', 'firstname', 'lastname', 'dob', 'specialty', 'phone_number',
    'user')
    ordering = ('lastname', 'firstname')
    search_fields = ('firstname', 'lastname', 'specialty')
    list_filter = ('specialty',)


