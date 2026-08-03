from django.urls import path
from .views import ListadoAlumnosView, ImportarAlumnosView, EditarAlumnoView, ProfesorListView, ListaCargosView, ImportarProfesoresView, VerAlumnoView, EditarProfesorView, DetalleProfesorView, ListaCalificacionesView, DetalleCalificacionesAlumnoView, EditarPersonalView, DetallePersonalCargoView, EditarCalificacionesView, CrearAlumnoView, CrearProfesorView, GestionTipoCargoView, GestionEspecialidadView, GestionCursoView, GestionMateriaView, GestionTurnoView, GestionAulaView, GestionBurbujaView, GestionCicloLectivoView, MisDictadosProfesorView, DictadoAlumnosView, ProfesorEditarCalificacionesView, GestionBoletinesView, TablonComunicadosView, CrearComunicadoView, PlanillaAsistenciaPreceptorView, ListaAsistenciasView, DetalleAsistenciasAlumnoView, PlanillaCargaNotasView, CargaFormsetAlumnosView, AltaPersonalCargoView

urlpatterns = [
    path('alumnos/', ListadoAlumnosView.as_view(), name='listado_alumnos'),
    path('alumnos/nuevo/', CrearAlumnoView.as_view(), name='crear_alumno'),
    path('alumnos/importar_alumnos/', ImportarAlumnosView.as_view(), name='importar_alumnos'),
    path('alumnos/editar/<int:pk>/', EditarAlumnoView.as_view(), name='editar_alumno'),
    path('alumno/ver/<int:pk>/', VerAlumnoView.as_view(), name='ver_alumno'),


    path('profesores/', ProfesorListView.as_view(), name='listado_profesor'),
    path('profesores/nuevo/',CrearProfesorView.as_view(),name='crear_profesor'),

    path('profesores/importar/', ImportarProfesoresView.as_view(), name='importar_profesores'),
    path('profesores/editar/<int:pk>/', EditarProfesorView.as_view(), name='editar_profesor'),
    path('profesor/<int:pk>/', DetalleProfesorView.as_view(), name='ver_profesor'),


    
    path('cargos/', ListaCargosView.as_view(), name='lista_cargos'),
    path('cargos/editar/<int:pk>/', EditarPersonalView.as_view(), name='editar_personal'),
    path('personal/detalle/<int:pk>/', DetallePersonalCargoView.as_view(), name='detalle_personal'),
    path('cargos/nuevo/', AltaPersonalCargoView.as_view(), name='alta_cargos'),


    path('calificaciones/', ListaCalificacionesView.as_view(), name='lista_calificaciones'),
    path('alumno/<int:pk>/calificaciones/', DetalleCalificacionesAlumnoView.as_view(), name='detalle_calificaciones_alumno'),
    path('calificaciones/editar/<int:dictado_id>/<int:alumno_id>/', EditarCalificacionesView.as_view(), name='editar_calificaciones'),
    path("boletines/", GestionBoletinesView.as_view(), name="gestion_boletines"),
    path("planilla-docente/", PlanillaCargaNotasView.as_view(), name="planilla_docente"),

    # --- DOMINIO: ASISTENCIAS ---
    path('asistencias/', ListaAsistenciasView.as_view(), name='lista_asistencias'),
    path('alumno/<int:pk>/asistencias/', DetalleAsistenciasAlumnoView.as_view(), name='detalle_asistencias_alumno'),
    path('planilla-preceptor/', PlanillaAsistenciaPreceptorView.as_view(), name='planilla_preceptor'),

    # --- DOMINIO: COMUNICADOS ---
    path('comunicados/', TablonComunicadosView.as_view(), name='lista_comunicados'),
    path('comunicados/nuevo/', CrearComunicadoView.as_view(), name='carga_comunicados'),

    path('carga/alumnos/', CargaFormsetAlumnosView.as_view(), name='carga_dinamica_alumnos'),

    path("tipos-cargo/", GestionTipoCargoView.as_view(), name="gestion_tipo_cargo",),
    path("especialidades/", GestionEspecialidadView.as_view(), name="gestion_especialidad",),
    path("cursos/", GestionCursoView.as_view(), name="gestion_curso",),
    path("materias/", GestionMateriaView.as_view(), name="gestion_materia"),
    path("turnos/", GestionTurnoView.as_view(), name="gestion_turno"),
    path("aulas/", GestionAulaView.as_view(), name="gestion_aula"),
    path("burbujas/", GestionBurbujaView.as_view(), name="gestion_burbuja"),
    path("ciclos-lectivos/", GestionCicloLectivoView.as_view(), name="gestion_ciclo_lectivo"),


    path("profesor/dictados/", MisDictadosProfesorView.as_view(), name="mis_dictados"),
    path("profesor/dictados/<int:pk>/", DictadoAlumnosView.as_view(), name="dictado_alumnos",),
    path("profesor/dictado/<int:dictado_id>/alumno/<int:alumno_id>/", ProfesorEditarCalificacionesView.as_view(), name="profesor_editar_calificaciones",
),

]