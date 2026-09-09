import json
import random
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

TITULO_PERFIL_NO_DISPONIBLE = "Profile isn't available • Instagram"
PAUSA_MINIMA_SEGUNDOS = 2
PAUSA_MAXIMA_SEGUNDOS = 5
MAX_FALLOS_SEGUIDOS = 3  # comprobaciones sin resultado claro seguidas antes de darse por bloqueado


def limpiar_usuario(usuario):
    if not usuario:
        return None

    usuario = usuario.strip().lower()
    usuario = usuario.replace("@", "")

    if not usuario:
        return None

    return usuario


def extraer_usuario_desde_href(href):
    if not href:
        return None

    href = href.strip().split("?")[0].rstrip("/")

    if "/_u/" in href:
        usuario = href.split("/_u/")[-1]
        return limpiar_usuario(usuario)

    if "instagram.com/" in href:
        usuario = href.split("instagram.com/")[-1]
        return limpiar_usuario(usuario)

    return None


def extraer_followers(path):
    """
    Extrae usuarios desde followers_1.json.
    Normalmente Instagram guarda aquí el username en string_list_data -> value.
    """
    data = json.loads(path.read_text(encoding="utf-8"))
    usuarios = set()

    def recorrer(obj):
        if isinstance(obj, dict):
            if "string_list_data" in obj:
                for item in obj["string_list_data"]:
                    usuario = item.get("value")

                    if usuario:
                        usuarios.add(limpiar_usuario(usuario))
                    else:
                        usuario_href = extraer_usuario_desde_href(item.get("href"))
                        if usuario_href:
                            usuarios.add(usuario_href)

            for valor in obj.values():
                recorrer(valor)

        elif isinstance(obj, list):
            for item in obj:
                recorrer(item)

    recorrer(data)
    return {u for u in usuarios if u}


def extraer_following(path):
    """
    Extrae usuarios desde following.json.
    En algunas exportaciones Instagram guarda los usuarios en:
    relationships_following -> title
    y no dentro de value.
    """
    data = json.loads(path.read_text(encoding="utf-8"))
    usuarios = set()

    if isinstance(data, dict) and "relationships_following" in data:
        for item in data["relationships_following"]:
            usuario_title = limpiar_usuario(item.get("title"))

            if usuario_title:
                usuarios.add(usuario_title)

            for subitem in item.get("string_list_data", []):
                usuario_href = extraer_usuario_desde_href(subitem.get("href"))

                if usuario_href:
                    usuarios.add(usuario_href)

    return {u for u in usuarios if u}


