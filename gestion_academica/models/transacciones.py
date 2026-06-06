from django.db import models, transaction
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from ..validators import dni_validator, cuil_validator
from . import Dictado, Alumno

# --------------------------------------------------------------------------------------
# ---                       CONSTANTES PARA CALIFICACIONES                           ---
# --------------------------------------------------------------------------------------

CONCEPTUAL_CHOICES = [
    ('TEA', 'Trayectoria Educativa Avanzada (TEA)'),
    ('TEP', 'Trayectoria Educativa en Proceso (TEP)'),
    ('TED', 'Trayectoria Educativa Discontinua (TED)'),
]

TIPO_ETAPA_CHOICES = [
    ('1C', 'Primer Cuatrimestre'),
    ('2C', 'Segundo Cuatrimestre'),
    ('DIC', 'Diciembre'),
    ('FEB', 'Febrero'),
    ('FINAL', 'Nota Final Anual'),
]

class InscripcionDictado(models.Model):
    """
    Vincula directamente al alumno con cada materia concreta (Dictado) 
    que debe cursar en el ciclo lectivo actual.
    """
    alumno = models.ForeignKey('Alumno', on_delete=models.CASCADE, related_name='inscripciones_dictados')
    dictado = models.ForeignKey('Dictado', on_delete=models.CASCADE, related_name='alumnos_inscriptos')
    ciclo_lectivo = models.ForeignKey('CicloLectivo', on_delete=models.CASCADE)
    
    CONDICION_CHOICES = [
        ('REGULAR', 'Regular'),
        ('RECURSANTE', 'Recursante'),
        ('PREVIA', 'Previa'),
    ]
    condicion = models.CharField(max_length=15, choices=CONDICION_CHOICES, default='REGULAR')

    class Meta:
        unique_together = ('alumno', 'dictado', 'ciclo_lectivo')
        verbose_name = "Inscripción a Dictado"
        verbose_name_plural = "Inscripciones a Dictados"

    def __str__(self):
        return f"{self.alumno.persona.apellido} en {self.dictado.materia.nombre} ({self.get_condicion_display()})"

class HorarioDictado(models.Model):
    DIAS_CHOICES = [(1, 'Lunes'), (2, 'Martes'), (3, 'Miércoles'), (4, 'Jueves'), (5, 'Viernes')]
    
    dictado = models.ForeignKey('Dictado', on_delete=models.CASCADE, related_name='horarios')
    dia_semana = models.PositiveSmallIntegerField(choices=DIAS_CHOICES)
    horario_inicio = models.TimeField()
    horario_fin = models.TimeField()
    aula = models.ForeignKey('Aula', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "Horario de Clase"
        verbose_name_plural = "Horarios de Clases"
        ordering = ['dia_semana', 'horario_inicio']
        constraints = [
            models.CheckConstraint(
                condition=models.Q(horario_inicio__lt=models.F('horario_fin')),
                name='check_horario_inicio_menor_fin',
            ),
        ]

    def __str__(self):
        return f"{self.dictado.materia} - {self.get_dia_semana_display()} {self.horario_inicio}-{self.horario_fin}"

    def clean(self):
        super().clean()
        
        if not self.horario_inicio or not self.horario_fin:
            return

        if self.horario_inicio >= self.horario_fin:
            raise ValidationError("El horario de inicio debe ser anterior al de fin.")

        if self.aula:
            solapamientos_aula = HorarioDictado.objects.filter(
                dia_semana=self.dia_semana,
                aula=self.aula,
                dictado__ciclo_lectivo=self.dictado.ciclo_lectivo,
                horario_inicio__lt=self.horario_fin,
                horario_fin__gt=self.horario_inicio
            ).exclude(pk=self.pk)

            if solapamientos_aula.exists():
                raise ValidationError(f"El aula {self.aula} ya está ocupada en este rango horario.")

        profesor = self.dictado.profesor
        if profesor:
            solapamientos_profe = HorarioDictado.objects.filter(
                dia_semana=self.dia_semana,
                dictado__profesor=profesor,
                dictado__ciclo_lectivo=self.dictado.ciclo_lectivo,
                horario_inicio__lt=self.horario_fin,
                horario_fin__gt=self.horario_inicio
            ).exclude(pk=self.pk)

            if solapamientos_profe.exists():
                raise ValidationError(f"El profesor {profesor} ya tiene otra clase asignada en este horario.")

class NotaEtapa(models.Model):
    """
    Notas institucionales de cierre (Boletín).
    """
    dictado = models.ForeignKey(Dictado, on_delete=models.CASCADE, related_name='notas_etapas')
    alumno = models.ForeignKey(Alumno, on_delete=models.PROTECT, related_name='notas_etapas')
    etapa = models.CharField(max_length=10, choices=TIPO_ETAPA_CHOICES)
    
    valor_numerico = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    
    valor_conceptual = models.CharField(
        max_length=3, 
        choices=CONCEPTUAL_CHOICES, 
        null=True, 
        blank=True
    )

    class Meta:
        unique_together = ('dictado', 'alumno', 'etapa')
        verbose_name = "Nota de Etapa"
        verbose_name_plural = "Notas de Etapa"

    def __str__(self):
        return f"{self.alumno.persona.apellido} - {self.etapa}: {self.valor_numerico}"

class NotaActividad(models.Model):
    """
    Notas de proceso (TPs, parciales) cargadas a voluntad por el profesor.
    """
    dictado = models.ForeignKey(Dictado, on_delete=models.CASCADE, related_name='notas_actividades')
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE, related_name='notas_actividades')

    cuatrimestre = models.IntegerField(choices=[(1, '1º Cuatrimestre'), (2, '2º Cuatrimestre')],db_index=True)
    nombre_actividad = models.CharField(max_length=100)
    fecha = models.DateField()
    valor = models.DecimalField(
        max_digits=4, 
        decimal_places=2,
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )

    class Meta:
        verbose_name = "Nota de Actividad"
        verbose_name_plural = "Notas de Actividades"

        indexes = [
            models.Index(fields=['dictado', 'alumno'], name='idx_notaact_dictado_alumno'),
        ]

    def __str__(self):
        return f"{self.alumno.persona.apellido} - {self.nombre_actividad}: {self.valor}"

