from django import forms
from django.core.exceptions import ValidationError

from .models import Alumno, Persona, Curso, Burbuja, CicloLectivo, HistorialAcademico

# --------------------------------------------------------------------------------------
# ---                           Form ImportarAlumnos                                 ---
# --------------------------------------------------------------------------------------

class ImportarAlumnosForm(forms.Form):
    archivo_excel = forms.FileField(
        label="Seleccionar archivo Excel",
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.xlsx'})
    )

    def clean_archivo_excel(self):
        archivo = self.cleaned_data.get('archivo_excel')
        if archivo and not archivo.name.endswith('.xlsx'):
            raise ValidationError("El archivo debe tener la extensión obligatoria .xlsx")
        return archivo
    
# --------------------------------------------------------------------------------------
# ---                                Form Persona                                    ---
# --------------------------------------------------------------------------------------

class PersonaForm(forms.ModelForm):
    class Meta:
        model = Persona
        fields = [
            'nombre', 'apellido', 'dni', 'cuil', 
            'fecha_nacimiento', 'fecha_ingreso', 
            'numero_legajo', 'email', 'telefono', 'domicilio'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'dni': forms.TextInput(attrs={'class': 'form-control'}),
            'cuil': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_ingreso': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'numero_legajo': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'domicilio': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

# --------------------------------------------------------------------------------------
# ---                                Form Alumno                                     ---
# --------------------------------------------------------------------------------------

from django import forms
from .models import Alumno, Curso, Burbuja, CicloLectivo, HistorialAcademico

class AlumnoForm(forms.ModelForm):
    # 1. Agregamos los campos artificiales al formulario
    curso = forms.ModelChoiceField(
        queryset=Curso.objects.all(),
        required=True,
        label="Curso / División",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    burbuja = forms.ModelChoiceField(
        queryset=Burbuja.objects.none(), # Se llena dinámicamente según el ciclo activo
        required=False,
        label="Burbuja (Opcional)",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    grupo_taller = forms.ChoiceField(
        choices=[('', 'Sin asignar'), ('A', 'Grupo A'), ('B', 'Grupo B')],
        required=False,
        label="Grupo de Taller",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Alumno
        fields = ['libro', 'folio', 'activo']
        # Si usás widgets para libro/folio, los dejás acá abajo...

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 2. Buscamos el ciclo lectivo que esté marcado como activo
        ciclo_activo = CicloLectivo.objects.filter(activo=True).first()
        
        if ciclo_activo:
            # Filtramos las burbujas para que solo muestre las de este año
            self.fields['burbuja'].queryset = Burbuja.objects.filter(ciclo_lectivo=ciclo_activo)
            
            # 3. Si estamos editando un alumno existente, buscamos su curso actual
            if self.instance and self.instance.pk:
                historial = HistorialAcademico.objects.filter(
                    alumno=self.instance, 
                    ciclo_lectivo=ciclo_activo
                ).first()
                
                # Si encontramos su inscripción, precargamos los selectores en la pantalla
                if historial:
                    self.fields['curso'].initial = historial.curso
                    self.fields['burbuja'].initial = historial.burbuja
                    self.fields['grupo_taller'].initial = historial.grupo_taller

