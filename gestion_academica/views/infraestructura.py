# gestion_academica/views/infraestructura.py
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from django.urls import reverse

from gestion_academica.models import Curso, Especialidad, Turno, Aula, Especialidad
from gestion_academica.forms import CursoForm, TurnoForm, EspecialidadForm, AulaForm

class GestionCursosView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = 'infraestructura/gestion_cursos.html'

    def has_permission(self):
        # Mantenemos tu regla estricta de seguridad institucional (solo personal de Staff)
        return self.request.user.is_active and self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Traemos la base de cursos optimizando queries
        context['cursos'] = Curso.objects.select_related('especialidad').order_by('nivel', 'division')
        
        # Formulario vacío listo para el modal de creación
        context['form'] = CursoForm()
        return context

    def post(self, request, *args, **kwargs):
        # Determinamos si es una edición o una creación mediante la presencia de curso_id
        curso_id = request.POST.get('curso_id')
        
        if curso_id:
            # --- MODO: MODIFICACIÓN ---
            curso = get_object_or_404(Curso, id=curso_id)
            form = CursoForm(request.POST, instance=curso)
            accion_str = "actualizado"
        else:
            # --- MODO: ALTA NUEVA ---
            form = CursoForm(request.POST)
            accion_str = "registrado"

        if form.is_valid():
            try:
                curso_guardado = form.save()
                messages.success(request, f"Curso {curso_guardado.nivel}° {curso_guardado.division}ª {accion_str} correctamente.")
            except Exception as e:
                messages.error(request, f"Error de integridad al guardar el curso: {str(e)}")
        else:
            # Si hay errores de validación, los exponemos en las alertas globales del sistema
            for field, errores in form.errors.items():
                for error in errores:
                    messages.error(request, f"Error en el campo [{field}]: {error}")

        return redirect(reverse('gestion_cursos'))

class BaseGestionView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    """Clase base para compartir la lógica de permisos del Staff"""
    def has_permission(self):
        return self.request.user.is_active and self.request.user.is_staff

class GestionTurnosView(BaseGestionView):
    template_name = 'infraestructura/gestion_turnos.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['turnos'] = Turno.objects.all().order_by('nombre')
        context['form'] = TurnoForm()
        return context

    def post(self, request, *args, **kwargs):
        turno_id = request.POST.get('turno_id')
        if turno_id:
            turno = get_object_or_404(Turno, id=turno_id)
            form = TurnoForm(request.POST, instance=turno)
            msg = "actualizado"
        else:
            form = TurnoForm(request.POST)
            msg = "creado"

        if form.is_valid():
            form.save()
            messages.success(request, f"Turno {msg} correctamente.")
        else:
            messages.error(request, "Error al procesar el formulario de Turnos.")
        return redirect(reverse('gestion_turnos'))

class GestionEspecialidadesView(BaseGestionView):
    template_name = 'infraestructura/gestion_especialidades.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['especialidades'] = Especialidad.objects.all().order_by('nombre')
        context['form'] = EspecialidadForm()
        return context

    def post(self, request, *args, **kwargs):
        esp_id = request.POST.get('especialidad_id')
        if esp_id:
            especialidad = get_object_or_404(Especialidad, id=esp_id)
            form = EspecialidadForm(request.POST, instance=especialidad)
            msg = "actualizada"
        else:
            form = EspecialidadForm(request.POST)
            msg = "creada"

        if form.is_valid():
            form.save()
            messages.success(request, f"Especialidad {msg} correctamente.")
        else:
            messages.error(request, "Error al procesar el formulario de Especialidades.")
        return redirect(reverse('gestion_especialidades'))

class GestionAulasView(BaseGestionView):
    template_name = 'infraestructura/gestion_aulas.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['aulas'] = Aula.objects.all().order_by('nombre')
        context['form'] = AulaForm()
        return context

    def post(self, request, *args, **kwargs):
        aula_id = request.POST.get('aula_id')
        if aula_id:
            aula = get_object_or_404(Aula, id=aula_id)
            form = AulaForm(request.POST, instance=aula)
            msg = "actualizada"
        else:
            form = AulaForm(request.POST)
            msg = "creada"

        if form.is_valid():
            form.save()
            messages.success(request, f"Aula {msg} correctamente.")
        else:
            messages.error(request, "Error al procesar el formulario de Aulas.")
        return redirect(reverse('gestion_aulas'))