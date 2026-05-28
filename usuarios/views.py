from django.views import View
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

class HomeView(View):
    def get(self, request):
        return render(request, 'usuarios/home.html')
    
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