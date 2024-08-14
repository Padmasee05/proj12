from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from .models import User, Patient, Doctor
from django.core.exceptions import ValidationError
from .forms import PatientRegistrationForm, DoctorRegistrationForm


def homepage(request):
    if request.method == 'POST':
        if 'login' in request.POST:
            email = request.POST.get('email')
            password = request.POST.get('password')

            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                if hasattr(user, 'patient'):
                    return redirect('patient_welcome')
                elif hasattr(user, 'doctor'):
                    return redirect('doctor_dashboard')
                else:
                    return redirect('homepage')  # Adjust as needed
            else:
                messages.error(request, 'Invalid email or password.')
    return render(request, 'homepage.html')


# def login_view(request):
#     if request.method == 'POST':
#         email = request.POST.get('email')
#         password = request.POST.get('password')
#
#         print(f"Email: {email}, Password: {password}")  # Debugging
#
#         user = authenticate(request, email=email, password=password)
#
#         if user is not None:
#             print("User authenticated successfully")
#             login(request, user)
#             if hasattr(user, 'patient'):
#                 return redirect('patient_welcome')
#             else:
#                 return redirect('homepage')  # Adjust as necessary
#         else:
#             print("Authentication failed")
#             messages.error(request, 'Invalid email or password.')
#
#     return render(request, 'homepage.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            if hasattr(user, 'doctor'):
                return redirect('doctor_dashboard')
            elif hasattr(user, 'patient'):
                return redirect('patient_welcome')
            else:
                return redirect('homepage')  # For admins or any other case
        else:
            messages.error(request, 'Invalid email or password.')

    return render(request, 'homepage.html')


def signup_view(request):
    if request.method == 'POST':
        role = request.POST['role']
        if role == 'patient':
            return redirect('patient_reg')
        elif role == 'doctor':
            return redirect('doctor_reg')
    return render(request, 'signup.html')


def doctor_reg_view(request):
    if request.method == 'POST':
        form = DoctorRegistrationForm(request.POST)
        if form.is_valid():
            # Create a new user
            user = User.objects.create_user(
                # username=form.cleaned_data['email'],  # Using email as username
                email=form.cleaned_data['email'],
                # Accessing email from cleaned_data
                password=form.cleaned_data['password'],
            )
            # Create a new doctor profile
            doctor = Doctor.objects.create(
                user=user,
                title=form.cleaned_data['title'],
                firstname=form.cleaned_data['firstname'],
                lastname=form.cleaned_data['lastname'],
                dob=form.cleaned_data['dob'],
                specialty=form.cleaned_data['specialty'],
                phone_number=form.cleaned_data['phone_number']
            )
            # Redirect after successful signup
            return redirect('homepage')  # or another URL
    else:
        form = DoctorRegistrationForm()
    return render(request, 'doctor_reg.html', {'form': form})


def patient_reg_view(request):
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            firstname = request.POST.get('firstname')
            lastname = request.POST.get('lastname')
            dob = request.POST.get('dob')
            disease_description = request.POST.get('disease_description')
            phone_number = request.POST.get('phone_number')
            title = request.POST.get('title')

            user = User.objects.create_user(
                email=email,
                password=password,
                is_active=True
            )

            Patient.objects.create(
                user=user,
                title=title,
                firstname=firstname,
                lastname=lastname,
                dob=dob,
                disease_description=disease_description,
                phone_number=phone_number
            )

            messages.success(request, 'Signup successful!')
            return redirect('homepage')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PatientRegistrationForm()

    return render(request, 'patient_reg.html', {'form': form})


def patient_welcome_view(request):
    return render(request, 'patient_welcome.html')


def doctor_dashboard(request):
    return render(request, 'doctor_dashboard.html')
