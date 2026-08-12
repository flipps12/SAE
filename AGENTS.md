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

## Datos de ejemplo (importante)

- Los listados (`/alumnos/`, `/profesores/`, `/cargos/`, etc.) consultan los modelos de dominio (`Alumno`, `Profesor`, `PersonalCargo`), **NO** a `User`. Una cuenta `User` por sí sola NO aparece en los listados.
- Para que un usuario sea visible en el dominio debe existir la cadena: `User` → `Persona` (OneToOne `persona.user`) → perfil (`Alumno`/`Profesor`/`Preceptor`/`PersonalNoDocente`/`PersonalCargo`). `JERARQUICOS` solo tiene `Persona` vinculada (no hay modelo de perfil propio).
- `Persona` exige `dni` y `cuil` únicos (validadores en `gestion_academica/validators.py`) y `numero_legajo` único.
- Hay 200 usuarios de ejemplo creados (contraseña `sae2026`): `profesor001-080`, `alumno001-080`, `preceptor001-010`, `pernodoc001-010`, `jerarquico001-010`, `cargo001-010`, todos con su `Persona` y perfil. No borrarlos ni recrearlos sin verificar; ya están vinculados.

## Datos auxiliares sembrados (ciclo lectivo 2026)

- **Turnos**: Mañana, Tarde, Vespertino. **Especialidades**: Ciclo Básico, MMO, TQ, IPP.
- **Cursos (38)**: 1° A-F (6), 2° A-D (4), 3° A-D (4), 4°-7° con 2 divisiones por modalidad (MMO/TQ/IPP). Una `Burbuja` por curso.
- **Aulas (22)**: Aula 01-15, Taller MMO/TQ/IPP, Laboratorio 1-2, Biblioteca, SUM.
- **Materias (85)**: troncales (basico y 4-7) + talleres por especialidad por año. Todos los `Dictado` (436) tienen profesor asignado (los 80 profesores cubiertos).
- **Vinculaciones**: alumnos con `HistorialAcademico` (curso/burbuja) + `InscripcionDictado`; preceptores con `AsignacionPreceptor`; cargos con `AsignacionCargo` (Tipos: Jefe de Taller, Regente, Secretario Técnico, Jefe de Preceptores, Auxiliar Administrativo).
- **Datos transaccionales**: 800 `Asistencia` (10 días hábiles) y 1808 `NotaEtapa` (1C/2C) para poblar los dashboards. Hay 1 `Comunicado` de bienvenida.
- Curriculum por curso: 1-3 → 8 troncales; 4-5 → 9 troncales + 6 de especialidad; 6-7 → 6 troncales + 6 de especialidad.

## Flujo de alta manual de alumnos (`/alumnos/nuevo/`)

- `CrearAlumnoView` crea `Persona` + `Alumno` + `HistorialAcademico` + `InscripcionDictado` y, desde el fix, **asigna automáticamente un preceptor al curso** si ese curso no tiene `AsignacionPreceptor` en el ciclo activo (elige un preceptor sin asignaciones en el ciclo o el menos cargado). Esto evita vínculos incompletos.
- IMPORTANTE: el alta manual NO crea cuenta de `User`; el alumno queda sin login. Si se necesita que el alumno acceda al sistema, hay que crearle el `User` aparte (o vincularlo).

## Planilla del docente (`/planilla-docente/`) — decimales

- El proyecto usa `LANGUAGE_CODE='es-ar'`; Django localiza los números (coma decimal). Los `<input type="number">` de la planilla deben renderizar valores con **punto** (`|unlocalize`, requiere `{% load l10n %}`) o el navegador los envía con coma y el guardado fallaba.
- El POST de `PlanillaCargaNotasView` parsea valores con `_valor_decimal()` (tolera coma o punto) antes de asignarlos a los `DecimalField`; NO usar `int()`/`float()` directo sobre datos del form, porque revienta con `9,00` y el `transaction.atomic()` revierte todo.
