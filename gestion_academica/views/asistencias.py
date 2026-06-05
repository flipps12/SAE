from django.views.generic import ListView, DetailView
from django.urls import reverse_lazy, reverse
from django.db.models import Q, Prefetch, Count, Sum, Case, When, DecimalField
from django.db import transaction, models
# from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin

from gestion_academica.models import Alumno, Curso, CicloLectivo, HistorialAcademico


class ListaAsistenciasView(ListView):
    model = HistorialAcademico
    template_name = 'asistencias/lista_asistencias.html'
    context_object_name = 'inscripciones_control'

    def get_queryset(self):
        # 1. Traemos la información del alumno y curso optimizada de un solo viaje
        queryset = HistorialAcademico.objects.select_related(
            'alumno__persona',
            'curso__especialidad',
            'ciclo_lectivo',
            'burbuja'
        ).order_by('curso', 'alumno__persona__apellido', 'alumno__persona__nombre')

        # 2. Captura de filtros desde la URL
        ciclo_id = self.request.GET.get('ciclo')
        curso_id = self.request.GET.get('curso')
        search_query = self.request.GET.get('q')

        # 3. Aplicación de filtros dinámicos
        if ciclo_id:
            queryset = queryset.filter(ciclo_lectivo_id=ciclo_id)
        else:
            queryset = queryset.filter(ciclo_lectivo__activo=True)

        if curso_id:
            queryset = queryset.filter(curso_id=curso_id)

        if search_query:
            queryset = queryset.filter(
                Q(alumno__persona__nombre__icontains=search_query) |
                Q(alumno__persona__apellido__icontains=search_query) |
                Q(alumno__persona__dni__icontains=search_query)
            )

        # 4. Agregación condicional: Calculamos los totales sumando el 'valor_falta' del turno
        queryset = queryset.annotate(
            total_presentes=Count(
                Case(When(asistencias__estado='P', then=1))
            ),
            total_justificadas=Count(
                Case(When(asistencias__estado='J', then=1))
            ),
            # Sumamos los pesos reales de las faltas (ej: 0.5 o 1.0 según el turno)
            total_faltas=Sum(
                Case(
                    When(asistencias__estado='A', then=models.F('asistencias__turno__valor_falta')),
                    default=0,
                    output_field=DecimalField()
                )
            )
        )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Desplegables para los filtros
        context['ciclos'] = CicloLectivo.objects.all().order_by('-anio')
        context['cursos'] = Curso.objects.all()
        
        # Persistencia de filtros en el HTML
        context['selected_ciclo'] = int(self.request.GET.get('ciclo')) if self.request.GET.get('ciclo') else None
        context['selected_curso'] = int(self.request.GET.get('curso')) if self.request.GET.get('curso') else None
        context['search_query'] = self.request.GET.get('q', '')

        return context

# --------------------------------------------------------------------------------------
# ---                     DetalleAsistenciasAlumnoView                               ---
# --------------------------------------------------------------------------------------

class DetalleAsistenciasAlumnoView(DetailView):
    model = Alumno
    template_name = 'asistencias/detalle_asistencias_alumno.html'
    context_object_name = 'alumno'

    def get_queryset(self):
        # Traemos la persona y preparamos el prefetch ordenado cronológicamente de sus asistencias
        return Alumno.objects.select_related('persona').prefetch_related(
            Prefetch(
                'historiales',  # Relación con HistorialAcademico
                queryset=HistorialAcademico.objects.select_related(
                    'curso__especialidad',
                    'ciclo_lectivo',
                    'burbuja'
                ).prefetch_related(
                    'asistencias__turno'  # Traemos los turnos para calcular los pesos de las faltas
                ).order_by('-ciclo_lectivo__anio'),
                to_attr='historial_asistencias'
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        historial_agrupado = {}
        
        # Procesamos en el servidor los acumulados de cada año para aliviar al template
        for historial in self.object.historial_asistencias:
            anio = historial.ciclo_lectivo.anio
            
            # Calculamos totales físicos usando listas de Python sobre los datos ya cacheados en memoria
            lista_asistencias = historial.asistencias.all().order_by('-fecha', 'turno__nombre')
            
            presentes = sum(1 for a in lista_asistencias if a.estado == 'P')
            justificadas = sum(1 for a in lista_asistencias if a.estado == 'J')
            
            # Sumamos los pesos reales (0.5, 1.0) cargados en la base de datos para los ausentes
            faltas_totales = sum(
                float(a.turno.valor_falta) for a in lista_asistencias if a.estado == 'A'
            )
            
            historial_agrupado[anio] = {
                'curso': historial.curso,
                'burbuja': historial.burbuja,
                'grupo_taller': historial.get_grupo_taller_display(),
                'estado_final': historial.get_estado_final_display(),
                'totales': {
                    'presentes': presentes,
                    'justificadas': justificadas,
                    'faltas': faltas_totales
                },
                'registros': lista_asistencias
            }
            
        context['historial_asistencias_agrupado'] = historial_agrupado
        return context

