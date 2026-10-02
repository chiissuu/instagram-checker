# 2026-10-02 — Limpieza de repo + vault de contexto

Objetivo: la raíz del repo se veía con demasiados archivos sueltos (4 READMEs junto a `checker.py`). Segundo objetivo: crear una válvula de contexto en Markdown para Obsidian, inspirada en el patrón que el usuario ya usa en otro proyecto (`Contexto.md`, `Decisiones.md`, `Pendientes.md`, `Sesiones/`...).

## Qué se hizo

- Movidos `README.es.md`, `README.txt`, `README.es.txt` a `READMEs/`. Solo `README.md` necesita estar en la raíz para que GitHub lo renderice en portada — los otros tres nunca tuvieron ese tratamiento especial, así que no se pierde nada al moverlos.
  - Se descartó el nombre `docs/` (el usuario lo rechazó por sonar "a otra cosa") y también `README's` (apóstrofe en nombre de carpeta da problemas de escape/URL) — se usó `READMEs/`.
  - Actualizado el selector de idioma cruzado en `README.md` ↔ `READMEs/README.es.md`, y el enlace a `LICENSE` dentro de `READMEs/README.es.md` (pasa a `../LICENSE` al bajar un nivel).
- Creada `Documentacion-Interna/` con: `Inicio.md`, `Funcionamiento.md`, `Contexto.md`, `Decisiones.md`, `Pendientes.md`, `Sesiones/` (este archivo y el retroactivo del 2026-09-09).

## Por qué va en el repo y no solo local

El usuario mantiene este mismo patrón (vault de Markdown dentro de un repo de GitHub, leído desde Obsidian) en otro proyecto — se replicó aquí para consistencia, en vez de dejarlo como notas sueltas fuera de git.
