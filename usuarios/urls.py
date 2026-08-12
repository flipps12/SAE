from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),

    path('dashboard/staff/', views.DashboardStaffView.as_view(), name='dashboard_staff'),
    path('dashboard/profesor/', views.DashboardProfesorView.as_view(), name='dashboard_profesor'),
    path('dashboard/preceptor/', views.DashboardPreceptorView.as_view(), name='dashboard_preceptor'),
    path('dashboard/pernodoc/', views.DashboardPernodocView.as_view(), name='dashboard_pernodoc'),
    path('dashboard/jerarquicos/', views.DashboardJerarquicosView.as_view(), name='dashboard_jerarquicos'),
    path('dashboard/alumno/', views.DashboardAlumnoView.as_view(), name='dashboard_alumno'),
    path('dashboard/cargos/', views.DashboardCargosView.as_view(), name='dashboard_cargos'),
    
    path('perfil/', views.PerfilView.as_view(), name='perfil'),
]