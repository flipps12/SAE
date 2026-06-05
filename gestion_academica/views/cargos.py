from django.views.generic import ListView
# from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin

from gestion_academica.models import PersonalCargo


class ListaCargosView(ListView):
    model = PersonalCargo
    template_name = 'cargos/lista_cargos.html'
    context_object_name = 'personal_con_cargos'

    def get_queryset(self):
        # Base optimizada de la consulta
        queryset = PersonalCargo.objects.select_related('persona').prefetch_related(
            'asignaciones__cargo'
        ).filter(asignaciones__activo=True).distinct()

        # Capturamos el buscador general 'q'
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(persona__nombre__icontains=query) |
                Q(persona__apellido__icontains=query) |
                Q(persona__cuil__icontains=query) |
                Q(persona__numero_legajo__icontains=query)
            )
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Mantenemos el texto ingresado en el input tras recargar/filtrar
        context['search_query'] = self.request.GET.get('q', '')
        return context