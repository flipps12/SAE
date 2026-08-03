# AGENTS.md

Contexto para trabajar en **SAE26** (Sistema de Administración Escolar).

## Stack

- Django 6.0.4 + SQLite (`db.sqlite3`)
- Python 3, entorno virtual en `venv/`
- Frontend: templates Django + Bootstrap + JS/CSS estáticos en `usuarios/static/`
- Importación de Excel con `openpyxl` (plantillas en `usuarios/static/imports/`)

## Estructura

- `SAE26/` — config del proyecto (`settings.py`, `urls.py`)
- `usuarios/` — app de autenticación: `User` (custom), dashboards por rol, `base.html`, navbars, CSS/JS globales
- `gestion_academica/` — dominio académico:
  - `models.py` — todos los modelos en un solo archivo
  - `views.py` — todas las vistas (CBV) en un solo archivo
  - `forms.py`, `admin.py`, `urls.py`
  - `templates/<dominio>/` — templates organizados por dominio (alumnos, profesores, cargos, calificaciones, asistencias, comunicados, cruds)

## Modelos clave (`gestion_academica/models.py`)

`CicloLectivo`, `Turno`, `Especialidad`, `Aula`, `Curso`, `Burbuja`, `Persona`, `Profesor`, `Alumno`, `Preceptor`, `PersonalNoDocente`, `TipoCargo`, `PersonalCargo`, `AsignacionCargo`, `Materia`, `Dictado`, `InscripcionDictado`, `HorarioDictado`, `NotaEtapa`, `NotaActividad`, `Intensificacion`, `Asistencia`, `HistorialAcademico`, `Comunicado`.

Roles de usuario en `usuarios/User` → dashboards: staff, profesor, preceptor, pernodoc, jerárquicos, alumno, cargos.

## Rutas útiles (`gestion_academica/urls.py`)

- `/alumnos/`, `/profesores/`, `/cargos/`, `/calificaciones/`, `/boletines/`, `/planilla-docente/`
- `/asistencias/`, `/planilla-preceptor/`, `/comunicados/`, `/carga/alumnos/`
- CRUDs: `/tipos-cargo/`, `/especialidades/`, `/cursos/`, `/materias/`, `/turnos/`, `/aulas/`, `/burbujas/`, `/ciclos-lectivos/`

## Comandos

```bash
./venv/bin/python manage.py runserver        # servidor
./venv/bin/python manage.py check            # verificación (siempre correr tras cambios)
./venv/bin/python manage.py makemigrations   # nuevas migraciones
./venv/bin/python manage.py migrate          # aplicar migraciones
./venv/bin/python manage.py createsuperuser  # super usuario
```

## Convenciones

- **Sin linter/config de tests configurados**: validar con `manage.py check`; no asumir herramientas no instaladas.
- Vistas y modelos son monolíticos (un archivo por app); mantener el patrón existente al agregar código.
- Templates extienden `usuarios/base.html`; agregar CSS/JS en `usuarios/static/usuarios/` por dominio.
- Importar planillas con los formularios existentes (`ImportarAlumnosForm`, `ImportarProfesoresForm`).
- NO agregar comentarios al código salvo que se pida.
- `SECRET_KEY`/`DEBUG` se leen de `.env` (ver `.env.example`) con fallback de desarrollo.

## Git / GitHub

- No hacer push directo a `main`; todo cambio vía Pull Request.
- Branches: `feature/*`, `fix/*`, `hotfix/*`, `docs/*`.
- Commits con formato `tipo: descripción` (feat/fix/docs/refactor).
- CI: `.github/workflows/discord_notifications.yml` notifica a Discord los cambios en `main` (requiere secret `DISCORD_WEBHOOK_URL`).

## Nota

- `backup/` es la copia del fork de referencia (fuente de features ya integradas) y está en `.gitignore`. No se edita; si se necesita, las features ya están en el código principal.
