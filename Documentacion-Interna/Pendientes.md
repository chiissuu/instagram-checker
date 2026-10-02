# Pendientes

El proyecto se considera funcionalmente completo (v1.0.0, CI en verde, topics y release ya puestos). Esto es lo que queda abierto o aparcado a propósito — no bloquea nada.

## Aparcado a propósito (no son bugs, son decisiones)

- **Auto-unfollow**: dejar de seguir cuentas automáticamente desde el propio script. Requeriría login real + acciones reales sobre la cuenta de Instagram del usuario — se trataría como una feature nueva con su propio alcance, no un añadido menor. Ver Decisiones.md.

## Ideas opcionales, nunca pedidas explícitamente

- **Branch protection en `main`**: exigir que el CI pase antes de poder mergear — tiene sentido ahora que existe el workflow de tests, pero requiere tocar ajustes del repo en GitHub (fuera del alcance de lo que se puede hacer sin `gh` CLI/API).
- **Fijar el repo en el perfil de GitHub** para que destaque como pieza de portfolio.
- **Imagen de social preview** del repo (la que se ve al compartir el link en redes/Slack).

## En curso (2026-10-02)

- Reorganización de la raíz del repo: READMEs secundarios movidos a `READMEs/`, creación de esta carpeta `Documentacion-Interna/`. Ver [Sesiones/2026-10-02-limpieza-repo.md](Sesiones/2026-10-02-limpieza-repo.md) para el detalle exacto de qué se tocó.

## Cosas que NO están pendientes (ya resueltas, por si se duda)

- Topics del repo: puestos por el usuario (`python`, `cli`, `instagram`, `automation`, `playwright`).
- Release `v1.0.0`: publicado con changelog.
- Descripción del repo en "About": ya estaba puesta.
