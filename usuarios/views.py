from django.views import View
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

from django.db.models import Count, Avg

import json

from gestion_academica.models import NotaEtapa, Asistencia, Especialidad, HistorialAcademico, CicloLectivo

from .models import User

# --------------------------------------------------------------------------------------
# ---                                   HomeView                                     ---
# --------------------------------------------------------------------------------------

class HomeView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, *args, **kwargs):

        # Administradores del sistema
        if request.user.is_active and request.user.is_staff:
            return redirect('dashboard_staff')

        # Profesor
        if request.user.user_type == User.TipoUsuario.PROFESOR:
            return redirect('dashboard_profesor')

        # Preceptor
        if request.user.user_type == User.TipoUsuario.PRECEPTOR:
            return redirect('dashboard_preceptor')

        # Personal no docente
        if request.user.user_type == User.TipoUsuario.PERNODOC:
            return redirect('dashboard_pernodoc')

        # Cargos
        if request.user.user_type == User.TipoUsuario.CARGOS:
            return redirect('dashboard_cargos')

        # Jerárquicos
        if request.user.user_type == User.TipoUsuario.JERARQUICOS:
            return redirect('dashboard_jerarquicos')

        # Alumnos
        if request.user.user_type == User.TipoUsuario.ALUMNO:
            return redirect('dashboard_alumno')

        # Si no coincide con ningún perfil
        return redirect('login')


# --------------------------------------------------------------------------------------
# ---                               DashboardStaffView                               ---
# --------------------------------------------------------------------------------------

class DashboardStaffView(View):
    def get(self, request):
        # Obtenemos el ciclo lectivo activo
        ciclo_activo = CicloLectivo.objects.filter(activo=True).first()
        
        # 1. Trayectorias: Contamos TEA, TEP, TED
        # Filtramos por ciclo lectivo para asegurar datos actuales
        tray_stats = NotaEtapa.objects.filter(dictado__ciclo_lectivo=ciclo_activo)\
            .values('valor_conceptual').annotate(total=Count('id'))
        
        tea = next((item['total'] for item in tray_stats if item['valor_conceptual'] == 'TEA'), 0)
        tep = next((item['total'] for item in tray_stats if item['valor_conceptual'] == 'TEP'), 0)
        ted = next((item['total'] for item in tray_stats if item['valor_conceptual'] == 'TED'), 0)

        # 2. Ausentismo: Contamos asistencias 'A' por nivel
        aus_stats = Asistencia.objects.filter(inscripcion__ciclo_lectivo=ciclo_activo, estado='A') \
            .values('inscripcion__curso__nivel') \
            .annotate(total=Count('id'))
        
        ausentismo = [0] * 7
        for item in aus_stats:
            nivel = item['inscripcion__curso__nivel']
            if nivel and 1 <= nivel <= 7:
                ausentismo[nivel-1] = item['total']

        # 3. Notas: Promedio de valor_numerico por etapa
        # Filtramos y agrupamos. El .order_by no afecta el orden del diccionario, pero es buena práctica
        notas_stats = NotaEtapa.objects.filter(dictado__ciclo_lectivo=ciclo_activo)\
            .values('etapa').annotate(prom=Avg('valor_numerico'))
        
        # Mapeo estricto para evitar el problema del "undefined" o desorden
        # Indices: 0='1C', 1='2C', 2='FINAL'
        mapping = {'1C': 0, '2C': 1, 'FINAL': 2}
        notas = [0.0, 0.0, 0.0]
        
        for item in notas_stats:
            etapa = item['etapa']
            # Usamos or 0.0 por si el promedio fuera None en la DB
            promedio = float(item['prom'] or 0.0)
            if etapa in mapping:
                notas[mapping[etapa]] = round(promedio, 2)

        # 4. Especialidades: Contamos alumnos activos por especialidad
        esp_stats = HistorialAcademico.objects.filter(ciclo_lectivo=ciclo_activo)\
            .values('curso__especialidad__nombre') \
            .annotate(total=Count('alumno', distinct=True))
        
        esp_nombres = [item['curso__especialidad__nombre'] for item in esp_stats if item['curso__especialidad__nombre']]
        esp_valores = [item['total'] for item in esp_stats if item['curso__especialidad__nombre']]

        # Contexto final para el template
        context = {
            'datos_dashboard': {
                'trayectorias': json.dumps([tea, tep, ted]),
                'ausentismo': json.dumps(ausentismo),
                'notas': json.dumps(notas),
                'especialidades_nombres': json.dumps(esp_nombres),
                'especialidades_valores': json.dumps(esp_valores)
            }
        }
        return render(request, 'usuarios/dashboard_staff.html', context)    
    
# --------------------------------------------------------------------------------------
# ---                            DashboardProfesorView                               ---
# --------------------------------------------------------------------------------------

class DashboardProfesorView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'usuarios/dashboard_profesor.html')

# --------------------------------------------------------------------------------------
# ---                            DashboardPreceptorView                              ---
# --------------------------------------------------------------------------------------

class DashboardPreceptorView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'usuarios/dashboard_preceptor.html')
    
# --------------------------------------------------------------------------------------
# ---                            DashboardPernodocView                              ---
# --------------------------------------------------------------------------------------

class DashboardPernodocView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'usuarios/dashboard_pernodoc.html')

# --------------------------------------------------------------------------------------
# ---                            DashboardJerarquicosView                            ---
# --------------------------------------------------------------------------------------

class DashboardJerarquicosView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'usuarios/dashboard_jerarquicos.html')

# --------------------------------------------------------------------------------------
# ---                            DashboardAlumnoView                                 ---
# --------------------------------------------------------------------------------------

class DashboardAlumnoView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'usuarios/dashboard_alumno.html')

# --------------------------------------------------------------------------------------
# ---                            DashboardCargosView                                 ---
# --------------------------------------------------------------------------------------    

class DashboardCargosView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'usuarios/dashboard_cargos.html')

# --------------------------------------------------------------------------------------
# ---                                   PerfilView                                   ---
# --------------------------------------------------------------------------------------
    
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