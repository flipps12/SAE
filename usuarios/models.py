from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class TipoUsuario(models.TextChoices):
        ALUMNO = 'ALUMNO', 'Alumno'
        PROFESOR = 'PROFESOR', 'Profesor'
        PRECEPTOR = 'PRECEPTOR', 'Preceptor'
        PERNODOC = 'NO DOCENTE', 'Personal no Docente'
        CARGOS = 'CARGOS', 'Cargos'
        JERARQUICOS = 'JERARQUICOS', 'Jerarquicos'
    
    user_type = models.CharField(
        max_length=15,
        choices=TipoUsuario.choices,
        default=TipoUsuario.ALUMNO,
        verbose_name="Tipo de usuario"
    )