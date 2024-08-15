from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('doctor_reg/', views.doctor_reg_view, name='doctor_reg'),
    path('patient_reg/', views.patient_reg_view, name='patient_reg'),
    path('patient_welcome/', views.patient_welcome_view, name='patient_welcome'),
    path('doctor_dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('doctor_availability/', views.doctor_availability, name='doctor_availability'),

]

