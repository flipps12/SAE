# gestion_academica/views/cursos.py
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from django.urls import reverse

from gestion_academica.models import Curso, Especialidad, Turno, Aula
from gestion_academica.forms import CursoForm

class GestionCursosView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = 'cursos/gestion_cursos.html'

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