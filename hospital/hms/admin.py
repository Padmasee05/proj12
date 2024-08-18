from django.contrib import admin
from django import forms
from .models import (User, Appointment, Patient, Doctor,
                     Staff, Qualification, Schedule, Salary)

admin.site.register(Appointment)


class PatientAdminForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = Patient
        fields = ['title', 'firstname', 'lastname', 'dob',
                  'disease_description', 'phone_number', 'email', 'password']

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
        fields = ['title', 'firstname', 'lastname', 'dob', 'specialty',
                  'phone_number', 'email', 'password']

    def save(self, commit=True):
        user = User.objects.create_user(
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password']
        )
        self.instance.user = user
        return super().save(commit=commit)


class QualificationInline(admin.TabularInline):
    model = Qualification
    extra = 1


class ScheduleInline(admin.TabularInline):
    model = Schedule
    extra = 1


class SalaryInline(admin.StackedInline):
    model = Salary
    extra = 1


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


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('firstname', 'lastname', 'title', 'email', 'position')
    search_fields = ('firstname', 'lastname', 'email')
    inlines = [QualificationInline, ScheduleInline, SalaryInline]


@admin.register(Qualification)
class QualificationAdmin(admin.ModelAdmin):
    list_display = (
    'qualification_name', 'institution', 'year_of_completion', 'staff')
    search_fields = ('qualification_name', 'institution')


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('staff', 'date', 'shift_start', 'shift_end')
    search_fields = ('staff__firstname', 'staff__lastname', 'date')


@admin.register(Salary)
class SalaryAdmin(admin.ModelAdmin):
    list_display = (
    'staff', 'basic_salary', 'bonuses', 'deductions', 'total_salary')
    search_fields = ('staff__firstname', 'staff__lastname')
