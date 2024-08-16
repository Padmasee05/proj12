from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login
from .models import User, Patient, Doctor, Appointment, DoctorAvailability
from django.core.exceptions import ValidationError
from .forms import PatientRegistrationForm, DoctorRegistrationForm, \
    AvailabilityForm, AppointmentForm
import datetime


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
    user = request.user
    patient = get_object_or_404(Patient,
                                user=user)  # Fetch the Patient instance

    current_appointments = Appointment.objects.filter(patient=patient,
                                                      date__exact=datetime.date.today())
    past_appointments = Appointment.objects.filter(patient=patient,
                                                   date__lt=datetime.date.today())
    upcoming_appointments = Appointment.objects.filter(patient=patient,
                                                       date__gt=datetime.date.today())

    context = {
        'patient_name': patient.firstname,  # Customize as needed
        'current_appointments': current_appointments,
        'past_appointments': past_appointments,
        'upcoming_appointments': upcoming_appointments,
    }
    return render(request, 'patient_welcome.html', context)


def doctor_dashboard(request):
    # Calculate total patients
    total_patients = Patient.objects.count()

    # Assuming that "pending patients" are those who have a pending appointment
    pending_patients = Appointment.objects.filter(status='pending',
                                                  doctor=request.user.doctor)

    todays_appointments = Appointment.objects.filter(
        date=datetime.date.today(), doctor=request.user.doctor)

    context = {
        'total_patients': total_patients,
        'pending_patients': pending_patients,
        'todays_appointments': todays_appointments,
    }
    return render(request, 'doctor_dashboard.html', context)


def doctor_availability(request):
    if request.method == 'POST':
        dates = request.POST.getlist('dates')
        slots = request.POST.getlist('slots')

        # Handle saving the availability in your model
        for date in dates:
            for slot in slots:
                DoctorAvailability.objects.create(
                    doctor=request.user.doctor,
                    date=date,
                    slot=slot
                )

        # Show a success message
        messages.success(request, 'Scheduled successfully!')
        return redirect('doctor_availability')

    return render(request, 'doctor_availability.html')


def patient_appointments(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            doctor = form.cleaned_data['doctor']
            date = form.cleaned_data['date']
            time_slot = form.cleaned_data['time_slot']
            patient = request.user.patient  # Assuming user is logged in as patient

            Appointment.objects.create(
                doctor=doctor,
                patient=patient,
                date=date,
                time=time_slot,
                status='pending'
            )

            return redirect(
                'patient_appointments')  # Redirect to appointments list page
    else:
        form = AppointmentForm()

    return render(request, 'appointments.html', {'form': form})


def load_doctors(request):
    specialty = request.GET.get('specialty')
    doctors = Doctor.objects.filter(specialty=specialty).all()
    return JsonResponse(list(doctors.values('id', 'firstname', 'lastname')),
                        safe=False)


def load_time_slots(request):
    doctor_id = request.GET.get('doctor')
    date = request.GET.get('date')
    availability = DoctorAvailability.objects.filter(doctor_id=doctor_id,
                                                     date=date).all()
    return JsonResponse(list(availability.values('id', 'slot')), safe=False)



