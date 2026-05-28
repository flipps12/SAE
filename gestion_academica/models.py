from django.db import models, transaction
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from .validators import dni_validator, cuil_validator

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

# --------------------------------------------------------------------------------------
# ---                              INFRAESTRUCTURA                                   ---
# --------------------------------------------------------------------------------------

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

# --------------------------------------------------------------------------------------

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

# --------------------------------------------------------------------------------------

class Especialidad(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    def __str__(self): return self.nombre

# --------------------------------------------------------------------------------------

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

# --------------------------------------------------------------------------------------

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
    
# --------------------------------------------------------------------------------------
# ---                                   ACTORES                                      ---
# --------------------------------------------------------------------------------------

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

# --------------------------------------------------------------------------------------

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

# --------------------------------------------------------------------------------------

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

# --------------------------------------------------------------------------------------

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

# --------------------------------------------------------------------------------------

class TipoCargo(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Tipo de Cargo"
        verbose_name_plural = "Tipos de Cargos"

# --------------------------------------------------------------------------------------

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

# --------------------------------------------------------------------------------------

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

# --------------------------------------------------------------------------------------

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
    
# --------------------------------------------------------------------------------------

class AsignacionPreceptor(models.Model):
    preceptor = models.ForeignKey(Preceptor, on_delete=models.CASCADE, related_name='asignaciones')
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    ciclo_lectivo = models.ForeignKey(CicloLectivo, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('preceptor', 'curso', 'ciclo_lectivo')


# --------------------------------------------------------------------------------------
# ---                                   ACADÉMICO                                    ---
# --------------------------------------------------------------------------------------

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

# --------------------------------------------------------------------------------------

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
    
# --------------------------------------------------------------------------------------

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
    
    
# --------------------------------------------------------------------------------------

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


# --------------------------------------------------------------------------------------
# ---                               TRANSACCIONAL                                    ---
# --------------------------------------------------------------------------------------


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

# --------------------------------------------------------------------------------------

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

# --------------------------------------------------------------------------------------

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

# --------------------------------------------------------------------------------------

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

# --------------------------------------------------------------------------------------

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

# --------------------------------------------------------------------------------------

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