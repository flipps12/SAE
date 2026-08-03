from django.core.validators import RegexValidator

# Validador para DNI: Solo números, entre 7 y 8 dígitos (estándar argentino)
dni_validator = RegexValidator(
    regex=r'^\d{7,8}$',
    message="El DNI debe tener entre 7 y 8 dígitos numéricos, sin puntos ni espacios."
)

# Validador para CUIL: Formato XX-XXXXXXXX-X
cuil_validator = RegexValidator(
    regex=r'^\d{11}$',
    message="El CUIL debe tener 11 dígitos numéricos sin guiones."
)