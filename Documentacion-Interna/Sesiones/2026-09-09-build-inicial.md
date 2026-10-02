# 2026-09-09 — Build principal

Sesión larga, de un script funcional básico a v1.0.0 completo.

## Código (`checker.py`)

- Caché de verificación entre ejecuciones (`verificacion_cache.json`), con reintento automático de cuentas `no_verificable` en la siguiente ejecución, antes que las cuentas nuevas.
- Eliminados los cálculos de `mutuos` y `te_siguen_pero_no_sigues` (código muerto).
- Exportación en `--format txt|csv|json`, todas construidas desde la misma lista de `Fila`.
- Segunda señal (texto del DOM) además del título de la pestaña, para detectar cuentas fantasma — añadida como respaldo, no sustituto.
- Type hints en todo el módulo (`from __future__ import annotations`).
- Flags de CLI: `--verify`, `--no-verify`, `--format`.
- Cabeceras numeradas (`1 ·`...`6 ·`, con subcabeceras `X.Y ·` por función) y bloque de cabecera de archivo (Programa/Autor/Fecha/Descripción), a petición explícita del usuario con un ejemplo en C como referencia de estilo.

## Calidad

- `tests/test_checker.py`: 13 tests con `unittest`, cubriendo las funciones puras.
- `ruff.toml`: ruleset fijado a `E,F,I,UP` (el resto de reglas por defecto chocaba con patrones intencionados del código).
- `.github/workflows/tests.yml`: CI con matriz Python 3.9-3.13 (tests) + job de lint.

## Documentación

- `requirements-optional.txt`: solo `playwright`, para la verificación opcional.
- READMEs bilingües: `README.md`/`README.txt` pasan a ser la versión en inglés (principal); `README.es.md`/`README.es.txt` quedan como el original en español.
- Badges (tests, Python, licencia) en los `.md`.

## Rama `demo`

- Export sintético generado a partir del export real del usuario: mismo grafo de relaciones (mismos totales — 813/1217/301), cada username sustituido por un `cuenta_demo_XXXX` aleatorio y no reversible. Incluye salida de ejemplo en los 3 formatos.
- Se descartó subir los datos reales directamente — ver Decisiones.md.

## GitHub

- Release `v1.0.0` con changelog.
- Topics añadidos por el usuario tras indicación: `python`, `cli`, `instagram`, `automation`, `playwright`.

## Fuera de `instagram-checker` (misma sesión, otros repos)

- `MegatronixOS`: `.gitignore` para archivos de salida generados (`CONTENTS_CACHE.bin`, `logcache.txt`), rama `demo` con esos archivos como ejemplo, CI de compilación, licencia MIT (tras confirmación explícita del usuario, dado que es coautoría con Mario Viso Quito).
- `Restaurant-Ordering-Platform` (fork de un proyecto de 3 personas): arreglado bug de README (URL de clonado desactualizada), CI de compilación — que reveló bugs reales preexistentes (imports a paquetes inexistentes, constructor mal nombrado) nunca antes compilados por línea de comandos; arreglados y verificados en local antes de subir. Licencia MIT añadida tras confirmación explícita.
