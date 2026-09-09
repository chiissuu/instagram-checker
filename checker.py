from __future__ import annotations

import argparse
import csv
import json
import random
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.sync_api import Page

BASE_DIR = Path(__file__).resolve().parent

TITULO_PERFIL_NO_DISPONIBLE = "Profile isn't available • Instagram"
TEXTO_PERFIL_NO_DISPONIBLE = "Sorry, this page isn't available."
PAUSA_MINIMA_SEGUNDOS = 2
PAUSA_MAXIMA_SEGUNDOS = 5
MAX_FALLOS_SEGUIDOS = 3  # comprobaciones sin resultado claro seguidas antes de darse por bloqueado
CACHE_PATH = BASE_DIR / "verificacion_cache.json"


# --------------------------------------------------------------------------
# Lectura de los datos exportados por Instagram
# --------------------------------------------------------------------------

def limpiar_usuario(usuario: str | None) -> str | None:
    if not usuario:
        return None

    usuario = usuario.strip().lower()
    usuario = usuario.replace("@", "")

    if not usuario:
        return None

    return usuario


def extraer_usuario_desde_href(href: str | None) -> str | None:
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


def extraer_followers(path: Path) -> set[str]:
    """
    Extrae usuarios desde followers_1.json.
    Normalmente Instagram guarda aquí el username en string_list_data -> value.
    """
    data = json.loads(path.read_text(encoding="utf-8"))
    usuarios: set[str] = set()

    def recorrer(obj: object) -> None:
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


def extraer_following(path: Path) -> set[str]:
    """
    Extrae usuarios desde following.json.
    En algunas exportaciones Instagram guarda los usuarios en:
    relationships_following -> title
    y no dentro de value.
    """
    data = json.loads(path.read_text(encoding="utf-8"))
    usuarios: set[str] = set()

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


def buscar_nombre_cuenta() -> str | None:
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

        resultado: str | None = None

        def recorrer(obj: object) -> None:
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


def nombre_archivo_seguro(texto: str) -> str:
    return re.sub(r'[\\/*?:"<>|\s]', "_", texto).strip("_")


def buscar_archivo_exacto(nombre_archivo: str) -> list[Path]:
    encontrados = [
        archivo
        for archivo in BASE_DIR.rglob("*.json")
        if archivo.name.lower() == nombre_archivo.lower()
    ]

    return encontrados


# --------------------------------------------------------------------------
# Caché de verificación (evita re-comprobar en Instagram lo ya comprobado)
# --------------------------------------------------------------------------

def cargar_cache() -> dict[str, dict[str, str]]:
    if not CACHE_PATH.exists():
        return {}

    try:
        return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def guardar_cache(cache: dict[str, dict[str, str]]) -> None:
    try:
        CACHE_PATH.write_text(json.dumps(cache, indent=2, ensure_ascii=False), encoding="utf-8")
    except OSError:
        pass


