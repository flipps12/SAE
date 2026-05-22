# Guía de Contribución


---

# Configuración Inicial

## 1. Clonar el repositorio

```bash
git clone https://github.com/USUARIO/REPOSITORIO.git
```

Ejemplo:

```bash
git clone https://github.com/flipps12/SAE.git
```

Entrar al proyecto:

```bash
cd REPOSITORIO
```

---

## 2. Verificar branch principal

```bash
git branch
```

Cambiar a `main`:

```bash
git checkout main
```

Actualizar repositorio:

```bash
git pull origin main
```

---

# Flujo de Trabajo

## IMPORTANTE

- No hacer `push` directamente a `main`
- Todo cambio debe pasar por Pull Request (PR)

---

## 1. Crear una branch

Crear una branch nueva antes de comenzar:

```bash
git checkout -b feature/nombre-feature
```

Ejemplos:

```bash
git checkout -b feature/login
git checkout -b feature/chat-system
git checkout -b fix/navbar-error
```

---

# Convención de Branches

## Features

Nuevas funcionalidades:

```txt
feature/*
```

Ejemplos:

```txt
feature/auth
feature/dashboard
feature/chat
```

---

## Fixes

Corrección de errores:

```txt
fix/*
```

Ejemplos:

```txt
fix/api-timeout
fix/navbar-mobile
```

---

## Hotfixes

Errores críticos:

```txt
hotfix/*
```

---

## Documentación

```txt
docs/*
```

---

# Commits

Usar mensajes claros.

## Formato recomendado

```txt
tipo: descripción
```

Ejemplos:

```txt
feat: agregar autenticación JWT
fix: corregir validación del login
docs: actualizar README
refactor: simplificar middleware
```

---

# Guardar Cambios

Agregar archivos:

```bash
git add .
```

Crear commit:

```bash
git commit -m "feat: agregar sistema de login"
```

---

# Subir Cambios

Subir branch al repositorio:

```bash
git push origin nombre-de-tu-branch
```

Ejemplo:

```bash
git push origin feature/login
```

---

# Pull Requests

Luego de subir la branch:

1. Ir al repositorio en GitHub
2. Abrir un Pull Request
3. Seleccionar:
   - base: `main`
   - compare: tu branch
4. Explicar claramente los cambios realizados

---

# Mantener la Branch Actualizada

Antes de trabajar:

```bash
git checkout main
git pull origin main
```

Actualizar tu branch:

```bash
git checkout feature/mi-branch
git merge main
```

---

# Reglas Importantes

- No hacer push directo a `main`
- No subir secretos o credenciales
- Mantener código legible
- Probar cambios antes de abrir PR
- Mantener PRs pequeños y específicos

---


