from django.contrib import admin

from .models import (
    CicloLectivo, Turno, Especialidad, Aula, Profesor, 
    Preceptor, Alumno, Materia, Curso, Dictado, Asistencia,
    NotaEtapa, PersonalNoDocente, TipoCargo, PersonalCargo, HistorialAcademico,
    AsignacionPreceptor, Burbuja, NotaActividad, Intensificacion, HorarioDictado,
    Persona, AsignacionCargo
)

# --------------------------------------------------------------------------------------
# ---                                   INLINES                                      ---
# --------------------------------------------------------------------------------------

class ProfesorInline(admin.StackedInline):
    model = Profesor
    extra = 0

class AlumnoInline(admin.StackedInline):
    model = Alumno
    extra = 0

class PreceptorInline(admin.StackedInline):
    model = Preceptor
    extra = 0

class AsignacionPreceptorInline(admin.TabularInline):
    model = AsignacionPreceptor
    extra = 1

class HorarioDictadoInline(admin.TabularInline):
    model = HorarioDictado
    extra = 1
    min_num = 1

class DictadoInline(admin.TabularInline):
    model = Dictado
    extra = 0
    fields = ['materia', 'profesor', 'ciclo_lectivo']


class AsignacionCargoInline(admin.TabularInline):
    """
    Permite editar las asignaciones de cargos directamente 
    dentro de la ficha de PersonalCargo.
    """
    model = AsignacionCargo
    extra = 1
    fields = ('cargo', 'fecha_inicio', 'fecha_fin', 'resolucion', 'activo')
    autocomplete_fields = ['cargo']

# --------------------------------------------------------------------------------------
# ---                          CONFIGURACIÓN DE ADMINS                               ---
# --------------------------------------------------------------------------------------


@admin.register(Persona)
class PersonaAdmin(admin.ModelAdmin):
    list_display = ('apellido', 'nombre', 'dni', 'numero_legajo', 'get_roles')
    search_fields = ('apellido', 'nombre', 'dni', 'numero_legajo')
    inlines = [ProfesorInline, AlumnoInline, PreceptorInline]

    def get_roles(self, obj):
        roles = []
        if hasattr(obj, 'perfil_profesor'): roles.append("Prof")
        if hasattr(obj, 'perfil_alumno'): roles.append("Alu")
        if hasattr(obj, 'perfil_preceptor'): roles.append("Prec")
        return ", ".join(roles) if roles else "-"
    get_roles.short_description = 'Roles'

# --------------------------------------------------------------------------------------


@admin.register(AsignacionCargo)
class AsignacionCargoAdmin(admin.ModelAdmin):
    list_display = ('cargo', 'get_persona', 'fecha_inicio', 'activo')
    list_filter = ('activo', 'cargo', 'fecha_inicio')
    search_fields = ('persona_cargo__persona__apellido', 'resolucion')

    def get_persona(self, obj):
        return obj.persona_cargo.persona.apellido
    get_persona.short_description = 'Personal'

# --------------------------------------------------------------------------------------

@admin.register(Alumno)
class AlumnoAdmin(admin.ModelAdmin):
    list_display = ('get_apellido', 'get_nombre', 'get_dni', 'get_legajo', 'activo')
    search_fields = ('persona__apellido', 'persona__nombre', 'persona__dni', 'persona__numero_legajo')
    
    def get_apellido(self, obj): return obj.persona.apellido
    def get_nombre(self, obj): return obj.persona.nombre
    def get_dni(self, obj): return obj.persona.dni
    def get_legajo(self, obj): return obj.persona.numero_legajo
    get_apellido.short_description = 'Apellido'
    get_nombre.short_description = 'Nombre'

    fieldsets = (
        ('Vinculación', {
            'fields': ('persona', 'activo'),
        }),
        ('Datos de Secretaría', {
            'fields': (('libro', 'folio'),), 
        }),
    )

# --------------------------------------------------------------------------------------

@admin.register(Profesor)
class ProfesorAdmin(admin.ModelAdmin):
    list_display = ('get_apellido', 'get_nombre', 'get_legajo', 'get_dni', 'get_fecha_ingreso')
    search_fields = ('persona__apellido', 'persona__nombre', 'persona__dni', 'persona__numero_legajo')
    readonly_fields = ('get_fecha_ingreso',)

    def get_apellido(self, obj): return obj.persona.apellido
    def get_nombre(self, obj): return obj.persona.nombre
    def get_dni(self, obj): return obj.persona.dni
    def get_legajo(self, obj): return obj.persona.numero_legajo
    
    @admin.display(description='Fecha de Ingreso')
    def get_fecha_ingreso(self, obj): return obj.persona.fecha_ingreso

    fieldsets = (
        ('Vinculación', { 'fields': ('persona',) }),
        ('Datos Laborales', { 
            'fields': ('get_fecha_ingreso', 'telefono_emergencia') 
        }),
    )

# --------------------------------------------------------------------------------------

@admin.register(Preceptor)
class PreceptorAdmin(admin.ModelAdmin):
    list_display = ('get_apellido', 'get_nombre', 'get_dni')
    search_fields = ('persona__apellido', 'persona__nombre', 'persona__dni')
    inlines = [AsignacionPreceptorInline]

    def get_apellido(self, obj): return obj.persona.apellido
    def get_nombre(self, obj): return obj.persona.nombre
    def get_dni(self, obj): return obj.persona.dni

# --------------------------------------------------------------------------------------

