from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
    PermissionsMixin, Group, Permission
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',  # Set a unique related name
        blank=True,
        help_text=(
            'The groups this user belongs to. A user will get all permissions granted to each of their groups.'),
        verbose_name=('groups'),
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_set',  # Set a unique related name
        blank=True,
        help_text=('Specific permissions for this user.'),
        verbose_name=('user permissions'),
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email


class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    TITLE_CHOICES = [
        ('Mr', 'Mr.'),
        ('Ms', 'Ms.'),
        ('Mrs', 'Mrs.'),
        ('Dr', 'Dr.'),
        ('Prof', 'Prof.'),
    ]
    title = models.CharField(max_length=30, choices=TITLE_CHOICES)
    firstname = models.CharField(max_length=30)
    lastname = models.CharField(max_length=30)
    dob = models.DateField()
    disease_description = models.TextField()
    phone_number = models.CharField(max_length=15)

    def __str__(self):
        return f'{self.firstname} {self.lastname}'


class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    TITLE_CHOICES = [
        ('Mr', 'Mr.'),
        ('Ms', 'Ms.'),
        ('Mrs', 'Mrs.'),
        ('Dr', 'Dr.'),
        ('Prof', 'Prof.'),
    ]
    title = models.CharField(max_length=30, choices=TITLE_CHOICES)
    firstname = models.CharField(max_length=30)
    lastname = models.CharField(max_length=30)
    dob = models.DateField()
    speciality_choice = [('general surgeon', 'General Surgeon'),
                         ('cardiologist', 'Cardiologist'),
                         ('dermatologist', 'Dermatologist'),
                         ('neurologist', 'Neurologist'),
                         ('orthopedician', 'Orthopedician'),
                         ('gynecologist', 'Gynecologist'), ]
    specialty = models.CharField(max_length=100, choices=speciality_choice)
    phone_number = models.CharField(max_length=15)

    def __str__(self):
        return f'{self.firstname} {self.lastname} ({self.specialty})'


class Appointment(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), (
    'confirmed', 'Confirmed'), ('completed', 'Completed')])

    def __str__(self):
        return (f"{self.patient.firstname} {self.patient.lastname} with Dr. "
                f"{self.doctor.firstname} {self.doctor.lastname} on {self.date} "
                f"at {self.time}")


class DoctorAvailability(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date = models.DateField()
    slot_start = models.TimeField(
        default="09:00")  # Set your default value here
    slot_end = models.TimeField(default="10:00")  # Set your default value here


def __str__(self):
    return f"{self.doctor} - {self.date} - {self.slot_start}-{self.slot_end}"


# models.py

from django.db import models


class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=30)
    firstname = models.CharField(max_length=30)
    lastname = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    position = models.CharField(max_length=50)  # E.g., 'Doctor', 'Nurse', etc.

    def __str__(self):
        return f'{self.firstname} {self.lastname}'


class Qualification(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    qualification_name = models.CharField(max_length=100)
    institution = models.CharField(max_length=100)
    year_of_completion = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.qualification_name} from {self.institution}'


class Schedule(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    date = models.DateField()
    shift_start = models.TimeField()
    shift_end = models.TimeField()

    def __str__(self):
        return f'{self.staff} on {self.date} from {self.shift_start} to {self.shift_end}'


class Salary(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    bonuses = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deductions = models.DecimalField(max_digits=10, decimal_places=2,
                                     default=0)

    @property
    def total_salary(self):
        return self.basic_salary + self.bonuses - self.deductions

    def __str__(self):
        return f'Salary record for {self.staff}'
