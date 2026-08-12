<h1 align='center'>SAE2026</h1>

### Clonar repositorio

```
git clone https://github.com/flipps12/SAE
cd SAE
```

### Crear entorno virtual y descargar dependencias

```
python -m venv venv

# GNU/Linux
source venv/bin/activate

# Windows (PowerShell)
.\\venv\\Scripts\\Activate.ps1

# Windows (CMD)
.\\venv\\Scripts\\activate.bat


pip install --upgrade pip
pip install -r requirements.txt

```

### Configuracion
```
# Copiar archivo .env
cp .env.example .env

# Crear Database
python manage.py migrate

# Crear super usuario
python manage.py createsuperuser

```

### Ejecutar server

```
python manage.py runserver
```

### Actualizar repositorio

```
git checkout main
git pull origin main
```