@admin.register(PersonalCargo)
class PersonalCargoAdmin(admin.ModelAdmin):
    list_display = ('get_apellido', 'get_nombre', 'get_cargos_activos', 'get_antiguedad')
    search_fields = ('persona__apellido', 'persona__nombre', 'persona__dni')

    inlines = [AsignacionCargoInline]

    # --- MÉTODOS PARA EL LISTADO ---

    @admin.display(description='Apellido', ordering='persona__apellido')
    def get_apellido(self, obj):
        return obj.persona.apellido

    @admin.display(description='Nombre', ordering='persona__nombre')
    def get_nombre(self, obj):
        return obj.persona.nombre

    @admin.display(description='Cargos Activos')
    def get_cargos_activos(self, obj):
        activos = obj.asignaciones.filter(activo=True)
        return ", ".join([a.cargo.nombre for a in activos]) if activos else "Sin cargos activos"

    @admin.display(description='Antigüedad (Ingreso)')
    def get_antiguedad(self, obj):
        return obj.persona.fecha_ingreso if obj.persona.fecha_ingreso else "No registrada"

# --------------------------------------------------------------------------------------

@admin.register(PersonalNoDocente)
class PersonalNoDocenteAdmin(admin.ModelAdmin):
    list_display = ('persona', 'get_legajo', 'get_fecha_ingreso')

    @admin.display(description='Fecha de Ingreso', ordering='persona__fecha_ingreso')
    def get_fecha_ingreso(self, obj):
        return obj.persona.fecha_ingreso

    @admin.display(description='Legajo', ordering='persona__numero_legajo')
    def get_legajo(self, obj):
        return obj.persona.numero_legajo
    
# --------------------------------------------------------------------------------------

@admin.register(CicloLectivo)
class CicloLectivoAdmin(admin.ModelAdmin):
    list_display = ('anio', 'activo')
    list_editable = ('activo',)

# --------------------------------------------------------------------------------------

@admin.register(Aula)
class AulaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'capacidad')
    list_filter = ('tipo',)
    search_fields = ('nombre',)

# --------------------------------------------------------------------------------------

@admin.register(HistorialAcademico)
class HistorialAcademicoAdmin(admin.ModelAdmin):
    list_display = ('alumno', 'curso', 'get_especialidad', 'ciclo_lectivo', 'burbuja', 'estado_final')
    list_filter = ('ciclo_lectivo', 'curso__especialidad', 'burbuja', 'estado_final')
    search_fields = ('alumno__persona__apellido', 'alumno__persona__nombre', 'alumno__persona__dni')
    autocomplete_fields = ['alumno', 'curso']

    def get_especialidad(self, obj):
        return obj.especialidad
    get_especialidad.short_description = 'Especialidad'

# --------------------------------------------------------------------------------------

@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ('nivel', 'division', 'especialidad')
    search_fields = ('nivel', 'division', 'especialidad__nombre') 
    inlines = [DictadoInline]

# --------------------------------------------------------------------------------------

@admin.register(Dictado)
class DictadoAdmin(admin.ModelAdmin):
    list_display = ('materia', 'curso', 'profesor', 'ciclo_lectivo')
    list_filter = ('ciclo_lectivo', 'curso', 'profesor')
    search_fields = ('materia__nombre', 'profesor__persona__apellido')
    inlines = [HorarioDictadoInline]

# --------------------------------------------------------------------------------------

@admin.register(Materia)
class MateriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'especialidad', 'tipo')
    list_filter = ('tipo', 'especialidad')
    search_fields = ('nombre',)

# --------------------------------------------------------------------------------------

@admin.register(Asistencia)
class AsistenciaAdmin(admin.ModelAdmin):
    list_display = ('get_alumno', 'get_curso', 'fecha', 'turno', 'estado')
    list_filter = ('fecha', 'turno', 'estado', 'inscripcion__curso')
    search_fields = ('inscripcion__alumno__persona__apellido', 'inscripcion__alumno__persona__dni')

    @admin.display(description='Alumno', ordering='inscripcion__alumno__persona__apellido')
    def get_alumno(self, obj):
        return f"{obj.inscripcion.alumno.persona.apellido}, {obj.inscripcion.alumno.persona.nombre}"

    @admin.display(description='Curso', ordering='inscripcion__curso')
    def get_curso(self, obj):
        return obj.inscripcion.curso

    fields = ('inscripcion', 'fecha', 'turno', 'estado', 'burbuja_sesion')

# --------------------------------------------------------------------------------------

@admin.register(NotaEtapa)
class NotaEtapaAdmin(admin.ModelAdmin):
    list_display = ('alumno', 'dictado', 'etapa', 'valor_numerico', 'valor_conceptual')
    list_filter = ('etapa', 'dictado__ciclo_lectivo')

# --------------------------------------------------------------------------------------

@admin.register(NotaActividad)
class NotaActividadAdmin(admin.ModelAdmin):
    list_display = ('alumno', 'dictado', 'nombre_actividad', 'valor')

# --------------------------------------------------------------------------------------

@admin.register(Intensificacion)
class IntensificacionAdmin(admin.ModelAdmin):
    list_display = ('alumno', 'dictado', 'fecha', 'valor')

# --------------------------------------------------------------------------------------

@admin.register(TipoCargo)
class TipoCargoAdmin(admin.ModelAdmin):
    search_fields = ['nombre'] 
    list_display = ('nombre',)

# --------------------------------------------------------------------------------------

admin.site.register(Turno)
admin.site.register(Especialidad)
admin.site.register(Burbuja)