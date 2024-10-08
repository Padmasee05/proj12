from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('admin/', views.admin_page, name='admin'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('signup/', views.signup_view, name='signup'),
    path('doctor_reg/', views.doctor_reg_view, name='doctor_reg'),
    path('patient_reg/', views.patient_reg_view, name='patient_reg'),
    path('patient_welcome/', views.patient_welcome_view, name='patient_welcome'),
    path('doctor_dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('doctor_availability/', views.doctor_availability, name='doctor_availability'),
    path('patient_appointments/', views.patient_appointments, name='patient_appointments'),
    path('get-doctors-by-specialty/', views.get_doctors_by_specialty,
         name='get_doctors_by_specialty'),
    path('get-availability-by-doctor-date/', views.get_availability_by_doctor_date,
         name='get_availability_by_doctor_date'),
    path('reschedule/', views.reschedule_appointment, name='reschedule_appointment'),
    path('cancel/', views.cancel_appointment, name='cancel_appointment'),

]