def actualizar_cache(cache: dict[str, dict[str, str]], usuario: str, estado: str) -> None:
    cache[usuario] = {
        "estado": estado,
        "verificado_en": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    guardar_cache(cache)


def separar_por_cache(
    usuarios: list[str], cache: dict[str, dict[str, str]]
) -> tuple[list[str], list[str], list[str], list[str]]:
    """
    Divide una lista de usuarios según lo que ya sabe la caché de
    ejecuciones anteriores.

    Devuelve: (ya_activas, ya_fantasma, a_reintentar, nuevas)
    - ya_activas / ya_fantasma: ya se comprobaron antes, no hace falta repetir.
    - a_reintentar: quedaron como "no_verificable" la última vez.
    - nuevas: nunca se comprobaron.
    """
    ya_activas: list[str] = []
    ya_fantasma: list[str] = []
    a_reintentar: list[str] = []
    nuevas: list[str] = []

    for usuario in usuarios:
        entrada = cache.get(usuario)

        if not entrada:
            nuevas.append(usuario)
            continue

        estado = entrada.get("estado")

        if estado == "existe":
            ya_activas.append(usuario)
        elif estado == "no_existe":
            ya_fantasma.append(usuario)
        else:
            a_reintentar.append(usuario)

    return ya_activas, ya_fantasma, a_reintentar, nuevas


# --------------------------------------------------------------------------
# Verificación en línea (Playwright)
# --------------------------------------------------------------------------

def hay_conexion_internet() -> bool:
    try:
        urllib.request.urlopen("https://www.instagram.com", timeout=6)
        return True
    except (urllib.error.URLError, OSError):
        return False


def hay_playwright() -> bool:
    try:
        import playwright.sync_api  # noqa: F401
        return True
    except ImportError:
        return False


def verificar_cuenta_instagram(pagina: "Page", usuario: str) -> str:
    """
    Comprueba, sin iniciar sesión, si el perfil de un usuario sigue
    existiendo/siendo accesible, cargando su página real con un
    navegador (igual que haría una persona), no la API interna.

    Usa dos señales independientes para detectar un perfil inexistente
    (el título de la pestaña y un texto del propio contenido de la
    página) para que el script no dependa de una sola de las dos si
    Instagram cambia el texto de alguna.

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

        try:
            if pagina.get_by_text(TEXTO_PERFIL_NO_DISPONIBLE, exact=False).count() > 0:
                return "no_existe"
        except Exception:
            pass  # la comprobación del DOM es un extra: si falla, se sigue solo con el título

        if titulo and titulo != "Instagram":
            return "existe"

        return "no_verificable"

    except Exception:
        return "no_verificable"


def verificar_cuentas(
    usuarios: list[str], cache: dict[str, dict[str, str]]
) -> tuple[list[str], list[str], list[str], bool]:
    """
    Comprueba una lista de usuarios abriendo su perfil real en un
    navegador (Playwright), con una pausa aleatoria entre cada uno. Cada
    resultado se guarda en la caché al momento, así que interrumpir con
    Ctrl+C nunca pierde progreso, ni siquiera entre distintas ejecuciones
    del script. Si varias comprobaciones seguidas no dan un resultado
    claro (señal de que Instagram ha empezado a poner trabas), se
    detiene. Nunca inicia sesión con la cuenta del usuario.

    Devuelve: (activas, fantasma, no_verificadas, interrumpido)
    """
    from playwright.sync_api import sync_playwright

    activas: list[str] = []
    fantasma: list[str] = []
    no_verificadas: list[str] = []
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

                actualizar_cache(cache, usuario, resultado)

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


# --------------------------------------------------------------------------
# Construcción y escritura del resultado
# --------------------------------------------------------------------------

@dataclass
class Fila:
    usuario: str
    categoria: str  # "sin_verificar" | "activa" | "fantasma" | "no_verificada"
    motivo: str | None = None


MOTIVOS_NO_VERIFICADO = {
    "sin_conexion": (
        "No se detectó conexión a internet, así que estas cuentas no se han podido comprobar contra Instagram."
    ),
    "sin_playwright": (
        "Falta instalar Playwright para poder hacer esta comprobación "
        "(pip install -r requirements-optional.txt && playwright install chromium)."
    ),
    "interrumpido": "Interrumpiste la comprobación (Ctrl+C) antes de terminar con estas cuentas.",
    "bloqueo": "Instagram empezó a limitar/bloquear las comprobaciones antes de llegar a estas cuentas.",
}


def construir_filas(
    no_te_siguen_de_vuelta: list[str],
    hacer_verificacion: bool,
    activas: list[str],
    fantasma: list[str],
    no_verificadas: list[str],
    motivo_no_verificado: str | None,
) -> list[Fila]:
    if not hacer_verificacion:
        return [Fila(usuario=u, categoria="sin_verificar") for u in no_te_siguen_de_vuelta]

    filas = [Fila(usuario=u, categoria="activa") for u in activas]
    filas += [Fila(usuario=u, categoria="fantasma") for u in fantasma]
    filas += [Fila(usuario=u, categoria="no_verificada", motivo=motivo_no_verificado) for u in no_verificadas]
    return filas


def escribir_txt(output_path: Path, filas: list[Fila], hacer_verificacion: bool) -> None:
    activas = [f.usuario for f in filas if f.categoria in ("sin_verificar", "activa")]
    fantasma = [f.usuario for f in filas if f.categoria == "fantasma"]
    no_verificadas = [f for f in filas if f.categoria == "no_verificada"]

    with open(output_path, "w", encoding="utf-8") as f:
        if not hacer_verificacion:
            f.write("Usuarios que sigues pero no te siguen de vuelta:\n\n")
            for usuario in activas:
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
                motivo = no_verificadas[0].motivo
                f.write(MOTIVOS_NO_VERIFICADO.get(motivo, MOTIVOS_NO_VERIFICADO["bloqueo"]) + "\n\n")
                for fila in no_verificadas:
                    f.write(f"https://instagram.com/{fila.usuario}\n")

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


def escribir_csv(output_path: Path, filas: list[Fila]) -> None:
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["usuario", "url", "categoria", "motivo_no_verificado"])
        for fila in filas:
            writer.writerow([
                fila.usuario,
                f"https://instagram.com/{fila.usuario}",
                fila.categoria,
                fila.motivo or "",
            ])


def escribir_json(output_path: Path, filas: list[Fila]) -> None:
    data = [
        {
            "usuario": fila.usuario,
            "url": f"https://instagram.com/{fila.usuario}",
            "categoria": fila.categoria,
            "motivo_no_verificado": fila.motivo,
        }
        for fila in filas
    ]
    output_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


# --------------------------------------------------------------------------
# CLI y punto de entrada
# --------------------------------------------------------------------------

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compara tus seguidores y seguidos de Instagram a partir del export oficial de tus datos."
    )
    grupo_verificacion = parser.add_mutually_exclusive_group()
    grupo_verificacion.add_argument(
        "--verify", action="store_true",
        help="Activa la verificación en línea (Playwright) sin preguntar por teclado.",
    )
    grupo_verificacion.add_argument(
        "--no-verify", action="store_true",
        help="Desactiva la verificación en línea sin preguntar por teclado.",
    )
    parser.add_argument(
        "--format", choices=["txt", "csv", "json"], default="txt",
        help="Formato del archivo de salida (por defecto: txt).",
    )
    return parser.parse_args(argv)


def main() -> None:
    args = parse_args()

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

    followers: set[str] = set()
    following: set[str] = set()

    for archivo in archivos_followers:
        followers.update(extraer_followers(archivo))

    for archivo in archivos_following:
        following.update(extraer_following(archivo))

    no_te_siguen_de_vuelta = sorted(following - followers)

    nombre_cuenta = buscar_nombre_cuenta()
    if not nombre_cuenta:
        entrada = input(
            "No se ha podido detectar tu nombre de usuario automáticamente.\n"
            "Escribe tu nombre de usuario de Instagram (se usará para nombrar el archivo): "
        )
        nombre_cuenta = limpiar_usuario(entrada) or "cuenta_desconocida"

    nombre_base = f"personas_que_no_te_siguen_de_vuelta_instagram_{nombre_archivo_seguro(nombre_cuenta)}"
    output_file = BASE_DIR / f"{nombre_base}.{args.format}"

    print("Resumen:")
    print(f"Personas a las que sigues: {len(following)}")
    print(f"Personas que te siguen: {len(followers)}")
    print(f"No te siguen de vuelta: {len(no_te_siguen_de_vuelta)}")

    if args.verify:
        hacer_verificacion = bool(no_te_siguen_de_vuelta)
    elif args.no_verify:
        hacer_verificacion = False
    elif no_te_siguen_de_vuelta:
        segundos_por_cuenta = (PAUSA_MINIMA_SEGUNDOS + PAUSA_MAXIMA_SEGUNDOS) / 2 + 2.5  # + tiempo de carga de la página
        estimado_minutos = round(len(no_te_siguen_de_vuelta) * segundos_por_cuenta / 60, 1)
        respuesta = input(
            f"\n¿Quieres que el script abra cada perfil de esas {len(no_te_siguen_de_vuelta)}\n"
            f"cuentas en un navegador (sin iniciar sesión con la tuya) para comprobar\n"
            f"cuáles ya no existen (eliminadas, suspendidas o que te han bloqueado)?\n"
            f"Necesita tener Playwright instalado (pip install -r requirements-optional.txt\n"
            f"&& playwright install chromium) y conexión a internet, y tardaría unos\n"
            f"{estimado_minutos} minutos (menos si ya hay cuentas comprobadas en ejecuciones\n"
            f"anteriores). Si Instagram empieza a poner trabas se para sola y deja el resto\n"
            f"como 'no verificado' (esto no afecta a tu cuenta). [s/N]: "
        ).strip().lower()
        hacer_verificacion = respuesta in ("s", "si", "sí", "y", "yes")
    else:
        hacer_verificacion = False

    activas = list(no_te_siguen_de_vuelta)
    fantasma: list[str] = []
    no_verificadas: list[str] = []
    motivo_no_verificado: str | None = None

    if hacer_verificacion:
        if not hay_conexion_internet():
            print("No se ha detectado conexión a internet: se omite la comprobación.")
            activas = []
            no_verificadas = list(no_te_siguen_de_vuelta)
            motivo_no_verificado = "sin_conexion"
        elif not hay_playwright():
            print(
                "No se puede hacer la verificación en línea: falta instalar Playwright.\n"
                "Instálalo con estos comandos y vuelve a ejecutar el script:\n"
                "    pip install -r requirements-optional.txt\n"
                "    playwright install chromium"
            )
            activas = []
            no_verificadas = list(no_te_siguen_de_vuelta)
            motivo_no_verificado = "sin_playwright"
        else:
            cache = cargar_cache()
            ya_activas, ya_fantasma, a_reintentar, nuevas = separar_por_cache(no_te_siguen_de_vuelta, cache)
            a_verificar = a_reintentar + nuevas

            if a_reintentar:
                print(f"{len(a_reintentar)} cuenta(s) quedaron sin verificar en una ejecución anterior: se reintentan primero.")
            if ya_activas or ya_fantasma:
                print(f"{len(ya_activas) + len(ya_fantasma)} cuenta(s) ya estaban en la caché de verificaciones anteriores: no se vuelven a comprobar.")

            nuevas_activas: list[str] = []
            nuevas_fantasma: list[str] = []
            interrumpido = False

            if a_verificar:
                print("Comprobando cuentas en Instagram (esto puede tardar varios minutos; puedes pulsar Ctrl+C para parar sin perder lo ya comprobado)...")
                nuevas_activas, nuevas_fantasma, no_verificadas, interrumpido = verificar_cuentas(a_verificar, cache)

            activas = ya_activas + nuevas_activas
            fantasma = ya_fantasma + nuevas_fantasma

            if interrumpido:
                motivo_no_verificado = "interrumpido"
            elif no_verificadas:
                motivo_no_verificado = "bloqueo"

            print()
            print(f"Cuentas que siguen activas: {len(activas)}")
            print(f"Cuentas que ya no existen o no son accesibles: {len(fantasma)}")
            print(f"Cuentas no verificadas: {len(no_verificadas)}")

    filas = construir_filas(no_te_siguen_de_vuelta, hacer_verificacion, activas, fantasma, no_verificadas, motivo_no_verificado)

    if args.format == "csv":
        escribir_csv(output_file, filas)
    elif args.format == "json":
        escribir_json(output_file, filas)
    else:
        escribir_txt(output_file, filas, hacer_verificacion)

    print()
    print(f"Archivo creado: {output_file}")


if __name__ == "__main__":
    main()