def buscar_nombre_cuenta():
    """
    Busca el username del dueño de la cuenta en personal_information.json
    (Instagram lo guarda bajo string_map_data -> "Username").
    Si no existe ese archivo en el export, devuelve None.
    """
    for archivo in BASE_DIR.rglob("personal_information.json"):
        try:
            data = json.loads(archivo.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue

        resultado = None

        def recorrer(obj):
            nonlocal resultado
            if resultado:
                return

            if isinstance(obj, dict):
                string_map = obj.get("string_map_data")
                if isinstance(string_map, dict):
                    for clave, valor in string_map.items():
                        if clave.strip().lower() == "username":
                            usuario = limpiar_usuario(valor.get("value"))
                            if usuario:
                                resultado = usuario
                                return

                for valor in obj.values():
                    recorrer(valor)

            elif isinstance(obj, list):
                for item in obj:
                    recorrer(item)

        recorrer(data)

        if resultado:
            return resultado

    return None


def nombre_archivo_seguro(texto):
    return re.sub(r'[\\/*?:"<>|\s]', "_", texto).strip("_")


def hay_conexion_internet():
    try:
        urllib.request.urlopen("https://www.instagram.com", timeout=6)
        return True
    except (urllib.error.URLError, OSError):
        return False


def verificar_cuenta_instagram(pagina, usuario):
    """
    Comprueba, sin iniciar sesión, si el perfil de un usuario sigue
    existiendo/siendo accesible, cargando su página real con un
    navegador (igual que haría una persona), no la API interna.

    Devuelve: "existe", "no_existe" o "no_verificable".
    """
    url = f"https://www.instagram.com/{usuario}/?hl=en"

    try:
        pagina.goto(url, timeout=15000, wait_until="domcontentloaded")
        pagina.wait_for_timeout(1200)  # deja que cargue el título dinámico

        if "/accounts/login" in pagina.url or "/challenge" in pagina.url:
            return "no_verificable"

        titulo = (pagina.title() or "").strip()

        if titulo == TITULO_PERFIL_NO_DISPONIBLE:
            return "no_existe"

        if titulo and titulo != "Instagram":
            return "existe"

        return "no_verificable"

    except Exception:
        return "no_verificable"


def verificar_cuentas(usuarios):
    """
    Comprueba una lista de usuarios abriendo su perfil real en un
    navegador (Playwright), con una pausa aleatoria entre cada uno. Si
    varias comprobaciones seguidas no dan un resultado claro (señal de
    que Instagram ha empezado a poner trabas), o si el usuario interrumpe
    con Ctrl+C, se detiene y el resto se deja como "no verificado" en vez
    de perder el progreso. Nunca inicia sesión con la cuenta del usuario.

    Devuelve: (activas, fantasma, no_verificadas, interrumpido)
    """
    from playwright.sync_api import sync_playwright

    activas = []
    fantasma = []
    no_verificadas = []
    fallos_seguidos = 0
    interrumpido = False

    total = len(usuarios)

    playwright = sync_playwright().start()
    try:
        navegador = playwright.chromium.launch(headless=True)
        try:
            pagina = navegador.new_page()

            for indice, usuario in enumerate(usuarios, start=1):
                try:
                    resultado = verificar_cuenta_instagram(pagina, usuario)
                except KeyboardInterrupt:
                    print(f"\nInterrumpido por el usuario tras revisar {indice - 1} de {total} cuentas.")
                    print("Se guarda lo comprobado hasta ahora; el resto queda como 'no verificado'.")
                    no_verificadas.extend(usuarios[indice - 1:])
                    interrumpido = True
                    break

                if resultado == "existe":
                    activas.append(usuario)
                    fallos_seguidos = 0
                elif resultado == "no_existe":
                    fantasma.append(usuario)
                    fallos_seguidos = 0
                else:
                    fallos_seguidos += 1
                    no_verificadas.append(usuario)

                    if fallos_seguidos >= MAX_FALLOS_SEGUIDOS:
                        print(
                            f"Instagram ha empezado a poner trabas a las comprobaciones "
                            f"tras revisar {indice} de {total} cuentas."
                        )
                        print("Se deja el resto como 'no verificado' en vez de seguir insistiendo.")
                        no_verificadas.extend(usuarios[indice:])
                        break

                if indice % 10 == 0 or indice == total:
                    print(f"Comprobadas {indice}/{total} cuentas...")

                try:
                    time.sleep(random.uniform(PAUSA_MINIMA_SEGUNDOS, PAUSA_MAXIMA_SEGUNDOS))
                except KeyboardInterrupt:
                    print(f"\nInterrumpido por el usuario tras revisar {indice} de {total} cuentas.")
                    print("Se guarda lo comprobado hasta ahora; el resto queda como 'no verificado'.")
                    no_verificadas.extend(usuarios[indice:])
                    interrumpido = True
                    break
        finally:
            # Tras una interrupción (Ctrl+C), en Windows el proceso del
            # driver de Playwright puede morir junto con el propio script,
            # así que cerrar algo que ya está muerto puede lanzar un error.
            # Se ignora a propósito: ya tenemos los resultados que importan.
            try:
                navegador.close()
            except Exception:
                pass
    finally:
        try:
            playwright.stop()
        except Exception:
            pass

    return activas, fantasma, no_verificadas, interrumpido


def hay_playwright():
    try:
        import playwright.sync_api  # noqa: F401
        return True
    except ImportError:
        return False


def buscar_archivo_exacto(nombre_archivo):
    encontrados = [
        archivo
        for archivo in BASE_DIR.rglob("*.json")
        if archivo.name.lower() == nombre_archivo.lower()
    ]

    return encontrados


def main():
    archivos_followers = buscar_archivo_exacto("followers_1.json")
    archivos_following = buscar_archivo_exacto("following.json")

    if not archivos_followers:
        print(f"No he encontrado followers_1.json en ninguna subcarpeta de: {BASE_DIR}")
        print("Coloca el contenido del ZIP de Instagram en cualquier carpeta dentro de este directorio (el nombre de la carpeta no importa).")
        return

    if not archivos_following:
        print(f"No he encontrado following.json en ninguna subcarpeta de: {BASE_DIR}")
        print("Coloca el contenido del ZIP de Instagram en cualquier carpeta dentro de este directorio (el nombre de la carpeta no importa).")
        return

    followers = set()
    following = set()

    for archivo in archivos_followers:
        followers.update(extraer_followers(archivo))

    for archivo in archivos_following:
        following.update(extraer_following(archivo))

    no_te_siguen_de_vuelta = sorted(following - followers)
    te_siguen_pero_no_sigues = sorted(followers - following)
    mutuos = sorted(following & followers)

    nombre_cuenta = buscar_nombre_cuenta()
    if not nombre_cuenta:
        entrada = input(
            "No se ha podido detectar tu nombre de usuario automáticamente.\n"
            "Escribe tu nombre de usuario de Instagram (se usará para nombrar el archivo): "
        )
        nombre_cuenta = limpiar_usuario(entrada) or "cuenta_desconocida"

    output_file = BASE_DIR / f"personas_que_no_te_siguen_de_vuelta_instagram_{nombre_archivo_seguro(nombre_cuenta)}.txt"

    print("Resumen:")
    print(f"Personas a las que sigues: {len(following)}")
    print(f"Personas que te siguen: {len(followers)}")
    print(f"Mutuos: {len(mutuos)}")
    print(f"No te siguen de vuelta: {len(no_te_siguen_de_vuelta)}")
    print(f"Te siguen pero tú no les sigues: {len(te_siguen_pero_no_sigues)}")

    hacer_verificacion = False
    if no_te_siguen_de_vuelta:
        segundos_por_cuenta = (PAUSA_MINIMA_SEGUNDOS + PAUSA_MAXIMA_SEGUNDOS) / 2 + 2.5  # + tiempo de carga de la página
        estimado_minutos = round(len(no_te_siguen_de_vuelta) * segundos_por_cuenta / 60, 1)
        respuesta = input(
            f"\n¿Quieres que el script abra cada perfil de esas {len(no_te_siguen_de_vuelta)}\n"
            f"cuentas en un navegador (sin iniciar sesión con la tuya) para comprobar\n"
            f"cuáles ya no existen (eliminadas, suspendidas o que te han bloqueado)?\n"
            f"Necesita tener Playwright instalado (pip install playwright && playwright\n"
            f"install chromium) y conexión a internet, y tardaría unos {estimado_minutos}\n"
            f"minutos. Si Instagram empieza a poner trabas se para sola y deja el resto\n"
            f"como 'no verificado' (esto no afecta a tu cuenta). [s/N]: "
        ).strip().lower()
        hacer_verificacion = respuesta in ("s", "si", "sí", "y", "yes")

    activas = list(no_te_siguen_de_vuelta)
    fantasma = []
    no_verificadas = []
    motivo_no_verificado = None

    if hacer_verificacion:
        if not hay_conexion_internet():
            print("No se ha detectado conexión a internet: se omite la comprobación.")
            activas = []
            no_verificadas = list(no_te_siguen_de_vuelta)
            motivo_no_verificado = "sin_conexion"
        elif not hay_playwright():
            print(
                "No se puede hacer la verificación en línea: falta instalar Playwright.\n"
                "Instálalo con estos dos comandos y vuelve a ejecutar el script:\n"
                "    pip install playwright\n"
                "    playwright install chromium"
            )
            activas = []
            no_verificadas = list(no_te_siguen_de_vuelta)
            motivo_no_verificado = "sin_playwright"
        else:
            print("Comprobando cuentas en Instagram (esto puede tardar varios minutos; puedes pulsar Ctrl+C para parar sin perder lo ya comprobado)...")
            activas, fantasma, no_verificadas, interrumpido = verificar_cuentas(no_te_siguen_de_vuelta)
            if interrumpido:
                motivo_no_verificado = "interrumpido"
            elif no_verificadas:
                motivo_no_verificado = "bloqueo"

            print()
            print(f"Cuentas que siguen activas: {len(activas)}")
            print(f"Cuentas que ya no existen o no son accesibles: {len(fantasma)}")
            print(f"Cuentas no verificadas: {len(no_verificadas)}")

    with open(output_file, "w", encoding="utf-8") as f:
        if not hacer_verificacion:
            f.write("Usuarios que sigues pero no te siguen de vuelta:\n\n")
            for usuario in no_te_siguen_de_vuelta:
                f.write(f"https://instagram.com/{usuario}\n")
        else:
            f.write("Usuarios que sigues pero no te siguen de vuelta\n")
            f.write("(comprobado contra Instagram sin usar tu login):\n\n")

            f.write(f"--- Cuentas activas que no te siguen de vuelta ({len(activas)}) ---\n\n")
            for usuario in activas:
                f.write(f"https://instagram.com/{usuario}\n")

            if fantasma:
                f.write(f"\n--- Cuentas que ya no existen o no son accesibles ({len(fantasma)}) ---\n")
                f.write("(eliminadas, desactivadas, suspendidas, o que te han bloqueado)\n\n")
                for usuario in fantasma:
                    f.write(f"https://instagram.com/{usuario}\n")

            if no_verificadas:
                f.write(f"\n--- No verificadas ({len(no_verificadas)}) ---\n")
                if motivo_no_verificado == "sin_conexion":
                    f.write("No se detectó conexión a internet, así que estas cuentas\n")
                    f.write("no se han podido comprobar contra Instagram.\n\n")
                elif motivo_no_verificado == "sin_playwright":
                    f.write("Falta instalar Playwright para poder hacer esta comprobación\n")
                    f.write("(pip install playwright && playwright install chromium).\n")
                    f.write("Instálalo y vuelve a ejecutar el script para comprobar estas\n")
                    f.write("cuentas.\n\n")
                elif motivo_no_verificado == "interrumpido":
                    f.write("Interrumpiste la comprobación (Ctrl+C) antes de terminar, así\n")
                    f.write("que estas cuentas no se llegaron a comprobar. Vuelve a\n")
                    f.write("ejecutar el script cuando quieras para comprobar el resto.\n\n")
                else:
                    f.write("Instagram empezó a limitar/bloquear las comprobaciones a\n")
                    f.write("mitad de proceso, así que estas cuentas no se llegaron a\n")
                    f.write("comprobar. Puedes volver a ejecutar el script más tarde\n")
                    f.write("para reintentarlo.\n\n")
                for usuario in no_verificadas:
                    f.write(f"https://instagram.com/{usuario}\n")

        f.write(
            "\n---\n"
            "Nota: si al abrir alguno de estos enlaces Instagram dice que la\n"
            "página no está disponible, no es un error del script: puede\n"
            "tratarse de una cuenta eliminada, desactivada o suspendida, o de\n"
            "una cuenta que te ha bloqueado. Instagram no elimina ese usuario\n"
            "de tus datos exportados solo por eso, así que sigue apareciendo\n"
            "aquí aunque el enlace ya no funcione.\n\n"
            "Consejo: para dejar de seguir a estas cuentas, hazlo desde tu\n"
            "perfil > Siguiendo, en vez de buscarlas con la barra de\n"
            "búsqueda de Instagram. Las cuentas eliminadas, suspendidas o que\n"
            "te han bloqueado no aparecen en los resultados de búsqueda, pero\n"
            "siguen visibles (y se pueden dejar de seguir) en tu lista de\n"
            "Siguiendo.\n"
        )

    print()
    print(f"Archivo creado: {output_file}")


if __name__ == "__main__":
    main()