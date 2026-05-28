from django.urls import path
from .views import ListadoAlumnosView, ImportarAlumnosView, EditarAlumnoView, ProfesorListView, ListaCargosView

urlpatterns = [
    path('alumnos/', ListadoAlumnosView.as_view(), name='listado_alumnos'),
    path('alumnos/importar_alumnos/', ImportarAlumnosView.as_view(), name='importar_alumnos'),
    path('alumnos/editar/<int:pk>/', EditarAlumnoView.as_view(), name='editar_alumno'),
    path('profesores/', ProfesorListView.as_view(), name='listado_profesor'),
    path('cargos/', ListaCargosView.as_view(), name='lista_cargos'),
]