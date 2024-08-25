from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import User, Patient, Doctor, Appointment, DoctorAvailability
from django.core.exceptions import ValidationError
from .forms import PatientRegistrationForm, DoctorRegistrationForm, \
    AvailabilityForm, AppointmentForm
import datetime
from django.utils import timezone


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


def admin_page(request):
    return render(request, 'admin_page.html')


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
                email=form.cleaned_data['email'],
                # Accessing email from cleaned_data
                password=form.cleaned_data['password'],
            )
            # Create a new doctor profile
            Doctor.objects.create(
                user=user,
                title=form.cleaned_data['title'],
                firstname=form.cleaned_data['firstname'],
                lastname=form.cleaned_data['lastname'],
                dob=form.cleaned_data['dob'],
                specialty=form.cleaned_data['specialty'],
                phone_number=form.cleaned_data['phone_number']
            )
            return render(request, 'doctor_reg.html',
                          {'form': form, 'success': True})
        else:
            return render(request, 'doctor_reg.html',
                          {'form': form, 'success': False})
    else:
        form = DoctorRegistrationForm()

    return render(request, 'doctor_reg.html', {'form': form})


def patient_reg_view(request):
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            firstname = form.cleaned_data.get('firstname')
            lastname = form.cleaned_data.get('lastname')
            dob = form.cleaned_data.get('dob')
            disease_description = form.cleaned_data.get('disease_description')
            phone_number = form.cleaned_data.get('phone_number')
            title = form.cleaned_data.get('title')

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

            return render(request, 'patient_reg.html',
                          {'form': form, 'success': True})
        else:
            return render(request, 'patient_reg.html', {'form': form})
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
    user = request.user
    doctor = get_object_or_404(Doctor,
                                user=user)
    # Get the logged-in doctor's instance
    today = datetime.date.today()

    # Calculate total patients who have appointments from today onward
    total_patients = Appointment.objects.filter(
        doctor=doctor,
        date__gte=today
    ).values('patient').distinct().count()

    # Pending patients are those with a pending appointment status
    pending_patients = Appointment.objects.filter(
        status='pending',
        doctor=doctor,
        date__gte=today
        # To ensure only upcoming pending appointments are shown
    )

    # Today's appointments
    todays_appointments = Appointment.objects.filter(
        date=today,
        doctor=doctor
    )

    context = {
        'total_patients': total_patients,
        'pending_patients': pending_patients,
        'todays_appointments': todays_appointments,
    }
    return render(request, 'doctor_dashboard.html', context)


def user_logout(request):
    logout(request)
    return redirect('homepage')


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

        # Split the doctor's name to extract firstname and lastname
        first_name, last_name = doctor_name.split()

        # Fetch the Doctor instance
        try:
            doctor = Doctor.objects.get(firstname=first_name,
                                        lastname=last_name)
        except Doctor.DoesNotExist:
            return JsonResponse({'error': 'Doctor not found'}, status=404)

        # Create the appointment
        Appointment.objects.create(
            doctor=doctor,
            patient=patient,
            date=selected_date,
            time=selected_time_slot,
            status='pending'
        )

        messages.success(request, 'Appointment booked successfully!')
        return redirect('patient_appointments')

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

    # Fetch the doctor based on the name
    try:
        doctor = Doctor.objects.get(
            firstname__iexact=doctor_name.split()[0],
            lastname__iexact=doctor_name.split()[1]
        )
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


def reschedule_appointment(request):
    if request.method == 'POST':
        appointment_id = request.POST.get('appointment_id')
        new_date = request.POST.get('new_date')
        new_time_slot = request.POST.get('new_time_slot')

        try:
            appointment = Appointment.objects.get(id=appointment_id,
                                                  patient=request.user.patient)
            appointment.date = new_date
            appointment.time = new_time_slot
            appointment.save()
            messages.success(request, 'Appointment rescheduled successfully.')
        except Appointment.DoesNotExist:
            messages.error(request, 'Appointment not found.')

        # Redirect to patient_welcome page after processing POST request
        return redirect('reschedule_appointment')

        # Handle GET request to display the reschedule form
    patient = request.user.patient
    upcoming_appointments = Appointment.objects.filter(patient=patient,
                                                       date__gte=timezone.now().date())

    # Extract the doctor’s name for each appointment
    for appointment in upcoming_appointments:
        appointment.doctor_name = f"{appointment.doctor.firstname} {appointment.doctor.lastname}"

    return render(request, 'reschedule_appointment.html',
                  {'upcoming_appointments': upcoming_appointments})


@login_required
def cancel_appointment(request):
    user = request.user

    try:
        # Fetch the corresponding Patient instance
        patient = Patient.objects.get(user=user)
    except Patient.DoesNotExist:
        messages.error(request, 'Patient not found.')
        return redirect('patient_appointments')

    if request.method == 'POST':
        # Logic to handle the cancellation
        appointment_id = request.POST.get('appointment_id')

        try:
            appointment = Appointment.objects.get(id=appointment_id, patient=patient)
            appointment.delete()
            messages.success(request, 'Appointment cancelled successfully!')
        except Appointment.DoesNotExist:
            messages.error(request, 'Appointment not found.')

        return redirect('cancel_appointment')

    # Retrieve upcoming appointments for the patient
    upcoming_appointments = Appointment.objects.filter(
        patient=patient, date__gte=timezone.now()
    ).order_by('date')

    return render(request, 'cancel_appointment.html', {
        'upcoming_appointments': upcoming_appointments
    })