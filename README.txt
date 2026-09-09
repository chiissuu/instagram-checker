===============================================================
 INSTAGRAM CHECKER - GUIA DE USO
===============================================================

Este programa compara tus "seguidores" y "seguidos" de Instagram
y genera un archivo .txt con las personas a las que sigues pero
que no te siguen de vuelta.

Para que funcione necesitas 3 cosas:
  1. Tener Python instalado en tu ordenador.
  2. Descargar tu información de Instagram (el export).
  3. Ejecutar el script checker.py.

A continuación se explica cada paso.


---------------------------------------------------------------
1. COMO DESCARGAR TU INFORMACION DE INSTAGRAM
---------------------------------------------------------------

Instagram permite descargar toda la información de tu cuenta
(seguidores, seguidos, mensajes, fotos, etc.) desde el
"Centro de cuentas". El proceso es igual tanto si lo haces
desde el móvil (app) como desde el ordenador (navegador web).

  1. Entra en Instagram (app o instagram.com) y accede a tu
     perfil.
  2. Entra en "Configuración y privacidad".
  3. Entra en "Centro de cuentas".
  4. Pulsa en "Tu información y permisos".
  5. Pulsa en "Descargar tu información".
  6. Selecciona tu cuenta de Instagram y pulsa en "Crear
     archivo de exportación".

  Al crear el archivo de exportación tendrás que elegir varias
  opciones. Se recomienda configurarlas así:

    - Información a incluir: selecciona SOLO "Seguidores y
      seguidos". No hace falta marcar el resto de categorías,
      el script solo usa esta.

    - Intervalo de fechas: el que tú prefieras, pero para
      asegurar el mejor resultado (que no falte nadie en el
      listado) se recomienda elegir "Todas las fechas" /
      "Todo el periodo".

    - Formato: OBLIGATORIAMENTE "JSON" (no "HTML"), ya que el
      script solo sabe leer archivos JSON.

    - Calidad de los archivos multimedia: "Baja". No se van a
      exportar fotos ni vídeos, así que esta opción no influye
      en el resultado, y hace que el archivo pese menos.

    - Destino: puedes elegir descargarlo directamente a tu
      dispositivo, o transferirlo a un servicio externo como
      Google Drive, Dropbox, etc. (las opciones exactas pueden
      variar un poco entre la app y la web). Elige lo que te
      resulte más cómodo. En cualquier caso, Instagram te
      avisará por notificación o correo cuando el archivo esté
      listo para descargar; ese aviso llega independientemente
      del destino que elijas, no es en sí mismo una opción de
      destino.

  7. Confirma la solicitud. Instagram tardará desde unos minutos
     hasta varias horas en preparar el archivo.
  8. Cuando recibas el aviso, entra de nuevo en "Descargar tu
     información" (o al servicio externo elegido) y descarga
     el archivo .zip.

Nota: si Instagram entrega el archivo a través de Google Drive,
a veces lo divide en varias partes (por ejemplo
"...-1-001.zip", "...-1-002.zip"). Si te pasa esto, descomprime
todas las partes y copia el contenido de todas ellas en alguna
carpeta junto al script checker.py (ver siguiente punto).


---------------------------------------------------------------
2. QUE HACER CON EL ARCHIVO DESCARGADO
---------------------------------------------------------------

  1. Descomprime el/los archivo(s) .zip que te ha dado Instagram.
  2. Verás una carpeta con subcarpetas dentro (followers_and_following,
     personal_information, etc.).
  3. Copia TODO el contenido descomprimido dentro de CUALQUIER
     carpeta que esté junto al script checker.py. El nombre de
     esa carpeta da igual (puede llamarse como quieras, o
     conservar el nombre que traiga de Instagram).

La estructura final debe quedar más o menos así:

  instagram-checker/
    checker.py
    followers_and_following/     <- el nombre da igual
      followers_1.json
      following.json
      personal_information/
        ...

NO hace falta modificar nada dentro del script checker.py, ni
crear una carpeta con un nombre concreto: el script busca, de
forma recursiva, en TODAS las carpetas y subcarpetas que haya
junto a checker.py (entrando en todos los niveles, sin importar
cuántos haya) hasta encontrar followers_1.json y following.json,
estén donde estén y se llame como se llame la carpeta que los
contiene. Basta con descomprimir el zip y copiar su contenido
en algún sitio dentro de la carpeta del proyecto.


