from django.views.generic import ListView, FormView
from django.db.models import Q
from django.urls import reverse_lazy
# from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin

from gestion_academica.models import Profesor
from gestion_academica.forms import AltaProfesorForm


class ProfesorListView(ListView):
    model = Profesor
    template_name = 'profesores/listado_profesor.html'
    context_object_name = 'profesores'
    ordering = ['persona__apellido', 'persona__nombre']
    
    def get_queryset(self):
        queryset = Profesor.objects.select_related('persona').order_by(*self.ordering)
        query = self.request.GET.get('q')
        
        if query:
            # Buscamos coincidencias en los datos de la Persona vinculada
            queryset = queryset.filter(
                Q(persona__nombre__icontains=query) |
                Q(persona__apellido__icontains=query) |
                Q(persona__dni__icontains=query) |
                Q(persona__numero_legajo__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Devolvemos la query al template para que el input no se vacíe al presionar "Filtrar"
        context['search_query'] = self.request.GET.get('q', '')
        return context

class AltaProfesorView(FormView):
    template_name = 'profesores/alta_profesor.html'
    form_class = AltaProfesorForm
    # Al usar reverse_lazy, no se evalúa la ruta hasta que se redirija efectivamente
    success_url = reverse_lazy('listado_profesor')

    def form_valid(self, form):
        # Ejecuta el método save() transaccional que armamos en el Form
        form.save()
        return super().form_valid(form)