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
        form = AvailabilityForm(request.POST)
        if form.is_valid():
            dates = form.cleaned_data['dates'].splitlines()
            slots = form.cleaned_data['slots']

            # Get the logged-in doctor
            doctor = Doctor.objects.get(user=request.user)

            # Process each date and slot
            for date in dates:
                for slot in slots:
                    start_time, end_time = slot.split('-')
                    # Create a new availability entry
                    DoctorAvailability.objects.create(
                        doctor=doctor,
                        date=date,
                        slot_start=start_time,
                        slot_end=end_time
                    )

            return redirect('doctor_availability')  # Redirect after saving
    else:
        form = AvailabilityForm()

    return render(request, 'doctor_availability.html', {'form': form})


def patient_appointments(request):
    if request.method == 'POST':
        specialty = request.POST.get('specialty')
        doctor_name = request.POST.get('doctor_name')
        selected_date = request.POST.get('date')
        selected_time_slot = request.POST.get('time_slot')
        patient = request.user.patient  # Assuming user is logged in as patient

        Appointment.objects.create(
                doctor=doctor_name,
                patient=patient,
                date=selected_date,
                time=selected_time_slot,
                status='pending'
            )

        return JsonResponse({'message': 'Appointment booked successfully!'})

    return render(request, 'appointments.html')


def get_doctors_by_specialty(request):
    specialty = request.GET.get('specialty')
    doctors = Doctor.objects.filter(specialty=specialty)
    doctor_list = [{'name': f"{doctor.firstname} {doctor.lastname}"} for
                   doctor in doctors]
    return JsonResponse(doctor_list, safe=False)


def get_availability_by_doctor_date(request):
    doctor_name = request.GET.get('doctor_name')
    selected_date = request.GET.get('date')

    # Fetch the doctor
    try:
        doctor = Doctor.objects.get(
            user__email=doctor_name)  # Adjust based on how you identify doctors
    except Doctor.DoesNotExist:
        return JsonResponse({'error': 'Doctor not found'}, status=404)

    # Fetch availability slots based on doctor and date
    availability = DoctorAvailability.objects.filter(
        doctor=doctor,
        date=selected_date
    ).values_list('slot_start', 'slot_end')

    if not availability:
        return JsonResponse({'message': 'Doctor not available on this date'},
                            status=404)

    # Format slots as ranges
    slots = [f"{start_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')}" for
             start_time, end_time in availability]

    return JsonResponse(slots, safe=False)

