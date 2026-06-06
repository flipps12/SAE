from django.db import models, transaction
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from ..validators import dni_validator, cuil_validator

class Comunicado(models.Model):
    class VisibilidadChoices(models.TextChoices):
        GLOBAL = 'GLOBAL', 'Global (Solo Logueados)'
        ESTUDIANTES = 'ESTUDIANTES', 'Solo Estudiantes'
        DOCENTES = 'DOCENTES', 'Solo Docentes'

    titulo = models.CharField(max_length=150, verbose_name="Título")
    contenido = models.TextField(verbose_name="Contenido del Comunicado")
    visibilidad = models.CharField(
        max_length=15,
        choices=VisibilidadChoices.choices,
        default=VisibilidadChoices.GLOBAL,
        verbose_name="Visibilidad"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    
    # Relación con el autor que lo creó (usuarios.User)
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='comunicados_creados',
        verbose_name="Autor"
    )

    class Meta:
        verbose_name = "Comunicado"
        verbose_name_plural = "Comunicados"
        ordering = ['-fecha_creacion']  # Los más nuevos primero por defecto

    def __str__(self):
        return f"{self.titulo} ({self.get_visibilidad_display()})"