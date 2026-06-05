from django.views.generic import ListView, CreateView
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin

from gestion_academica.models import Comunicado
from gestion_academica.forms import ComunicadoForm

User = get_user_model()

class TablonComunicadosView(LoginRequiredMixin, ListView):
    model = Comunicado
    template_name = 'comunicados/lista_comunicados.html'  # Tu template real
    context_object_name = 'comunicados'
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        filtros = Q(visibilidad=Comunicado.VisibilidadChoices.GLOBAL)

        if user.user_type == 'ALUMNO':
            filtros |= Q(visibilidad=Comunicado.VisibilidadChoices.ESTUDIANTES)
        elif user.user_type in ['PROFESOR', 'PRECEPTOR', 'JERARQUICOS', 'CARGOS']:
            filtros |= Q(visibilidad=Comunicado.VisibilidadChoices.DOCENTES)
            filtros |= Q(visibilidad=Comunicado.VisibilidadChoices.ESTUDIANTES)

        return Comunicado.objects.filter(filtros)


class CrearComunicadoView(LoginRequiredMixin, CreateView):
    model = Comunicado
    form_class = ComunicadoForm
    template_name = 'comunicados/carga_comunicados.html'  # Tu template real

    def get_success_url(self):
        # Redirige de forma dinámica usando reverse común una vez procesado con éxito
        return reverse('lista_comunicados')

    def dispatch(self, request, *args, **kwargs):
        if request.user.user_type == 'ALUMNO':
            messages.error(request, "No tenés permisos para publicar comunicados.")
            return redirect('lista_comunicados')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.autor = self.request.user
        messages.success(self.request, "Comunicado publicado de manera exitosa.")
        return super().form_valid(form)