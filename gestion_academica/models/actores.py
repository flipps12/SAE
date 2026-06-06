from django.db import models, transaction
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from ..validators import dni_validator, cuil_validator


class Persona(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='persona',
        null=True, 
        blank=True,
        help_text="Usuario de sistema vinculado"
    )
    
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    
    dni = models.CharField(
        max_length=8, 
        unique=True, 
        validators=[dni_validator],
        help_text="Número de documento sin puntos"
    )

    cuil = models.CharField(
        max_length=11, 
        unique=True, 
        validators=[cuil_validator],
        help_text="CUIL sin guiones"
    )
    
    fecha_nacimiento = models.DateField(null=True, blank=True)
    fecha_ingreso = models.DateField(null=True, blank=True)
    numero_legajo = models.CharField(max_length=30, unique=True)
    
    email = models.EmailField(blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    domicilio = models.TextField(blank=True)

    class Meta:
        verbose_name = "Persona"
        verbose_name_plural = "Personas"
        ordering = ['apellido', 'nombre']

    def __str__(self):
        return f"{self.apellido}, {self.nombre} (Legajo: {self.numero_legajo})"

class Profesor(models.Model):
    persona = models.OneToOneField(
        Persona, 
        on_delete=models.CASCADE, 
        related_name='perfil_profesor'
    )
    
    telefono_emergencia = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"Prof. {self.persona.apellido}, {self.persona.nombre}"

    class Meta:
        verbose_name = "Profesor"
        verbose_name_plural = "Profesores"

class Alumno(models.Model):
    persona = models.OneToOneField(
        Persona, 
        on_delete=models.CASCADE, 
        related_name='perfil_alumno'
    )
    
    libro = models.CharField(blank=True, max_length=30)
    folio = models.CharField(blank=True, max_length=30)
    
    activo = models.BooleanField(
        default=True, 
        help_text="Define si el alumno es parte de la institución actualmente."
    )

    def __str__(self):
        return f"Alumno: {self.persona.apellido}, {self.persona.nombre}"

    class Meta:
        verbose_name = "Alumno"
        verbose_name_plural = "Alumnos"

class PersonalNoDocente(models.Model):
    persona = models.OneToOneField(
        Persona, 
        on_delete=models.CASCADE, 
        related_name='perfil_nodocente'
    )
    
    observaciones = models.TextField(
        blank=True, 
        help_text="Notas sobre el personal (ej. turno de limpieza, tareas específicas)"
    )

    def __str__(self):
        return f"No Docente: {self.persona.apellido}, {self.persona.nombre}"

    class Meta:
        verbose_name = "Personal No Docente"
        verbose_name_plural = "Personal No Docente"

class TipoCargo(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Tipo de Cargo"
        verbose_name_plural = "Tipos de Cargos"

class PersonalCargo(models.Model):
    persona = models.OneToOneField(
        'Persona', 
        on_delete=models.CASCADE, 
        related_name='perfil_cargo'
    )
    
    cargos = models.ManyToManyField(
        'TipoCargo', 
        through='AsignacionCargo',
        related_name='personal_asignado'
    )

    def __str__(self):
        return f"Perfil de Cargos: {self.persona.apellido}, {self.persona.nombre}"

    class Meta:
        verbose_name = "Personal con Cargo"
        verbose_name_plural = "Personal con Cargos"

class AsignacionCargo(models.Model):
    persona_cargo = models.ForeignKey(
        PersonalCargo, 
        on_delete=models.CASCADE,
        related_name='asignaciones'
    )
    cargo = models.ForeignKey(
        'TipoCargo', 
        on_delete=models.CASCADE,
        related_name='asignaciones_historicas'
    )
    
    fecha_inicio = models.DateField(
        verbose_name="Fecha de Toma de Posesión",
        help_text="Fecha en la que inicia en este cargo específico"
    )
    fecha_fin = models.DateField(
        null=True, 
        blank=True, 
        verbose_name="Fecha de Cese",
        help_text="Dejar en blanco si el cargo sigue activo"
    )
    
    resolucion = models.CharField(
        max_length=100, 
        blank=True, 
        help_text="Nro de Resolución o Disposición"
    )
    
    activo = models.BooleanField(
        default=True, 
        help_text="Indica si el cargo está vigente actualmente"
    )

    class Meta:
        verbose_name = "Asignación de Cargo"
        verbose_name_plural = "Asignaciones de Cargos"
        ordering = ['-fecha_inicio']

    def __str__(self):
        estado = "Activo" if self.activo else "Cesado"
        return f"{self.persona_cargo.persona.apellido} - {self.cargo.nombre} ({estado})"

class Preceptor(models.Model):
    persona = models.OneToOneField(
        Persona, 
        on_delete=models.CASCADE, 
        related_name='perfil_preceptor'
    )

    class Meta:
        verbose_name = "Preceptor"
        verbose_name_plural = "Preceptores"

    def __str__(self):
        return f"Preceptor: {self.persona.apellido}"