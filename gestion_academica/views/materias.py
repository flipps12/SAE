# gestion_academica/views/materias.py
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from django.urls import reverse

from gestion_academica.models import Materia
from gestion_academica.forms import MateriaForm

class GestionMateriasView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = 'materias/gestion_materias.html'

    def has_permission(self):
        # Mantenemos tu regla estricta de seguridad (Personal de Staff activo)
        return self.request.user.is_active and self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Traemos las materias optimizando con select_related
        context['materias'] = Materia.objects.select_related('especialidad').order_by('nombre')
        # Formulario vacío listo para el modal de alta
        context['form'] = MateriaForm()
        return context

    def post(self, request, *args, **kwargs):
        materia_id = request.POST.get('materia_id')
        
        if materia_id:
            # --- MODO: MODIFICACIÓN ---
            materia = get_object_or_404(Materia, id=materia_id)
            form = MateriaForm(request.POST, instance=materia)
            accion_str = "actualizada"
        else:
            # --- MODO: ALTA ---
            form = MateriaForm(request.POST)
            accion_str = "creada"

        if form.is_valid():
            try:
                materia_guardada = form.save()
                messages.success(request, f"Materia '{materia_guardada.nombre}' {accion_str} con éxito.")
            except Exception as e:
                messages.error(request, f"Error de integridad en base de datos: {str(e)}")
        else:
            for field, errores in form.errors.items():
                for error in errores:
                    messages.error(request, f"Error en campo [{field}]: {error}")

        return redirect(reverse('gestion_materias'))