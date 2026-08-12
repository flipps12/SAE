from django import forms
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from django.db import transaction

from .models import Alumno, Persona, Curso, Burbuja, CicloLectivo, HistorialAcademico,Profesor, Dictado, HorarioDictado, AsignacionCargo, PersonalCargo, TipoCargo, Especialidad, Materia, Turno, Aula, Comunicado


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
# ---                         Form ImportarProfesoresForm                            ---
# --------------------------------------------------------------------------------------

class ImportarProfesoresForm(forms.Form):
    archivo_excel = forms.FileField(
        label="Seleccionar archivo Excel",
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.xlsx'})
    )

    def clean_archivo_excel(self):
        archivo = self.cleaned_data.get('archivo_excel')
        # Validación estricta de extensión para evitar archivos corruptos o .xls viejos
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
            'fecha_nacimiento': forms.DateInput(
                format='%Y-%m-%d', 
                attrs={'class': 'form-control', 'type': 'date'}
            ),
            'fecha_ingreso': forms.DateInput(
                format='%Y-%m-%d', 
                attrs={'class': 'form-control', 'type': 'date'}
            ),
            'numero_legajo': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'domicilio': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(PersonaForm, self).__init__(*args, **kwargs)
        # Forzamos el formato de entrada para todos los campos de fecha
        self.fields['fecha_nacimiento'].input_formats = ('%Y-%m-%d',)
        self.fields['fecha_ingreso'].input_formats = ('%Y-%m-%d',)
# --------------------------------------------------------------------------------------
# ---                                Form Alumno                                     ---
# --------------------------------------------------------------------------------------

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
        fields = ['libro', 'folio', 'activo', 'datos_pase']
        
        widgets = {
            'libro': forms.TextInput(attrs={'class': 'form-control'}),
            'folio': forms.TextInput(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input', 'role': 'switch'}),
            'motivo_baja': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Ej: Traslado a la Escuela Técnica N° 1...'
            }),
        }

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
        
        # 4. Configuración para campos de fecha (si agregas alguno en el futuro)
        # Ejemplo: Si tuvieras un campo 'fecha_inscripcion', lo configurarías así:
        # self.fields['fecha_inscripcion'].widget.format = '%Y-%m-%d'
        # self.fields['fecha_inscripcion'].input_formats = ('%Y-%m-%d',)


# --------------------------------------------------------------------------------------
# ---                           Form EditarProfesor                                 ---
# --------------------------------------------------------------------------------------

class ProfesorUpdateForm(forms.ModelForm):
    class Meta:
        model = Profesor
        fields = ['telefono_emergencia']
        widgets = {
            'telefono_emergencia': forms.TextInput(attrs={'class': 'form-control'}),
        }

class DictadoForm(forms.ModelForm):
    class Meta:
        model = Dictado
        fields = [
            'materia', 'curso', 'ciclo_lectivo', 'grupo', 
            'pid', 'cupof', 'secuencia', 'toma_posesion', 
            'forma_ingreso', 'situacion_revista'
        ]
        widgets = {
            'materia': forms.Select(attrs={'class': 'form-control'}),
            'curso': forms.Select(attrs={'class': 'form-control'}),
            'ciclo_lectivo': forms.Select(attrs={'class': 'form-control'}),
            'grupo': forms.Select(attrs={'class': 'form-control'}),
            'pid': forms.TextInput(attrs={'class': 'form-control'}),
            'cupof': forms.NumberInput(attrs={'class': 'form-control'}),
            'secuencia': forms.NumberInput(attrs={'class': 'form-control'}),
            'toma_posesion': forms.DateInput(
                format='%Y-%m-%d', 
                attrs={'class': 'form-control', 'type': 'date'}
            ),
            'forma_ingreso': forms.Select(attrs={'class': 'form-control'}),
            'situacion_revista': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(DictadoForm, self).__init__(*args, **kwargs)
        # Asegura que el formato de entrada sea compatible con el input date
        self.fields['toma_posesion'].input_formats = ('%Y-%m-%d',)

# Formsets
DictadoFormSet = inlineformset_factory(
    Profesor, 
    Dictado, 
    form=DictadoForm, 
    extra=1, 
    can_delete=True
)

HorarioFormSet = inlineformset_factory(
    Dictado, 
    HorarioDictado, 
    fields=('dia_semana', 'horario_inicio', 'horario_fin', 'aula'),
    extra=1, 
    can_delete=True,
    widgets={
        'dia_semana': forms.Select(attrs={'class': 'form-control'}),
        'horario_inicio': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        'horario_fin': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        'aula': forms.Select(attrs={'class': 'form-control'}),
    }
)


# --------------------------------------------------------------------------------------
# ---                           Form AsignacionCargoForm                             ---
# --------------------------------------------------------------------------------------

class AsignacionCargoForm(forms.ModelForm):
    class Meta:
        model = AsignacionCargo
        fields = ['cargo', 'fecha_inicio', 'fecha_fin', 'activo', 'resolucion', 
                  'forma_ingreso', 'situacion_revista', 'pid', 'cupof', 'secuencia']
        widgets = {
            'cargo': forms.Select(attrs={'class': 'form-control'}),
            'fecha_inicio': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_fin': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'resolucion': forms.TextInput(attrs={'class': 'form-control'}),
            'forma_ingreso': forms.Select(attrs={'class': 'form-control'}),
            'situacion_revista': forms.Select(attrs={'class': 'form-control'}),
            'pid': forms.TextInput(attrs={'class': 'form-control'}),
            'cupof': forms.NumberInput(attrs={'class': 'form-control'}),
            'secuencia': forms.NumberInput(attrs={'class': 'form-control'}),
        }


AsignacionCargoFormSet = inlineformset_factory(
    PersonalCargo, 
    AsignacionCargo, 
    form=AsignacionCargoForm,
    extra=1,
    can_delete=True
)

# --------------------------------------------------------------------------------------
# ---                              Form TipoCargoForm                                ---
# --------------------------------------------------------------------------------------


class TipoCargoForm(forms.ModelForm):

    class Meta:
        model = TipoCargo
        fields = [
            "nombre",
            "descripcion",
        ]

        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "descripcion": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                }
            ),
        }


