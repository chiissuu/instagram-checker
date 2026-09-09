# Instagram Checker

Script en Python que compara tus **seguidores** y **seguidos** de Instagram a partir del export oficial de tus datos, y genera un `.txt` con las personas a las que sigues pero que no te siguen de vuelta.

Todo el análisis principal se hace **en local**: el script solo lee los archivos JSON que tú mismo descargas de Instagram. Opcionalmente puede conectarse a Instagram para comprobar cuáles de esas cuentas ya no existen (ver [Verificación opcional en línea](#verificación-opcional-en-línea-cuentas-que-ya-no-existen)), pero solo si tú lo pides explícitamente cada vez.

## Qué genera

Un único archivo de texto:

```
personas_que_no_te_siguen_de_vuelta_instagram_<tu_usuario>.txt
```

con un enlace de perfil por línea, uno por cada persona a la que sigues y que no te sigue de vuelta.

## Requisitos

- Python 3 instalado.
- El export de tus datos de Instagram en formato **JSON**.
- Opcional, solo si vas a usar la [verificación en línea](#verificación-opcional-en-línea-cuentas-que-ya-no-existen): [Playwright](https://playwright.dev/python/) (`pip install playwright && playwright install chromium`).

## 1. Descargar tus datos de Instagram

El proceso es el mismo tanto desde el móvil como desde el ordenador, ya que Instagram lo gestiona todo desde el **Centro de cuentas**.

1. Entra en Instagram (app o [instagram.com](https://instagram.com)) y accede a tu perfil.
2. Entra en **Configuración y privacidad**.
3. Entra en **Centro de cuentas**.
4. Pulsa en **Tu información y permisos**.
5. Pulsa en **Descargar tu información**.
6. Selecciona tu cuenta de Instagram → **Crear archivo de exportación**.

### Qué elegir al crear el archivo de exportación

| Opción | Qué elegir | Por qué |
|---|---|---|
| Información a incluir | Solo **Seguidores y seguidos** | Es lo único que usa el script; no hace falta descargar el resto |
| Intervalo de fechas | El que prefieras (recomendado: **todas las fechas**) | Para asegurarte de que no falte nadie en el resultado |
| Formato | **JSON** (nunca HTML) | El script solo sabe leer JSON |
| Calidad de archivos multimedia | **Baja** | No se exportan fotos ni vídeos, así que no influye, y el archivo pesa menos |
| Destino | A tu dispositivo, o transferido a un servicio como **Google Drive** | El que te resulte más cómodo |

Sobre el destino: Instagram deja elegir entre descargarlo directamente al dispositivo o transferirlo a un servicio en la nube (Google Drive, Dropbox, Google Photos...); las opciones exactas pueden variar algo entre la app y la web. En cualquier caso, te avisará por notificación o correo cuando el archivo esté listo para descargar — ese aviso llega igual sea cual sea el destino elegido, no es una opción de destino en sí misma.

Confirma la solicitud y espera al aviso (puede tardar desde minutos hasta unas horas).

> **Nota:** si Instagram entrega el archivo a través de Google Drive, a veces lo divide en varias partes (`...-1-001.zip`, `...-1-002.zip`, etc.). Si te ocurre, descomprime todas las partes y copia el contenido de todas ellas junto a `checker.py` (ver siguiente paso).

## 2. Colocar los datos en el proyecto

1. Descomprime el/los `.zip` que te envía Instagram.
2. Copia todo su contenido dentro de **cualquier carpeta que esté junto a `checker.py`**. Por ejemplo:

```
instagram-checker/
├── checker.py
└── followers_and_following/      ← el nombre de esta carpeta da igual
    ├── followers_1.json
    └── following.json
```

No es necesario tocar nada del script ni respetar un nombre de carpeta concreto: el script busca, de forma recursiva, en **todas las carpetas y subcarpetas que haya junto a `checker.py`** hasta encontrar `followers_1.json` y `following.json`, sea cual sea el nombre o la profundidad de las carpetas que traiga el `.zip` (Instagram ha usado distintas estructuras según el método de descarga, por ejemplo con o sin una carpeta `connections/` intermedia). Basta con descomprimir y copiar: no hace falta renombrar nada.

## 3. Instalar Python

<details>
<summary>Windows</summary>

1. Descarga el instalador desde [python.org/downloads](https://www.python.org/downloads/).
2. Ejecútalo y marca la casilla **Add Python to PATH** antes de instalar.
3. Verifica con:

```bash
python --version
```
</details>

<details>
<summary>macOS</summary>

Con Homebrew (recomendado):

```bash
brew install python3
python3 --version
```

O descargando el instalador oficial desde [python.org/downloads](https://www.python.org/downloads/).
</details>

<details>
<summary>Linux</summary>

Suele venir preinstalado. Comprueba con:

```bash
python3 --version
```

Si no lo tienes:

```bash
# Ubuntu / Debian
sudo apt update && sudo apt install python3

# Fedora
sudo dnf install python3

# Arch
sudo pacman -S python
```
</details>

## 4. Ejecutar el script

```bash
python checker.py       # Windows
python3 checker.py      # macOS / Linux
```

Si el export no incluye la categoría "Información personal", el script no podrá detectar tu usuario automáticamente y te lo pedirá por teclado.

Al terminar verás un resumen en la terminal y se creará el archivo `personas_que_no_te_siguen_de_vuelta_instagram_<tu_usuario>.txt` en la carpeta del proyecto.

## Cuentas cuyo enlace no funciona

Es normal que, dentro del listado generado, algunos enlaces te lleven a un "Esta página no está disponible". No es un fallo del script: esos usuarios siguen guardados en tu export porque Instagram no limpia esa relación de tus datos aunque la cuenta:

- se haya **eliminado** o **desactivado**,
- haya sido **suspendida/baneada** por Instagram, o
- **te haya bloqueado** a ti (en ese caso el perfil parece inexistente solo para tu cuenta).

No hay forma de distinguir estos casos solo con el enlace, y da igual cuál sea el motivo: la acción a hacer es la misma, dejar de seguir a esa cuenta (ver consejo siguiente).

### Cómo dejar de seguir a estas cuentas

Usa tu perfil → **Siguiendo**, en lugar de la barra de búsqueda de Instagram. Las cuentas eliminadas, suspendidas o que te han bloqueado no aparecen en los resultados de búsqueda, pero siguen visibles (y se pueden dejar de seguir) en tu lista de Siguiendo. El propio archivo `.txt` generado incluye este mismo aviso al final.

## Verificación opcional en línea (cuentas que ya no existen)

Al terminar el análisis, el script te pregunta si quieres que compruebe, cuenta por cuenta, cuáles de los perfiles que no te siguen de vuelta ya no existen (eliminados, suspendidos o que te han bloqueado). Es completamente opcional (por defecto no se hace) y solo se activa si respondes que sí esa vez.

Cómo funciona:

- **Abre cada perfil en un navegador real (Chromium, vía Playwright)**, exactamente como harías tú a mano — no llama a ninguna API interna. Se probó primero con peticiones directas a la API interna de Instagram, pero esa vía bloquea cualquier cliente automatizado casi al instante (incluso con la cabecera correcta y cookies válidas); cargar la página del perfil de verdad, en cambio, funciona con normalidad.
- **Nunca usa tu inicio de sesión.** El navegador entra sin haber iniciado sesión en ninguna cuenta. Así, si algo sale mal, el riesgo es que Instagram deje de mostrar perfiles sin sesión iniciada durante un rato — nunca que se marque tu cuenta por comportamiento automatizado.
- **Requiere tener Playwright instalado** (ver [Requisitos](#requisitos)). Si no lo tienes, el script te avisa con el comando exacto a ejecutar y deja esas cuentas marcadas como "no verificadas" en el `.txt`, en vez de fallar.
- **Comprueba antes si tienes conexión a internet.** Si no la hay, no lo intenta: deja todas las cuentas marcadas como "no verificadas (sin conexión)" en el `.txt`.
- **Va despacio a propósito**, con una pausa aleatoria de unos segundos entre cada perfil visitado. Con muchas cuentas puede tardar bastantes minutos (el script te da una estimación antes de empezar).
- **Se detiene sola si Instagram empieza a poner trabas** (varias comprobaciones seguidas sin resultado claro, por ejemplo si te redirige a la pantalla de inicio de sesión). En ese caso, dejará el resto de cuentas como "no verificadas" en vez de insistir — puedes volver a ejecutar el script más tarde para reintentarlo con las que falten.
- **Puedes interrumpirla con Ctrl+C en cualquier momento sin perder el progreso**: guarda como activas/inaccesibles las cuentas ya comprobadas hasta ese punto, y deja el resto marcado como "no verificadas (interrumpido)" en el `.txt` — no hace falta esperar a que termine si tarda demasiado.
- El resultado final separa el `.txt` en tres bloques: cuentas que siguen activas (no te siguen de verdad), cuentas confirmadas como inaccesibles, y cuentas no verificadas (con el motivo).

> **Por qué no hay una opción más rápida, ligera o "garantizada":** Instagram no ofrece ninguna API pública para consultar si una cuenta ajena existe. La única forma fiable encontrada es cargar la página del perfil en un navegador de verdad, lo que implica instalar Playwright (una dependencia bastante más pesada que el resto del script) y ejecutar un Chromium en segundo plano. No es oficial ni 100% fiable a largo plazo: puede dejar de funcionar si Instagram cambia su web. Es normal, y no indica ningún problema con tus datos.

## Solución de problemas

**Se crea un archivo vacío llamado `python` (o similar) al ejecutar el script.**
El script no crea ningún archivo con ese nombre. Si te aparece, casi siempre es porque el comando ejecutado incluía una redirección de salida por accidente, por ejemplo `python checker.py > python` en vez de `python checker.py`. Revisa que el comando no tenga un `>` de más (puede colarse al pegar el comando o al reutilizar una línea del historial de la terminal con la flecha ↑) y bórralo si aparece; no afecta al funcionamiento del script.

## Privacidad

Por defecto, ningún dato sale de tu ordenador: el script únicamente lee los `.json` que tú descargaste desde tu cuenta de Instagram. La única excepción es la [verificación opcional en línea](#verificación-opcional-en-línea-cuentas-que-ya-no-existen): si la activas explícitamente, el script consulta a Instagram (de forma anónima, sin tu login) el nombre de usuario de cada cuenta que no te sigue de vuelta, para saber si sigue existiendo.
