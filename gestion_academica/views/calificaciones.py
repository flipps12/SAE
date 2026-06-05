from django.views.generic import ListView, DetailView
from django.db.models import Q, Prefetch
# from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin

from gestion_academica.models import Alumno, Curso, CicloLectivo, InscripcionDictado, Dictado


class ListaCalificacionesView(ListView):
    model = InscripcionDictado
    template_name = 'calificaciones/lista_calificaciones.html'
    context_object_name = 'inscripciones'

    def get_queryset(self):
        # 1. Optimización de base para traer datos del alumno y la materia de un solo viaje a la BD
        queryset = InscripcionDictado.objects.select_related(
            'alumno__persona',
            'dictado__materia',
            'dictado__curso__especialidad',
            'ciclo_lectivo'
        ).prefetch_related(
            'dictado__notas_etapas',       # Prefetch de notas institucionales (Boletín)
            'dictado__notas_actividades',  # Prefetch de trabajos prácticos/parciales
            'dictado__intensificaciones'   # Prefetch de instancias de recuperación
        ).order_by('dictado__curso', 'alumno__persona__apellido', 'alumno__persona__nombre')

        # 2. Captura de filtros desde los parámetros GET del navegador
        ciclo_id = self.request.GET.get('ciclo')
        curso_id = self.request.GET.get('curso')
        dictado_id = self.request.GET.get('dictado')
        search_query = self.request.GET.get('q')

        # 3. Aplicación de filtros dinámicos
        if ciclo_id:
            queryset = queryset.filter(ciclo_lectivo_id=ciclo_id)
        else:
            # Si no seleccionan ciclo, por defecto filtramos por el ciclo activo
            queryset = queryset.filter(ciclo_lectivo__activo=True)

        if curso_id:
            queryset = queryset.filter(dictado__curso_id=curso_id)

        if dictado_id:
            queryset = queryset.filter(dictado_id=dictado_id)

        if search_query:
            queryset = queryset.filter(
                Q(alumno__persona__nombre__icontains=search_query) |
                Q(alumno__persona__apellido__icontains=search_query) |
                Q(alumno__persona__dni__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Inyectamos los listados para los desplegables (Selects) del filtro
        context['ciclos'] = CicloLectivo.objects.all().order_by('-anio')
        context['cursos'] = Curso.objects.all()
        
        # Si ya se seleccionó un curso, filtramos las materias/dictados de ese curso para facilitar la UI
        curso_seleccionado = self.request.GET.get('curso')
        if curso_seleccionado:
            context['dictados'] = Dictado.objects.filter(curso_id=curso_seleccionado).select_related('materia')
        else:
            context['dictados'] = Dictado.objects.select_related('materia', 'curso').all()[:50] # Limite prudencial si no hay filtro

        # Mantener los valores actuales de los filtros en la plantilla HTML
        context['selected_ciclo'] = int(self.request.GET.get('ciclo')) if self.request.GET.get('ciclo') else None
        context['selected_curso'] = int(self.request.GET.get('curso')) if self.request.GET.get('curso') else None
        context['selected_dictado'] = int(self.request.GET.get('dictado')) if self.request.GET.get('dictado') else None
        context['search_query'] = self.request.GET.get('q', '')

        return context

# --------------------------------------------------------------------------------------
# ---                   DetalleCalificacionesAlumnoView                              ---
# --------------------------------------------------------------------------------------


class DetalleCalificacionesAlumnoView(DetailView):
    model = Alumno
    template_name = 'calificaciones/detalle_alumno.html'
    context_object_name = 'alumno'

    def get_queryset(self):
        # Traemos la persona de un viaje y preparamos el prefetch de sus materias cursadas
        return Alumno.objects.select_related('persona').prefetch_related(
            Prefetch(
                'inscripciones_dictados',
                queryset=InscripcionDictado.objects.select_related(
                    'dictado__materia', 
                    'dictado__curso__especialidad',
                    'ciclo_lectivo'
                ).prefetch_related(
                    'dictado__notas_actividades',
                    'dictado__notas_etapas',
                    'dictado__intensificaciones'
                ).order_by('-ciclo_lectivo__anio', 'dictado__materia__nombre'),
                to_attr='historial_materias' # Guardamos en memoria para manipularlo fácil en el template
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Agrupamos las materias por Ciclo Lectivo en el servidor para facilitar el renderizado
        materias_por_ciclo = {}
        for inscripcion in self.object.historial_materias:
            anio = inscripcion.ciclo_lectivo.anio
            if anio not in materias_por_ciclo:
                materias_por_ciclo[anio] = {
                    'curso': inscripcion.dictado.curso,
                    'inscripciones': []
                }
            materias_por_ciclo[anio]['inscripciones'].append(inscripcion)
            
        context['historial_agrupado'] = materias_por_ciclo
        return context