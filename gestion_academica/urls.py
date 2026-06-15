from django.urls import path
# Importamos directamente los archivos del paquete views
from .views import alumnos, asistencias, calificaciones, cargos, comunicados, profesores, planilla_docente, infraestructura

# app_name = 'gestion_academica'

urlpatterns = [
    # --- DOMINIO: ALUMNOS ---
    path('alumnos/', alumnos.ListadoAlumnosView.as_view(), name='listado_alumnos'),
    path('alumnos/importar_alumnos/', alumnos.ImportarAlumnosView.as_view(), name='importar_alumnos'),
    path('alumnos/editar/<int:pk>/', alumnos.EditarAlumnoView.as_view(), name='editar_alumno'),
    path('carga/alumnos/', alumnos.CargaFormsetAlumnosView.as_view(), name='carga_dinamica_alumnos'),

    # --- DOMINIO: PROFESORES Y CARGOS ---
    path('profesores/', profesores.ProfesorListView.as_view(), name='listado_profesor'),
    path('profesores/nuevo/', profesores.AltaProfesorView.as_view(), name='alta_profesor'),
    path('cargos/', cargos.ListaCargosView.as_view(), name='lista_cargos'),
    path('cargos/nuevo/', cargos.AltaPersonalCargoView.as_view(), name='alta_cargos'),

    # --- DOMINIO: CALIFICACIONES ---
    path('calificaciones/', calificaciones.ListaCalificacionesView.as_view(), name='lista_calificaciones'),
    path('alumno/<int:pk>/calificaciones/', calificaciones.DetalleCalificacionesAlumnoView.as_view(), name='detalle_calificaciones_alumno'),
    path('planilla-docente/', planilla_docente.PlanillaCargaNotasView.as_view(), name='planilla_docente'),

    # --- DOMINIO: ASISTENCIAS ---
    path('asistencias/', asistencias.ListaAsistenciasView.as_view(), name='lista_asistencias'),
    path('alumno/<int:pk>/asistencias/', asistencias.DetalleAsistenciasAlumnoView.as_view(), name='detalle_asistencias_alumno'),

    # --- DOMINIO: COMUNICADOS ---
    path('comunicados/', comunicados.TablonComunicadosView.as_view(), name='lista_comunicados'),
    path('comunicados/nuevo/', comunicados.CrearComunicadoView.as_view(), name='carga_comunicados'),
    
    # --- DOMINIO: INFRAESTRUCTURA ---
    path('infraestructura/cursos/', infraestructura.GestionCursosView.as_view(), name='gestion_cursos'),
    path('infraestructura/turnos/', infraestructura.GestionTurnosView.as_view(), name='gestion_turnos'),
    path('infraestructura/especialidades/', infraestructura.GestionEspecialidadesView.as_view(), name='gestion_especialidades'),
    path('infraestructura/aulas/', infraestructura.GestionAulasView.as_view(), name='gestion_aulas'),
]