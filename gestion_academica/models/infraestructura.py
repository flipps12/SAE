from django.db import models, transaction
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from ..validators import dni_validator, cuil_validator

class CicloLectivo(models.Model):
    anio = models.IntegerField(unique=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Ciclo Lectivo"
        verbose_name_plural = "Ciclos Lectivos"
        constraints = [models.UniqueConstraint(fields=['activo'],condition=models.Q(activo=True),name='unique_active_ciclo_lectivo')]

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if self.activo:
                CicloLectivo.objects.filter(activo=True).exclude(pk=self.pk).update(activo=False)
            
            super(CicloLectivo, self).save(*args, **kwargs)

    def __str__(self): 
        return str(self.anio)

class Turno(models.Model):
    nombre = models.CharField(max_length=20, unique=True)
    valor_falta = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        default=0.5,
        validators=[
            MinValueValidator(0, message="El valor no puede ser negativo."),
            MaxValueValidator(1, message="El valor de una falta no puede ser mayor a 1.0.")
        ],
        help_text="Ejemplo: 0.5 para media falta, 1.0 para falta completa."
    )

    def __str__(self): 
        return self.nombre
    
class Especialidad(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    def __str__(self): return self.nombre

class Aula(models.Model):
    TIPO_AULA_CHOICES = [
        ('AULA', 'Aula'),
        ('LAB.', 'Laboratorio'),
        ('S.U.M', 'S.U.M'),
        ('BIBLIO.', 'Biblioteca'),
    ]
    nombre = models.CharField(max_length=50, unique=True)
    capacidad = models.PositiveIntegerField()
    tipo = models.CharField(max_length=10, choices=TIPO_AULA_CHOICES, default='AULA')
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"

class Curso(models.Model):
    nivel = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1, message="El nivel mínimo es 1."),
            MaxValueValidator(7, message="El nivel máximo permitido es 7.")
        ],
        help_text="Ingrese el año (ej: 1 al 7)"
    )
    division = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1, message="La división mínima es 1."),
            MaxValueValidator(15, message="La división máxima permitida es 15.")
        ],
        help_text="Ingrese el número de división"
    )
    especialidad = models.ForeignKey('Especialidad', on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Curso"
        verbose_name_plural = "Cursos"
        ordering = ['nivel', 'division']
        unique_together = ('nivel', 'division', 'especialidad')

    def __str__(self): 
        return f"{self.nivel}° {self.division}ª - {self.especialidad}"
    