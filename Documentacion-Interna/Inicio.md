# Instagram Checker — Inicio

Válvula de contexto del proyecto. Pensada para cargar rápido en Obsidian (o en una sesión de Claude nueva) sin tener que releer todo `checker.py` ni el historial de conversación completo.

## Qué es el proyecto

Script en Python (`checker.py`, raíz del repo) que compara tus seguidores y seguidos de Instagram a partir del export oficial de datos, y genera un listado de quién no te sigue de vuelta. Tiene una verificación opcional en línea (Playwright) para detectar cuáles de esas cuentas ya no existen. Todo el análisis corre en local; la única conexión a internet es la verificación opcional, y nunca usa tu login.

- Repo: https://github.com/chiissuu/instagram-checker
- Rama `main`: código real, sin datos personales (gitignorados).
- Rama `demo`: mismo código, con un export sintético (usernames falsos, mismo grafo de relaciones) para poder enseñarlo sin exponer datos reales.
- Estado: v1.0.0 publicado, CI en verde, se considera funcionalmente completo.

## Mapa de esta carpeta

| Archivo | Para qué sirve |
|---|---|
| [Funcionamiento.md](Funcionamiento.md) | Cómo funciona el script por dentro: flujo de datos, cada sección del código, mecanismos clave (caché, verificación, DOM check). |
| [Contexto.md](Contexto.md) | Por qué existe el proyecto y qué ha ido pasando a lo largo del desarrollo (historia resumida). |
| [Decisiones.md](Decisiones.md) | Decisiones técnicas tomadas y el razonamiento detrás de cada una — para no repetir una discusión ya cerrada. |
| [Pendientes.md](Pendientes.md) | Qué queda abierto o aparcado a propósito. |
| [Sesiones/](Sesiones/) | Registro por fecha de qué se hizo en cada sesión de trabajo sobre este repo. |

## Dónde está cada cosa en el repo real

```
instagram-checker/
├── README.md                  ← inglés, el que ve GitHub en portada
├── READMEs/                   ← README.es.md, README.txt, README.es.txt
├── checker.py                 ← todo el script, con cabeceras numeradas (1·..6·) y comentarios
├── tests/test_checker.py      ← 13 tests, unittest estándar
├── ruff.toml                  ← config del linter (reglas E/F/I/UP)
├── requirements-optional.txt  ← solo playwright, solo si usas --verify
├── .github/workflows/tests.yml← CI: tests en Python 3.9-3.13 + lint
└── Documentacion-Interna/     ← esta carpeta
```
