# gestion_academica/views/cargos.py
from django.views.generic import ListView, FormView
from django.urls import reverse_lazy
from django.db.models import Q
from gestion_academica.models.actores import PersonalCargo
from gestion_academica.forms import AltaPersonalCargoForm

class ListaCargosView(ListView):
    model = PersonalCargo
    template_name = 'cargos/lista_cargos.html'
    context_object_name = 'personal_con_cargos'
    ordering = ['persona__apellido', 'persona__nombre']

    def get_queryset(self):
        # Prefetch optimizado evitando consultas duplicadas N+1 en el bucle del template
        queryset = PersonalCargo.objects.select_related('persona').prefetch_related(
            'asignaciones__cargo'
        ).filter(asignaciones__activo=True).order_by(*self.ordering).distinct()

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
        context['search_query'] = self.request.GET.get('q', '')
        return context


class AltaPersonalCargoView(FormView):
    template_name = 'cargos/alta_cargos.html'
    form_class = AltaPersonalCargoForm
    # Cambiar por 'lista_cargos' a secas si removiste la insulación de namespaces globales
    success_url = reverse_lazy('lista_cargos')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)