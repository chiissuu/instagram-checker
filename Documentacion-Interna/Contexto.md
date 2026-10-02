# Contexto

## Por qué existe

Herramienta personal de Jesús (chiissuu) para saber qué cuentas sigue en Instagram que no le siguen de vuelta — Instagram no ofrece esto de forma nativa. También funciona como pieza de portfolio: código limpio, tests, CI, documentación bilingüe.

## Historia resumida

El script ya existía y funcionaba (comparación básica + verificación opcional por Playwright) antes de la sesión grande de trabajo. A partir de ahí:

**Sesión 2026-09-09 — build principal** (ver [Sesiones/2026-09-09-build-inicial.md](Sesiones/2026-09-09-build-inicial.md)): caché de verificación persistente, limpieza de cálculos no usados, exportación CSV/JSON, segunda señal (DOM) para detectar cuentas fantasma, type hints, tests unitarios, `requirements-optional.txt`, flags de CLI, READMEs bilingües (inglés principal, español en `README.es.*`), rama `demo` con datos sintéticos, cabeceras numeradas + comentarios en el código, CI de GitHub Actions, badges, release `v1.0.0`, topics.

Dentro de esa misma sesión, tangencialmente: se aplicó un tratamiento similar (topics, CI, licencia) a otros dos repos del usuario (`MegatronixOS`, `Restaurant-Ordering-Platform`) — incluyendo encontrar y arreglar bugs reales de compilación en Java en `Restaurant-Ordering-Platform`. No forma parte de `instagram-checker` pero ocurrió en la misma conversación.

**Sesión 2026-10-02 — limpieza de repo + vault de contexto** (ver [Sesiones/2026-10-02-limpieza-repo.md](Sesiones/2026-10-02-limpieza-repo.md)): los READMEs secundarios (`README.es.md`, `README.txt`, `README.es.txt`) se movieron a `READMEs/` para despejar la raíz — solo `README.md` necesita estar en la raíz para que GitHub lo renderice en portada, así que mover los otros tres no cuesta nada. Se crea esta carpeta `Documentacion-Interna/` como válvula de contexto para Obsidian, inspirada en el patrón que el usuario ya usa en otro proyecto (`Contexto.md`, `Decisiones.md`, `Pendientes.md`, `Sesiones/`, etc.).

## Quién trabaja en esto

Proyecto individual de Jesús. Sin colaboradores en `instagram-checker` (a diferencia de `MegatronixOS` y `Restaurant-Ordering-Platform`, que sí son de varias personas — ver Decisiones.md de por qué eso importó para las licencias de esos otros repos, no de este).
