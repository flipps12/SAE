# gestion_academica/views/planilla_docente.py
from django.views.generic import TemplateView
from django.db import transaction
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.dateparse import parse_date
from django.contrib import messages
from datetime import date

from gestion_academica.models import (
    InscripcionDictado, CicloLectivo, Curso, Dictado, 
    NotaActividad, NotaEtapa, Intensificacion
)

class PlanillaCargaNotasView(TemplateView):
    template_name = 'calificaciones/planilla_docente.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['ciclos'] = CicloLectivo.objects.all().order_by('-anio')
        context['cursos'] = Curso.objects.all()
        
        ciclo_id = self.request.GET.get('ciclo')
        curso_id = self.request.GET.get('curso')
        dictado_id = self.request.GET.get('dictado')

        context['selected_ciclo'] = int(ciclo_id) if ciclo_id else None
        context['selected_curso'] = int(curso_id) if curso_id else None
        context['selected_dictado'] = int(dictado_id) if dictado_id else None

        if context['selected_curso']:
            context['dictados'] = Dictado.objects.filter(curso_id=curso_id).select_related('materia')
        else:
            context['dictados'] = []

        if ciclo_id and curso_id and dictado_id:
            inscripciones = InscripcionDictado.objects.filter(
                dictado_id=dictado_id,
                ciclo_lectivo_id=ciclo_id
            ).select_related('alumno__persona').order_by('alumno__persona__apellido', 'alumno__persona__nombre')

            notas_existentes = NotaActividad.objects.filter(dictado_id=dictado_id).order_by('fecha', 'id')
            etapas_existentes = NotaEtapa.objects.filter(dictado_id=dictado_id).order_by('etapa')
            
            # Traemos TODAS las intensificaciones del dictado ordenadas cronológicamente e ID
            intensificaciones_existentes = Intensificacion.objects.filter(dictado_id=dictado_id).order_by('fecha', 'id')

            # 1. Cabeceras de Actividades
            actividades_cabecera = []
            seen_actividades = set()
            for n in notas_existentes:
                if n.nombre_actividad not in seen_actividades:
                    actividades_cabecera.append({'nombre': n.nombre_actividad, 'cuatrimestre': n.cuatrimestre})
                    seen_actividades.add(n.nombre_actividad)
            
            # 2. Cabeceras de Etapas
            etapas_cabecera = []
            seen_etapas = set()
            for e in etapas_existentes:
                if e.etapa not in seen_etapas:
                    etapas_cabecera.append(e.etapa)
                    seen_etapas.add(e.etapa)

            # 3. GENERAR MÚLTIPLES CABECERAS DE INTENSIFICACIÓN POR FECHA E ÍNDICE
            # Buscamos cuál es el máximo de notas que llegó a tener un solo alumno en una misma fecha
            # para saber cuántas columnas dibujar de esa fecha.
            conteo_por_alumno_fecha = {} 
            for i in intensificaciones_existentes:
                key = (i.alumno_id, i.fecha)
                conteo_por_alumno_fecha[key] = conteo_por_alumno_fecha.get(key, 0) + 1

            max_subcolumnas_por_fecha = {} # {fecha: max_cantidad}
            for (alumno_id, fch), cantidad in conteo_por_alumno_fecha.items():
                if cantidad > max_subcolumnas_por_fecha.get(fch, 0):
                    max_subcolumnas_por_fecha[fch] = cantidad

            # Armamos las cabeceras reales de Intensificación ordenadas por fecha
            intensificaciones_cabecera = []
            fechas_unicas_ordenadas = sorted(list(set(i.fecha for i in intensificaciones_existentes if i.fecha)))
            
            for fch in fechas_unicas_ordenadas:
                total_columnas_ese_dia = max_subcolumnas_por_fecha.get(fch, 1)
                for index in range(total_columnas_ese_dia):
                    intensificaciones_cabecera.append({
                        'fecha_obj': fch,
                        'str_cabecera': fch.strftime('%d/%m/%Y'),
                        'indice': index
                    })

            context['actividades_cabecera'] = actividades_cabecera
            context['etapas_cabecera'] = etapas_cabecera
            context['intensificaciones_cabecera'] = intensificaciones_cabecera
            context['today'] = date.today()

            # Matriz de alumnos
            matriz_alumnos = []
            for ins in inscripciones:
                alumno = ins.alumno
                
                # Celdas Actividades
                columnas_actividades = []
                for act in actividades_cabecera:
                    nota_obj = notas_existentes.filter(alumno_id=alumno.id, nombre_actividad=act['nombre']).first()
                    columnas_actividades.append({
                        'id': nota_obj.id if nota_obj else None,
                        'valor': nota_obj.valor if nota_obj else '',
                        'identificador_vacio': f"{alumno.id}__act__{act['nombre'].replace(' ', '_')}"
                    })

                # Celdas Etapas
                columnas_etapas = []
                for etapa_nombre in etapas_cabecera:
                    etapa_obj = etapas_existentes.filter(alumno_id=alumno.id, etapa=etapa_nombre).first()
                    columnas_etapas.append({
                        'id': etapa_obj.id if etapa_obj else None,
                        'valor_numerico': etapa_obj.valor_numerico if etapa_obj else '',
                        'identificador_vacio': f"{alumno.id}__etapa__{etapa_nombre.replace(' ', '_')}"
                    })

                # Celdas Intensificación: Mapeamos de forma posicional las notas que tiene el alumno en esa fecha
                columnas_intensificaciones = []
                for cabecera in intensificaciones_cabecera:
                    fch = cabecera['fecha_obj']
                    idx = cabecera['indice']
                    
                    # Traemos las notas de este alumno en este día y tomamos la correspondiente al índice
                    notas_alumno_fecha = intensificaciones_existentes.filter(alumno_id=alumno.id, fecha=fch)
                    
                    inte_obj = None
                    if idx < len(notas_alumno_fecha):
                        inte_obj = notas_alumno_fecha[idx]

                    columnas_intensificaciones.append({
                        'id': inte_obj.id if inte_obj else None,
                        'valor': int(inte_obj.valor) if inte_obj and inte_obj.valor is not None else '',
                        # Identificador en caso de estar vacío para completarlo en caliente
                        'identificador_vacio': f"{alumno.id}__inte__{fch.strftime('%Y-%m-%d')}__idx__{idx}"
                    })

                matriz_alumnos.append({
                    'alumno': alumno,
                    'notas_columnas': columnas_actividades,
                    'etapas_columnas': columnas_etapas,
                    'intensificaciones_columnas': columnas_intensificaciones
                })

            context['matriz_alumnos'] = matriz_alumnos

        return context

    def post(self, request, *args, **kwargs):
        ciclo_id = request.GET.get('ciclo')
        curso_id = request.GET.get('curso')
        dictado_id = request.GET.get('dictado')

        if not dictado_id:
            return redirect(reverse('planilla_docente'))

        nueva_actividad_nombre = request.POST.get('nuevo_nombre_actividad')
        nuevo_cuatrimestre = request.POST.get('nuevo_cuatrimestre')
        
        # Fecha seleccionada por el docente para añadir una nueva columna de intensificación
        nueva_fecha_intensificacion_str = request.POST.get('nueva_fecha_intensificacion')

        with transaction.atomic():
            # ---- A. PROCESAR MODIFICACIONES Y CELDAS RELLENADAS ----
            for key, value in request.POST.items():
                if value.strip() == '':
                    continue

                # Modificar Actividad Ordinaria
                if key.startswith('nota_existente_'):
                    NotaActividad.objects.filter(id=key.replace('nota_existente_', '')).update(valor=int(value))
                
                # Rellenar Celda de Actividad Ordinaria Vacía
                elif key.startswith('nota_nueva_celda_'):
                    info = key.replace('nota_nueva_celda_', '').split('__act__')
                    alumno_id, act_nombre = info[0], info[1].replace('_', ' ')
                    act_prev = NotaActividad.objects.filter(dictado_id=dictado_id, nombre_actividad=act_nombre).first()
                    NotaActividad.objects.create(
                        dictado_id=dictado_id, alumno_id=alumno_id, nombre_actividad=act_nombre,
                        cuatrimestre=act_prev.cuatrimestre if act_prev else 1, valor=int(value),
                        fecha=act_prev.fecha if act_prev else date.today()
                    )

                # Modificar Nota de Etapa
                elif key.startswith('etapa_existente_'):
                    NotaEtapa.objects.filter(id=key.replace('etapa_existente_', '')).update(valor_numerico=int(value))
                
                # Rellenar Celda de Etapa Vacía
                elif key.startswith('etapa_nueva_celda_'):
                    info = key.replace('etapa_nueva_celda_', '').split('__etapa__')
                    NotaEtapa.objects.create(dictado_id=dictado_id, alumno_id=info[0], etapa=info[1].replace('_', ' '), valor_numerico=int(value))

                # EDITAR INTENSIFICACIÓN EXISTENTE (Cualquiera de las filas o subcolumnas repetidas)
                elif key.startswith('intensificacion_existente_'):
                    inte_id = key.replace('intensificacion_existente_', '')
                    Intensificacion.objects.filter(id=inte_id).update(valor=float(value))

                # RELLENAR UNA CELDA VACÍA EN UNA COLUMNA DE FECHA YA EXISTENTE
                elif key.startswith('intensificacion_nueva_celda_'):
                    info = key.replace('intensificacion_nueva_celda_', '').split('__inte__')
                    alumno_id = info[0]
                    fecha_columna = parse_date(info[1].split('__idx__')[0])
                    
                    Intensificacion.objects.create(
                        dictado_id=dictado_id, alumno_id=alumno_id,
                        valor=float(value), fecha=fecha_columna
                    )

            # ---- B. ALTA DE NUEVA COLUMNA DE ACTIVIDAD ORDINARIA ----
            if nueva_actividad_nombre and nueva_actividad_nombre.strip():
                nombre_limpio = nueva_actividad_nombre.strip()
                fecha_carga = parse_date(request.POST.get('nueva_fecha_actividad')) or date.today()
                for k, val in request.POST.items():
                    if k.startswith('nueva_nota_alumno_') and val.strip() != '':
                        NotaActividad.objects.create(
                            dictado_id=dictado_id, alumno_id=k.replace('nueva_nota_alumno_', ''),
                            nombre_actividad=nombre_limpio, cuatrimestre=int(nuevo_cuatrimestre),
                            valor=int(val), fecha=fecha_carga
                        )

            # ---- C. CREAR NUEVA COLUMNA DE INTENSIFICACIÓN (ALTA POR FECHA) ----
            if nueva_fecha_intensificacion_str:
                fecha_int_nueva = parse_date(nueva_fecha_intensificacion_str)
                if fecha_int_nueva:
                    contador_altas = 0
                    for k, val in request.POST.items():
                        if k.startswith('nueva_intensificacion_alumno_') and val.strip() != '':
                            alumno_id = k.replace('nueva_intensificacion_alumno_', '')
                            Intensificacion.objects.create(
                                dictado_id=dictado_id,
                                alumno_id=alumno_id,
                                valor=float(val),
                                fecha=fecha_int_nueva
                            )
                            contador_altas += 1
                    if contador_altas > 0:
                        messages.success(request, f"Nueva columna de intensificación registrada para el día {fecha_int_nueva.strftime('%d/%m/%Y')}.")

        return redirect(f"{reverse('planilla_docente')}?ciclo={ciclo_id}&curso={curso_id}&dictado={dictado_id}")