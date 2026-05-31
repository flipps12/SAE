from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from .models import User

from gestion_academica.models import Alumno, Profesor, Preceptor, Curso, Asistencia

class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'usuarios/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Conteo de Alumnos Activos
        context['total_alumnos'] = Alumno.objects.filter(activo=True).count()
        
        # Conteo de Profesores y Preceptores (desde gestion_academica)
        context['total_profesores'] = Profesor.objects.count()
        context['total_preceptores'] = Preceptor.objects.count()
        
        # Total de Divisiones / Cursos creados
        context['total_cursos'] = Curso.objects.count()
        
        # Métrica diaria: asistencias tomadas hoy (30/05/2026)
        hoy = timezone.now().date()
        context['asistencias_hoy'] = Asistencia.objects.filter(fecha=hoy).count()
        
        # Extra: Podés contar cuántos usuarios de cada tipo hay en auth si querés cruzar datos
        # context['total_usuarios_alumnos'] = User.objects.filter(user_type=User.TipoUsuario.ALUMNO).count()
        
        return context
   
class PerfilView(LoginRequiredMixin, View):
    def get(self, request):
        password_form = PasswordChangeForm(request.user)
        return render(request, 'usuarios/perfil.html', {
            'user': request.user,
            'password_form': password_form
        })
    
    def post(self, request):
        if 'editar_perfil' in request.POST:
            request.user.first_name = request.POST.get('first_name')
            request.user.last_name = request.POST.get('last_name')
            request.user.email = request.POST.get('email')
            request.user.save()
            messages.success(request, 'Perfil actualizado')
            return redirect('perfil')
        
        elif 'cambiar_password' in request.POST:
            form = PasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Contraseña actualizada')
                return redirect('perfil')
        
        return redirect('perfil')
    
