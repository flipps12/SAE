from django.db import models, transaction
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from ..validators import dni_validator, cuil_validator
from . import Preceptor, Curso, CicloLectivo, Especialidad, Profesor


class AsignacionPreceptor(models.Model):
    preceptor = models.ForeignKey(Preceptor, on_delete=models.CASCADE, related_name='asignaciones')
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    ciclo_lectivo = models.ForeignKey(CicloLectivo, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('preceptor', 'curso', 'ciclo_lectivo')

class Materia(models.Model):
    TIPOS = [('AULA', 'Aula/Teoría'), ('TALLER', 'Taller/Práctica')]
    nombre = models.CharField(max_length=100)
    
    especialidad = models.ForeignKey(
        Especialidad, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Dejar vacío si la materia es común a todas las especialidades (Troncal)."
    )

    tipo = models.CharField(max_length=10, choices=TIPOS, default='AULA')
    
    def __str__(self):
        tipo = self.especialidad.nombre if self.especialidad else "Troncal"
        return f"{self.nombre} ({tipo})"

class Dictado(models.Model):
    SITUACIONES_REVISTA = [
        ('TITULAR', 'Titular'),
        ('INTERINO', 'Interino'),
        ('SUPLENTE', 'Suplente'),
        ('PROVICIONAL', 'Provicional'),
    ]

    FORMAS_INGRESO = [
        ('MAD', 'MAD'),
        ('REUBICADO', 'Reubicado'),
        ('ACTO_PUBLICO', 'Acto Público'),
        ('ACTO_PUBLICO_DIGITAL', 'Acto Público Digital'),
        ('DESTINO_DEFINITIVO', 'Destino Definitivo'),
        ('PROPUESTA_NOMBRAMIENTO', 'Propuesta Nombramiento'),
        ('PROYECTO_ELECCION', 'Proyecto y Elección'),
        ('DISPOSICION', 'Disposición'),
        ('OTROS', 'Otros'),
    ]

class AsignacionPreceptor(models.Model):
    preceptor = models.ForeignKey(Preceptor, on_delete=models.CASCADE, related_name='asignaciones')
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    ciclo_lectivo = models.ForeignKey(CicloLectivo, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('preceptor', 'curso', 'ciclo_lectivo')

class Dictado(models.Model):
    SITUACIONES_REVISTA = [
        ('TITULAR', 'Titular'),
        ('INTERINO', 'Interino'),
        ('SUPLENTE', 'Suplente'),
        ('PROVICIONAL', 'Provicional'),
    ]

    FORMAS_INGRESO = [
        ('MAD', 'MAD'),
        ('REUBICADO', 'Reubicado'),
        ('ACTO_PUBLICO', 'Acto Público'),
        ('ACTO_PUBLICO_DIGITAL', 'Acto Público Digital'),
        ('DESTINO_DEFINITIVO', 'Destino Definitivo'),
        ('PROPUESTA_NOMBRAMIENTO', 'Propuesta Nombramiento'),
        ('PROYECTO_ELECCION', 'Proyecto y Elección'),
        ('DISPOSICION', 'Disposición'),
        ('OTROS', 'Otros'),
    ]

    materia = models.ForeignKey(Materia, on_delete=models.CASCADE, related_name='dictados')
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='dictados')
    profesor = models.ForeignKey(Profesor, on_delete=models.PROTECT, null=True, blank=True, related_name='dictados')
    ciclo_lectivo = models.ForeignKey(CicloLectivo, on_delete=models.CASCADE, related_name='dictados')

    # --- CAMPOS ADMINISTRATIVOS ACTUALIZADOS ---
    pid = models.CharField(max_length=50, verbose_name="PID", null=True, blank=True)
    cupof = models.IntegerField(verbose_name="CUPOF", null=True, blank=True)
    secuencia = models.IntegerField(verbose_name="Secuencia", null=True, blank=True)
    
    toma_posesion = models.DateField(verbose_name="Toma de Posesión", null=True, blank=True)
    
    forma_ingreso = models.CharField(
        max_length=30, 
        choices=FORMAS_INGRESO, 
        verbose_name="Forma de Ingreso", 
        null=True, 
        blank=True
    )
    
    situacion_revista = models.CharField(
        max_length=20, 
        choices=SITUACIONES_REVISTA, 
        verbose_name="Situación de Revista", 
        null=True, 
        blank=True
    )

    class Meta:
        unique_together = ('materia', 'curso', 'ciclo_lectivo')
        verbose_name = "Dictado de Materia"
        verbose_name_plural = "Dictados de Materias"

    def __str__(self):
        profe_str = f" | {self.profesor}" if self.profesor else " | Sin Profesor asignado"
        return f"{self.materia.nombre} - {self.curso} ({self.ciclo_lectivo}){profe_str}"
    
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE, related_name='dictados')
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='dictados')
    profesor = models.ForeignKey(Profesor, on_delete=models.PROTECT, null=True, blank=True, related_name='dictados')
    ciclo_lectivo = models.ForeignKey(CicloLectivo, on_delete=models.CASCADE, related_name='dictados')

    # --- CAMPOS ADMINISTRATIVOS ACTUALIZADOS ---
    pid = models.CharField(max_length=50, verbose_name="PID", null=True, blank=True)
    cupof = models.IntegerField(verbose_name="CUPOF", null=True, blank=True)
    secuencia = models.IntegerField(verbose_name="Secuencia", null=True, blank=True)
    
    toma_posesion = models.DateField(verbose_name="Toma de Posesión", null=True, blank=True)
    
    forma_ingreso = models.CharField(
        max_length=30, 
        choices=FORMAS_INGRESO, 
        verbose_name="Forma de Ingreso", 
        null=True, 
        blank=True
    )
    
    situacion_revista = models.CharField(
        max_length=20, 
        choices=SITUACIONES_REVISTA, 
        verbose_name="Situación de Revista", 
        null=True, 
        blank=True
    )

    class Meta:
        unique_together = ('materia', 'curso', 'ciclo_lectivo')
        verbose_name = "Dictado de Materia"
        verbose_name_plural = "Dictados de Materias"

    def __str__(self):
        profe_str = f" | {self.profesor}" if self.profesor else " | Sin Profesor asignado"
        return f"{self.materia.nombre} - {self.curso} ({self.ciclo_lectivo}){profe_str}"
    