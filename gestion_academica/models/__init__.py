# gestion_academica/models/__init__.py

from .infraestructura import CicloLectivo, Turno, Especialidad, Aula, Curso
from .actores import Persona, Profesor, Alumno, PersonalNoDocente, TipoCargo, PersonalCargo, AsignacionCargo, Preceptor
from .academico import Materia, Dictado, AsignacionPreceptor
from .transacciones import InscripcionDictado, NotaEtapa, NotaActividad, Intensificacion, Burbuja, Asistencia, HistorialAcademico, HorarioDictado, CONCEPTUAL_CHOICES, TIPO_ETAPA_CHOICES
from .comunicados import Comunicado