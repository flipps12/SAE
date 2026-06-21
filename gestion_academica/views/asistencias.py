# gestion_academica/views/asistencias.py
from django.views.generic import ListView, DetailView, TemplateView
from django.urls import reverse_lazy, reverse
from django.db.models import Q, Prefetch, Count, Sum, Case, When, DecimalField
from django.db import transaction, models
from django.shortcuts import redirect
from django.utils.dateparse import parse_date
# from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from datetime import date

from gestion_academica.models import Alumno, Curso, CicloLectivo, HistorialAcademico, Turno, Burbuja, Asistencia



class PlanillaAsistenciaPreceptorView(TemplateView):
    template_name = 'asistencias/planilla_preceptor.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Selectores base ordenados
        context['ciclos'] = CicloLectivo.objects.all().order_by('-anio')
        context['cursos'] = Curso.objects.all().select_related('especialidad')
        context['turnos'] = Turno.objects.all()
        
        # Recuperar filtros por GET
        ciclo_id = self.request.GET.get('ciclo')
        curso_id = self.request.GET.get('curso')
        turno_id = self.request.GET.get('turno')
        burbuja_id = self.request.GET.get('burbuja')
        grupo_taller = self.request.GET.get('grupo_taller')
        fecha_str = self.request.GET.get('fecha')

        # Manejo estricto de fecha por defecto (Hoy)
        fecha_seleccionada = parse_date(fecha_str) if fecha_str else date.today()
        context['selected_fecha'] = fecha_seleccionada.strftime('%Y-%m-%d')

        context['selected_ciclo'] = int(ciclo_id) if ciclo_id else None
        context['selected_curso'] = int(curso_id) if curso_id else None
        context['selected_turno'] = int(turno_id) if turno_id else None
        context['selected_burbuja'] = int(burbuja_id) if burbuja_id else None
        context['selected_grupo_taller'] = grupo_taller if grupo_taller else None

        # Las burbujas se filtran de forma dinámica en base al ciclo lectivo seleccionado
        if context['selected_ciclo']:
            context['burbujas'] = Burbuja.objects.filter(ciclo_lectivo_id=ciclo_id)
        else:
            context['burbujas'] = []

        # Solo renderizamos si los parámetros obligatorios mínimos están presentes
        if ciclo_id and curso_id and turno_id:
            # Construcción del QuerySet base de Historiales Académicos activos ("CURSANDO")
            queryset_inscripciones = HistorialAcademico.objects.filter(
                ciclo_lectivo_id=ciclo_id,
                curso_id=curso_id,
                estado_final='CURSANDO'
            ).select_related('alumno__persona')

            # Aplicación de filtros opcionales (Burbuja y Grupo de Taller)
            if burbuja_id:
                queryset_inscripciones = queryset_inscripciones.filter(burbuja_id=burbuja_id)
            if grupo_taller:
                queryset_inscripciones = queryset_inscripciones.filter(grupo_taller=grupo_taller)

            inscripciones = queryset_inscripciones.order_by('alumno__persona__apellido', 'alumno__persona__nombre')

            # Recuperar asistencias ya registradas para esta combinación exacta de Fecha y Turno
            asistencias_existentes = Asistencia.objects.filter(
                fecha=fecha_seleccionada,
                turno_id=turno_id,
                inscripcion__in=inscripciones
            ).values_list('inscripcion_id', 'estado', 'burbuja_sesion_id', 'id')

            # Mapeo posicional indexado en memoria: {inscripcion_id: {datos_asistencia}}
            asistencias_dict = {
                a[0]: {'estado': a[1], 'burbuja_sesion_id': a[2], 'asistencia_id': a[3]} 
                for a in asistencias_existentes
            }

            matriz_alumnos = []
            for insc in inscripciones:
                registro = asistencias_dict.get(insc.id)
                matriz_alumnos.append({
                    'inscripcion': insc,
                    'asistencia': registro  # Contiene estado, burbuja_sesion_id, etc. o None si no se tomó lista
                })

            context['matriz_alumnos'] = matriz_alumnos
            context['estados_choices'] = Asistencia.EstadoAsistencia.choices

        return context

    def post(self, request, *args, **kwargs):
        ciclo_id = request.GET.get('ciclo')
        curso_id = request.GET.get('curso')
        turno_id = request.GET.get('turno')
        burbuja_id = request.GET.get('burbuja')
        grupo_taller = request.GET.get('grupo_taller')
        fecha_str = request.GET.get('fecha') or str(date.today())
        fecha_obj = parse_date(fecha_str)

        if not ciclo_id or not curso_id or not turno_id or not fecha_obj:
            messages.error(request, "Error crítico: Faltan parámetros estructurales en el envío del Formulario.")
            return redirect(reverse('planilla_preceptor'))

        # Capturar turno y burbuja seleccionada para la sesión por si hay que setearla en masa
        try:
            turno_instancia = Turno.objects.get(id=turno_id)
        except Turno.DoesNotExist:
            messages.error(request, "El turno seleccionado es inválido.")
            return redirect(reverse('planilla_preceptor'))

        burbuja_sesion_instancia = Burbuja.objects.filter(id=burbuja_id).first() if burbuja_id else None

        with transaction.atomic():
            # Barremos el diccionario POST buscando las claves de cada alumno de la fila
            for key, value in request.POST.items():
                if key.startswith('asistencia_insc_'):
                    inscripcion_id = key.replace('asistencia_insc_', '')
                    
                    # update_or_create garantiza que si volvemos a pasar lista sobre el mismo día/turno,
                    # se sobreescriba y actualice el registro anterior en caliente, tal como las notas.
                    Asistencia.objects.update_or_create(
                        inscripcion_id=inscripcion_id,
                        fecha=fecha_obj,
                        turno=turno_instancia,
                        defaults={
                            'estado': value,
                            'registrado_por': request.user if request.user.is_authenticated else None,
                            'burbuja_sesion': burbuja_sesion_instancia
                        }
                    )
            
            messages.success(request, f"Parte diario del {fecha_obj.strftime('%d/%m/%Y')} registrado con éxito para este curso.")

        # Reconstrucción de la URL de redirección con los mismos filtros aplicados para mantener al preceptor en su contexto
        url_retorno = f"{reverse('planilla_preceptor')}?ciclo={ciclo_id}&curso={curso_id}&turno={turno_id}"
        if burbuja_id:
            url_retorno += f"&burbuja={burbuja_id}"
        if grupo_taller:
            url_retorno += f"&grupo_taller={grupo_taller}"
        url_retorno += f"&fecha={fecha_str}"

        return redirect(url_retorno)

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

