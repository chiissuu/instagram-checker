# Decisiones

Registro de "por qué se hizo así" para no reabrir discusiones ya cerradas.

## Verificación en línea

- **Playwright + navegador real, no la API interna**: se probó la API interna de Instagram primero; bloquea clientes automatizados casi al instante incluso con cabeceras y cookies correctas. Cargar la página real del perfil funciona con normalidad.
- **Nunca inicia sesión**: el navegador entra sin login. Si algo sale mal, el riesgo es que Instagram deje de mostrar perfiles sin sesión durante un rato — nunca que se marque la cuenta real del usuario.
- **Sin reintento dentro de la misma ejecución**: se consideró añadir un reintento automático cuando una comprobación da "no_verificable". Se descartó porque, según el propio usuario, ese resultado es muy común (~300 cuentas/20 min de media) y reintentar en caliente doblaría el tiempo de espera para el caso más frecuente. En su lugar, el reintento ocurre **entre ejecuciones** vía la caché (ver Funcionamiento.md) — efectivamente gratis.
- **Check por DOM como señal añadida, no sustituto**: se evaluó sustituir el chequeo por título por uno basado en el contenido del DOM, pensando que sería más rápido. No lo es — el tiempo lo consume la carga de página + la pausa deliberada, no el propio chequeo. Se dejó como señal adicional (OR con el título) para dar resiliencia ante un cambio de texto por parte de Instagram, sin tocar el tiempo de ejecución.

## Alcance del script

- Se eliminaron los cálculos de `mutuos` y `te_siguen_pero_no_sigues`: el script está pensado únicamente para "a quién sigues que no te sigue de vuelta" (lo único que Instagram no ofrece nativamente). Los otros dos cálculos eran código muerto.
- **Auto-unfollow aparcado a propósito**: requeriría login real y acciones reales sobre la cuenta — salto de alcance y riesgo mucho mayor (posible marcado por Instagram como comportamiento automatizado). Se decidió dejarlo fuera hasta que se hable explícitamente como su propia feature.

## Documentación

- **Inglés como README principal**: `README.md`/`README.txt` son la versión en inglés (más alcance al ser repo público); `README.es.md`/`README.es.txt` son el original en español. Los `.md` llevan selector de idioma cruzado arriba del todo; los `.txt` no, porque su público (gente no técnica) los recibe directamente de mano del usuario, no navegando GitHub.
- **`READMEs/` en vez de `docs/`**: el usuario rechazó `docs/` por sonar "a otra cosa". Solo `README.md` necesita estar en la raíz del repo para que GitHub lo muestre en portada — los otros tres nunca tuvieron ese tratamiento especial, así que moverlos a una subcarpeta no pierde nada.

## Calidad de código

- **ruff con ruleset explícito (`E`, `F`, `I`, `UP`) en `ruff.toml`**: el comportamiento por defecto de ruff en este entorno incluía reglas de `flake8-bandit` (S) y `flake8-blind-except` (BLE) que marcaban como error patrones usados a propósito en el script (p. ej. `except Exception: pass` para limpieza tras un Ctrl+C, ya documentado con comentario explicando por qué). Se fijó el ruleset explícitamente para evitar ese ruido.
- **CI con matriz Python 3.9-3.13**: cubre el rango de versiones razonable sin necesidad real de ir más atrás (el script usa `from __future__ import annotations`, soportado desde 3.7, pero no hay razón para testear versiones tan antiguas).

## Comentarios en el código

- Se añadieron cabeceras numeradas (`1 ·`, `2.1 ·`...) y un bloque de cabecera de archivo (Programa/Autor/Fecha/Descripción) **a petición explícita del usuario**, con el estilo de un ejemplo en C que proporcionó. Esto va contra la convención por defecto de "sin comentarios salvo que expliquen un porqué no obvio" — aquí se siguió la instrucción explícita del usuario por encima de esa convención por defecto.

## Rama `demo`

- Usa un export **100% sintético**: mismo grafo de relaciones que el export real (mismos totales: 813 seguidos, 1217 seguidores, 301 que no siguen de vuelta), pero cada username real sustituido por un `cuenta_demo_XXXX` aleatorio, no reversible. Se descartó subir los datos reales "total, solo son cuentas de Instagram" — el export real contiene ~2000 nombres de usuario reales de terceros, y publicarlo (aunque fuera en otra rama) es una exposición de datos personales real, además de contradecir la propia promesa de privacidad del README ("por defecto ningún dato sale de tu ordenador").

## Repos externos tocados en la misma sesión (no son instagram-checker, pero mismo criterio aplicado)

- En `MegatronixOS` y `Restaurant-Ordering-Platform` (ambos con coautores) no se añadió licencia MIT hasta que el usuario confirmó explícitamente que quería ponerla de todos modos, después de que se le explicara que un `LICENSE` concede permisos en nombre de todos los titulares del copyright conjunto, no solo de quien lo sube a GitHub.
