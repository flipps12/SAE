from django import forms
from django.db import transaction
from django.core.exceptions import ValidationError
from .validators import dni_validator, cuil_validator
from .models import Alumno, Persona, Curso, Burbuja, CicloLectivo, HistorialAcademico, Comunicado, Profesor, TipoCargo, PersonalCargo, AsignacionCargo

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


# --------------------------------------------------------------------------------------
# ---                              AlumnoFilaForm                                    ---
# --------------------------------------------------------------------------------------

class AlumnoFilaForm(forms.Form):
    dni = forms.CharField(
        max_length=8,
        widget=forms.TextInput(attrs={'class': 'form-control bg-dark text-white border-secondary', 'placeholder': 'DNI (8 dígitos)'})
    )
    apellido = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control bg-dark text-white border-secondary', 'placeholder': 'Apellido'})
    )
    nombre = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control bg-dark text-white border-secondary', 'placeholder': 'Nombres'})
    )
    numero_legajo = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control bg-dark text-white border-secondary', 'placeholder': 'Legajo (Op.)'})
    )
    libro = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control bg-dark text-white border-secondary', 'placeholder': 'Libro (Op.)'})
    )
    folio = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control bg-dark text-white border-secondary', 'placeholder': 'Folio (Op.)'})
    )

AlumnoFormSet = forms.formset_factory(AlumnoFilaForm, extra=1, min_num=1)

class ComunicadoForm(forms.ModelForm):
    class Meta:
        model = Comunicado
        fields = ['titulo', 'contenido', 'visibilidad']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control bg-dark text-white border-secondary',
                'placeholder': 'Escribí un título claro e institucional...'
            }),
            'contenido': forms.Textarea(attrs={
                'class': 'form-control bg-dark text-white border-secondary',
                'rows': 5,
                'placeholder': 'Desarrollá el cuerpo del comunicado aquí...'
            }),
            'visibilidad': forms.Select(attrs={
                'class': 'form-select bg-dark text-white border-secondary'
            }),
        }


class AltaProfesorForm(forms.Form):
    # Campos de Persona
    nombre = forms.CharField(max_length=50, label="Nombre")
    apellido = forms.CharField(max_length=50, label="Apellido")
    dni = forms.CharField(max_length=8, label="DNI", validators=[dni_validator])
    cuil = forms.CharField(max_length=11, label="CUIL", validators=[cuil_validator])
    numero_legajo = forms.CharField(max_length=30, label="Número de Legajo")
    fecha_nacimiento = forms.DateField(
        required=False, 
        label="Fecha de Nacimiento", 
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    fecha_ingreso = forms.DateField(
        required=False, 
        label="Fecha de Ingreso", 
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    email = forms.EmailField(required=False, label="Email")
    telefono = forms.CharField(max_length=20, required=False, label="Teléfono")
    domicilio = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), required=False, label="Domicilio")
    
    # Campo específico de Profesor
    telefono_emergencia = forms.CharField(max_length=20, required=False, label="Teléfono de Emergencia")

    def clean_dni(self):
        dni = self.cleaned_data.get('dni')
        if Persona.objects.filter(dni=dni).exists():
            raise forms.ValidationError("Ya existe una persona registrada con este DNI.")
        return dni

    def clean_cuil(self):
        cuil = self.cleaned_data.get('cuil')
        if Persona.objects.filter(cuil=cuil).exists():
            raise forms.ValidationError("Ya existe una persona registrada con este CUIL.")
        return cuil

    def clean_numero_legajo(self):
        legajo = self.cleaned_data.get('numero_legajo')
        if Persona.objects.filter(numero_legajo=legajo).exists():
            raise forms.ValidationError("Este número de legajo ya se encuentra asignado.")
        return legajo

    def save(self):
        """
        Guarda de forma atómica tanto la Persona como el Profesor.
        Si algo falla en el camino, se aplica un rollback completo.
        """
        with transaction.atomic():
            # 1. Crear la instancia de Persona
            persona = Persona.objects.create(
                nombre=self.cleaned_data['nombre'],
                apellido=self.cleaned_data['apellido'],
                dni=self.cleaned_data['dni'],
                cuil=self.cleaned_data['cuil'],
                numero_legajo=self.cleaned_data['numero_legajo'],
                fecha_nacimiento=self.cleaned_data.get('fecha_nacimiento'),
                fecha_ingreso=self.cleaned_data.get('fecha_ingreso'),
                email=self.cleaned_data.get('email', ''),
                telefono=self.cleaned_data.get('telefono', ''),
                domicilio=self.cleaned_data.get('domicilio', '')
            )
            
            # 2. Crear el Profesor vinculando la Persona creada
            profesor = Profesor.objects.create(
                persona=persona,
                telefono_emergencia=self.cleaned_data.get('telefono_emergencia', '')
            )
            
            return profesor