# --------------------------------------------------------------------------------------
# ---                             Form EspecialidadForm                              ---
# --------------------------------------------------------------------------------------


class EspecialidadForm(forms.ModelForm):

    class Meta:
        model = Especialidad
        fields = ["nombre"]

        widgets = {
            "nombre": forms.TextInput(
                attrs={
                    "class": "form-control bg-dark text-white border-secondary",
                    "placeholder": "Nombre de la especialidad",
                }
            ),
        }

# --------------------------------------------------------------------------------------
# ---                               Form CursoForm                                   ---
# --------------------------------------------------------------------------------------

class CursoForm(forms.ModelForm):

    class Meta:
        model = Curso
        fields = ["nivel", "division", "especialidad"]

        widgets = {
            "nivel": forms.NumberInput(attrs={
                "class": "form-control bg-dark text-white border-secondary"
            }),
            "division": forms.NumberInput(attrs={
                "class": "form-control bg-dark text-white border-secondary"
            }),
            "especialidad": forms.Select(attrs={
                "class": "form-select bg-dark text-white border-secondary"
            }),
        }

# --------------------------------------------------------------------------------------
# ---                             Form MateriaForm                                   ---
# --------------------------------------------------------------------------------------

class MateriaForm(forms.ModelForm):
    class Meta:
        model = Materia
        fields = ["nombre", "especialidad", "tipo"]

        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "especialidad": forms.Select(attrs={"class": "form-select"}),
            "tipo": forms.Select(attrs={"class": "form-select"}),
        }

# --------------------------------------------------------------------------------------
# ---                              Form TurnoForm                                    ---
# --------------------------------------------------------------------------------------

class TurnoForm(forms.ModelForm):
    class Meta:
        model = Turno
        fields = ["nombre", "valor_falta"]

        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "valor_falta": forms.NumberInput(attrs={"class": "form-control", "step": "0.1"}),
        }

# --------------------------------------------------------------------------------------
# ---                              Form AulaForm                                     ---
# --------------------------------------------------------------------------------------

class AulaForm(forms.ModelForm):
    class Meta:
        model = Aula
        fields = ["nombre", "capacidad", "tipo", "descripcion"]

        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "capacidad": forms.NumberInput(attrs={"class": "form-control"}),
            "tipo": forms.Select(attrs={"class": "form-select"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

# --------------------------------------------------------------------------------------
# ---                           Form BurbujaForm                                     ---
# --------------------------------------------------------------------------------------

class BurbujaForm(forms.ModelForm):
    class Meta:
        model = Burbuja
        fields = ["nombre", "ciclo_lectivo"]

        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "ciclo_lectivo": forms.Select(attrs={"class": "form-select"}),
        }

# --------------------------------------------------------------------------------------
# ---                           Form CicloLectivoForm                                ---
# --------------------------------------------------------------------------------------

class CicloLectivoForm(forms.ModelForm):
    class Meta:
        model = CicloLectivo
        fields = ["anio", "activo"]

        widgets = {
            "anio": forms.NumberInput(attrs={"class": "form-control"}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

# --------------------------------------------------------------------------------------
# ---                           Form AlumnoFilaForm                                  ---
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

# --------------------------------------------------------------------------------------
# ---                             Form ComunicadoForm                                ---
# --------------------------------------------------------------------------------------

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

# --------------------------------------------------------------------------------------
# ---                         Form AltaPersonalCargoForm                             ---
# --------------------------------------------------------------------------------------

class AltaPersonalCargoForm(forms.Form):
    nombre = forms.CharField(max_length=50, label="Nombre")
    apellido = forms.CharField(max_length=50, label="Apellido")
    dni = forms.CharField(max_length=8, label="DNI")
    cuil = forms.CharField(max_length=11, label="CUIL")
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

            personal_cargo = PersonalCargo.objects.create(persona=persona)

            AsignacionCargo.objects.create(
                persona_cargo=personal_cargo,
                cargo=self.cleaned_data['cargo'],
                fecha_inicio=self.cleaned_data['fecha_inicio'],
                resolucion=self.cleaned_data.get('resolucion', ''),
                activo=True
            )

            return personal_cargo