class Intensificacion(models.Model):
    """
    Notas de refuerzo post-ciclo lectivo. 
    """
    dictado = models.ForeignKey(Dictado, on_delete=models.CASCADE, related_name='intensificaciones')
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE, related_name='intensificaciones')
    fecha = models.DateField(help_text="Fecha de la instancia de intensificación")
    valor = models.DecimalField(
        max_digits=4, 
        decimal_places=2,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Nota numérica única del intento"
    )

    class Meta:
        verbose_name = "Nota de Intensificación"
        verbose_name_plural = "Notas de Intensificación"
        ordering = ['fecha']

    def __str__(self):
        return f"Intensificación: {self.alumno.persona.apellido} - {self.valor} ({self.fecha})"

class Burbuja(models.Model):
    nombre = models.CharField(max_length=50)
    ciclo_lectivo = models.ForeignKey(
        'CicloLectivo', 
        on_delete=models.CASCADE, 
        related_name='burbujas'
    )

    def __str__(self):
        return f"{self.nombre} ({self.ciclo_lectivo.anio})"

    class Meta:
        verbose_name = "Burbuja"
        verbose_name_plural = "Burbujas"
        constraints = [
            models.UniqueConstraint(
                fields=['nombre', 'ciclo_lectivo'], 
                name='unique_nombre_burbuja_por_ciclo'
            )
        ]

class Asistencia(models.Model):
    class EstadoAsistencia(models.TextChoices):
        PRESENTE = 'P', 'Presente'
        AUSENTE = 'A', 'Ausente'
        JUSTIFICADA = 'J', 'Justificada'

    inscripcion = models.ForeignKey(
        'HistorialAcademico', 
        on_delete=models.CASCADE, 
        related_name='asistencias'
    )
    
    fecha = models.DateField(db_index=True)
    turno = models.ForeignKey('Turno', on_delete=models.CASCADE)
    
    estado = models.CharField(
        max_length=1, 
        choices=EstadoAsistencia.choices, 
        default=EstadoAsistencia.PRESENTE
    )
    
    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True,
        blank=True,
        editable=False 
    )

    burbuja_sesion = models.ForeignKey(
        'Burbuja', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Burbuja que asistió"
    )

    class Meta:
        unique_together = ('inscripcion', 'fecha', 'turno')
        verbose_name = "Asistencia"
        verbose_name_plural = "Asistencias"

        indexes = [
            models.Index(fields=['inscripcion', 'fecha'], name='idx_asistencia_insc_fecha'),
        ]

    def __str__(self):
        return f"{self.inscripcion.alumno.persona.apellido} - {self.fecha} ({self.get_estado_display()})"

class HistorialAcademico(models.Model):
    ESTADOS_FINALES = [
        ('CURSANDO', 'Cursando'),
        ('PASE', 'Pase'),
        ('EGRESADO', 'Egresado'),
        ('ABANDONO', 'Abandono/Pase'),
    ]

    alumno = models.ForeignKey(
        'Alumno', 
        on_delete=models.PROTECT, 
        related_name='historiales'
    )
    ciclo_lectivo = models.ForeignKey(
        'CicloLectivo', 
        on_delete=models.PROTECT, 
        related_name='inscripciones'
    )
    curso = models.ForeignKey(
        'Curso', 
        on_delete=models.PROTECT, 
        related_name='alumnos_inscriptos'
    )
    burbuja = models.ForeignKey(
        'Burbuja', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='inscripciones',
        verbose_name="Burbuja (Opcional)"
    )
    grupo_taller = models.CharField(
        max_length=1, 
        choices=[('A', 'Grupo A'), ('B', 'Grupo B')], 
        blank=True, 
        null=True,
        verbose_name="Grupo de Taller"
    )
    estado_final = models.CharField(
        max_length=20, 
        choices=ESTADOS_FINALES, 
        default='CURSANDO'
    )

    class Meta:
        verbose_name = "Historial Académico"
        verbose_name_plural = "Historiales Académicos"
        unique_together = ('alumno', 'ciclo_lectivo')
        ordering = ['-ciclo_lectivo__anio', 'alumno__persona__apellido']

    def __str__(self):
        return f"{self.alumno} - {self.curso} ({self.ciclo_lectivo})"

    def clean(self):
        super().clean()
        
        if self.burbuja and self.ciclo_lectivo:
            if self.burbuja.ciclo_lectivo != self.ciclo_lectivo:
                raise ValidationError({
                    'burbuja': f"La burbuja '{self.burbuja.nombre}' pertenece al ciclo {self.burbuja.ciclo_lectivo.anio}, "
                               f"pero la inscripción es para el ciclo {self.ciclo_lectivo.anio}."
                })

    @property
    def especialidad(self):
        """Devuelve la especialidad a través del curso asignado"""
        return self.curso.especialidad