class AltaPersonalCargoForm(forms.Form):
    # Campos base de Persona
    nombre = forms.CharField(max_length=50, label="Nombre")
    apellido = forms.CharField(max_length=50, label="Apellido")
    dni = forms.CharField(max_length=8, label="DNI", validators=[dni_validator])
    cuil = forms.CharField(max_length=11, label="CUIL", validators=[cuil_validator])
    numero_legajo = forms.CharField(max_length=30, label="Número de Legajo")
    fecha_nacimiento = forms.DateField(
        required=False, label="Fecha de Nacimiento", widget=forms.DateInput(attrs={'type': 'date'})
    )
    fecha_ingreso = forms.DateField(
        required=False, label="Fecha de Ingreso", widget=forms.DateInput(attrs={'type': 'date'})
    )
    email = forms.EmailField(required=False, label="Email")
    telefono = forms.CharField(max_length=20, required=False, label="Teléfono")
    domicilio = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), required=False, label="Domicilio")
    
    # Datos de la asignación inicial del Cargo
    cargo = forms.ModelChoiceField(
        queryset=TipoCargo.objects.all(), 
        label="Cargo a Asignar",
        empty_label="-- Seleccione un tipo de cargo --"
    )
    fecha_inicio = forms.DateField(
        label="Fecha de Toma de Posesión", 
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    resolucion = forms.CharField(max_length=100, required=False, label="Nro. de Resolución / Disposición")

    def clean_dni(self):
        dni = self.cleaned_data.get('dni')
        if Persona.objects.filter(dni=dni).exists():
            raise forms.ValidationError("Ya existe una persona registrada con este DNI.")
        return dni

    def clean_cuil(self):
        cuil = self.cleaned_data.get('cuil')
        if Persona.objects.filter(cuil=cuil).exists():
            raise forms.ValidationError("Ya existe una persona registrada con este CUIL.")
        return cuil

    def clean_numero_legajo(self):
        legajo = self.cleaned_data.get('numero_legajo')
        if Persona.objects.filter(numero_legajo=legajo).exists():
            raise forms.ValidationError("Este número de legajo ya se encuentra asignado.")
        return legajo

    def save(self):
        with transaction.atomic():
            # 1. Creamos la instancia de Persona
            persona = Persona.objects.create(
                nombre=self.cleaned_data['nombre'],
                apellido=self.cleaned_data['apellido'],
                dni=self.cleaned_data['dni'],
                cuil=self.cleaned_data['cuil'],
                numero_legajo=self.cleaned_data['numero_legajo'],
                fecha_nacimiento=self.cleaned_data.get('fecha_nacimiento'),
                fecha_ingreso=self.cleaned_data.get('fecha_ingreso'),
                email=self.cleaned_data.get('email', ''),
                telefono=self.cleaned_data.get('telefono', ''),
                domicilio=self.cleaned_data.get('domicilio', '')
            )
            
            # 2. Creamos el perfil contenedor para cargos (OneToOne con Persona)
            personal_cargo = PersonalCargo.objects.create(persona=persona)
            
            # 3. Creamos la relación intermedia de la asignación del cargo específico
            AsignacionCargo.objects.create(
                persona_cargo=personal_cargo,
                cargo=self.cleaned_data['cargo'],
                fecha_inicio=self.cleaned_data['fecha_inicio'],
                resolucion=self.cleaned_data.get('resolucion', ''),
                activo=True
            )
            
            return personal_cargo