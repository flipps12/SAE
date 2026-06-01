from django.urls import path
from .views import TablonComunicadosView, CrearComunicadoView, CargaFormsetAlumnosView, DetalleAsistenciasAlumnoView, ListaAsistenciasView, DetalleCalificacionesAlumnoView, ListadoAlumnosView, ListaCalificacionesView, ImportarAlumnosView, EditarAlumnoView, ProfesorListView, ListaCargosView

urlpatterns = [
    path('alumnos/', ListadoAlumnosView.as_view(), name='listado_alumnos'),
    path('alumnos/importar_alumnos/', ImportarAlumnosView.as_view(), name='importar_alumnos'),
    path('alumnos/editar/<int:pk>/', EditarAlumnoView.as_view(), name='editar_alumno'),
    path('profesores/', ProfesorListView.as_view(), name='listado_profesor'),
    path('cargos/', ListaCargosView.as_view(), name='lista_cargos'),
    path('calificaciones/', ListaCalificacionesView.as_view(), name='lista_calificaciones'),
    path('alumno/<int:pk>/calificaciones/', DetalleCalificacionesAlumnoView.as_view(), name='detalle_calificaciones_alumno'),
    path('asistencias/', ListaAsistenciasView.as_view(), name='lista_asistencias'),
    path('alumno/<int:pk>/asistencias/', DetalleAsistenciasAlumnoView.as_view(), name='detalle_asistencias_alumno'),

    
    path('carga/alumnos/', CargaFormsetAlumnosView.as_view(), name='carga_dinamica_alumnos'),

    path('comunicados/', TablonComunicadosView.as_view(), name='lista_comunicados'),
    path('comunicados/nuevo/', CrearComunicadoView.as_view(), name='carga_comunicados'),
]