---------------------------------------------------------------
3. COMO INSTALAR PYTHON
---------------------------------------------------------------

El script está escrito en Python, así que necesitas tenerlo
instalado para poder ejecutarlo.

--- Windows ---

  1. Ve a https://www.python.org/downloads/ y descarga la última
     versión de Python para Windows.
  2. Ejecuta el instalador descargado.
  3. IMPORTANTE: marca la casilla "Add Python to PATH" antes de
     pulsar "Install Now".
  4. Una vez instalado, abre una terminal (cmd o PowerShell) y
     escribe:
         python --version
     Si te muestra un número de versión, está instalado
     correctamente.

--- macOS ---

  Opción A (recomendada, con Homebrew):
    1. Instala Homebrew si no lo tienes (https://brew.sh).
    2. Abre la Terminal y ejecuta:
         brew install python3
    3. Comprueba la instalación con:
         python3 --version

  Opción B (instalador oficial):
    1. Ve a https://www.python.org/downloads/ y descarga el
       instalador para macOS.
    2. Ábrelo y sigue los pasos del asistente.
    3. Comprueba la instalación abriendo la Terminal y
       escribiendo:
         python3 --version

--- Linux ---

  La mayoría de distribuciones ya traen Python instalado. Para
  comprobarlo, abre una terminal y escribe:
      python3 --version

  Si no está instalado, usa el gestor de paquetes de tu
  distribución:

    Ubuntu / Debian:
        sudo apt update
        sudo apt install python3

    Fedora:
        sudo dnf install python3

    Arch Linux:
        sudo pacman -S python

Opcional: si quieres usar la verificación en línea (punto 6),
instala además Playwright (Windows, macOS y Linux por igual):

    pip install playwright
    playwright install chromium

No hace falta si no vas a usar esa función opcional.


---------------------------------------------------------------
4. COMO EJECUTAR EL SCRIPT
---------------------------------------------------------------

  1. Abre una terminal (cmd, PowerShell, Terminal de macOS/Linux)
     dentro de la carpeta del proyecto (instagram-checker).
  2. Ejecuta el script con:

       Windows:      python checker.py
       macOS/Linux:  python3 checker.py

  3. Si el script no encuentra tu nombre de usuario de forma
     automática (esto ocurre si no incluiste la categoría
     "Información personal" en tu descarga), te lo pedirá por
     teclado. Simplemente escríbelo y pulsa Enter.
  4. Te preguntará si quieres activar la verificación opcional
     en línea (ver punto 6 más abajo). Puedes responder que no
     sin problema, es opcional.
  5. Al terminar, se generará un archivo de texto llamado:

       personas_que_no_te_siguen_de_vuelta_instagram_<tu_usuario>.txt

     Ese archivo contiene, uno por línea, el enlace de perfil de
     cada persona a la que sigues y que no te sigue de vuelta.


---------------------------------------------------------------
5. CUENTAS CUYO ENLACE NO FUNCIONA
---------------------------------------------------------------

Es normal que, dentro del listado generado, algunos enlaces te
lleven a un "Esta página no está disponible". No es un fallo
del script: esos usuarios siguen guardados en tu export porque
Instagram no limpia esa relación de tus datos aunque la cuenta:

  - se haya eliminado o desactivado,
  - haya sido suspendida/baneada por Instagram, o
  - te haya bloqueado a ti (en ese caso el perfil parece
    inexistente solo para tu cuenta).

No hay forma de distinguir estos casos solo con el enlace, y da
igual cuál sea el motivo: la acción a hacer es la misma, dejar
de seguir a esa cuenta (ver el consejo del siguiente punto).

Para dejar de seguir a estas cuentas, usa tu perfil > Siguiendo,
en lugar de la barra de búsqueda de Instagram. Las cuentas
eliminadas, suspendidas o que te han bloqueado no aparecen en
los resultados de búsqueda, pero siguen visibles (y se pueden
dejar de seguir) en tu lista de Siguiendo. El propio archivo
.txt generado incluye este mismo aviso al final.


---------------------------------------------------------------
6. VERIFICACION OPCIONAL EN LINEA (cuentas que ya no existen)
---------------------------------------------------------------

Al terminar el análisis, el script te pregunta si quieres que
compruebe, cuenta por cuenta, cuáles de los perfiles que no te
siguen de vuelta ya no existen (eliminados, suspendidos o que te
han bloqueado). Es totalmente opcional (por defecto NO se hace)
y solo se activa si respondes que sí esa vez.

Cómo funciona:

  - Abre cada perfil en un navegador real (Chromium, mediante la
    librería Playwright), exactamente como harías tú a mano; no
    llama a ninguna API interna. Se probó primero haciendo
    peticiones directas a la API interna de Instagram, pero esa
    vía bloquea cualquier cliente automatizado casi al instante
    (incluso con la cabecera correcta y cookies válidas);
    cargando la página del perfil de verdad, en cambio, funciona
    con normalidad.

  - NUNCA usa tu inicio de sesión. El navegador entra sin haber
    iniciado sesión en ninguna cuenta. Si algo sale mal, lo que
    se puede bloquear temporalmente es la visualización de
    perfiles sin sesión iniciada, nunca tu cuenta.

  - Necesita tener Playwright instalado (ver el punto 3, más
    abajo hay que ejecutar además "pip install playwright" y
    "playwright install chromium"). Si no lo tienes, el script
    te avisa con el comando exacto y deja esas cuentas marcadas
    como "no verificadas" en el .txt, en vez de fallar.

  - Comprueba antes si tienes conexión a internet. Si no la hay,
    no lo intenta: deja todas las cuentas marcadas como "no
    verificadas (sin conexión)" en el .txt, tal cual se pidió.

  - Va despacio a propósito, con una pausa aleatoria de unos
    segundos entre cada perfil visitado. Con muchas cuentas
    puede tardar bastantes minutos (el script te da una
    estimación antes de empezar).

  - Se detiene sola si Instagram empieza a poner trabas (varias
    comprobaciones seguidas sin resultado claro, por ejemplo si
    te redirige a la pantalla de inicio de sesión). En ese caso
    deja el resto como "no verificadas" en vez de insistir;
    puedes volver a ejecutar el script más tarde para reintentar
    con las que falten.

  - Puedes interrumpirla con Ctrl+C en cualquier momento sin
    perder el progreso: guarda como activas/inaccesibles las
    cuentas ya comprobadas hasta ese punto, y deja el resto
    marcado como "no verificadas (interrumpido)" en el .txt. No
    hace falta esperar a que termine si tarda demasiado.

  - El resultado final separa el .txt en tres bloques: cuentas
    que siguen activas (no te siguen de verdad), cuentas
    confirmadas como inaccesibles, y cuentas no verificadas (con
    el motivo).

Por qué no hay una opción más rápida, ligera o "garantizada":
Instagram no ofrece ninguna API pública para consultar si una
cuenta ajena existe. La única forma fiable encontrada es cargar
la página del perfil en un navegador de verdad, lo que implica
instalar Playwright (una dependencia bastante más pesada que el
resto del script) y ejecutar un Chromium en segundo plano. No es
oficial ni 100% fiable a largo plazo: puede dejar de funcionar
si Instagram cambia su web. Es normal, y no indica ningún
problema con tus datos.


---------------------------------------------------------------
SOLUCION DE PROBLEMAS
---------------------------------------------------------------

Se crea un archivo vacío llamado "python" (o similar) al
ejecutar el script.

  El script no crea ningún archivo con ese nombre. Si te
  aparece, casi siempre es porque el comando ejecutado incluía
  una redirección de salida por accidente, por ejemplo:

      python checker.py > python

  en vez de:

      python checker.py

  Revisa que el comando no tenga un ">" de más (puede colarse
  al pegar el comando o al reutilizar una línea del historial
  de la terminal con la flecha de arriba) y bórralo si aparece;
  no afecta al funcionamiento del script.


---------------------------------------------------------------
NOTAS FINALES
---------------------------------------------------------------

- Por defecto, este script no se conecta a internet ni envía tus
  datos a ningún sitio: todo el análisis se hace en local,
  leyendo los archivos JSON que ya tienes descargados. La única
  excepción es la verificación opcional en línea (punto 6): si
  la activas explícitamente, el script consulta a Instagram, de
  forma anónima y sin tu login, el nombre de usuario de cada
  cuenta que no te sigue de vuelta.
- Puedes volver a ejecutar el script cuando quieras, siempre que
  actualices el contenido de la carpeta con los datos (la que
  sea) con una descarga más reciente.
