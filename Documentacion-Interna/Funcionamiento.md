# Funcionamiento

Cómo funciona `checker.py` por dentro. El propio archivo ya tiene cabeceras numeradas (`1 ·` a `6 ·`) y comentarios explicando las partes complejas — esto es el resumen para no tener que abrirlo.

## Flujo de datos, de principio a fin

1. **Localizar el export**: `buscar_archivo_exacto` busca recursivamente (`rglob`) `followers_1.json` y `following.json` en cualquier subcarpeta junto a `checker.py`, sin importar el nombre de la carpeta ni la profundidad. Instagram varía la estructura del export según el método de descarga.
2. **Extraer usuarios**: `extraer_followers` / `extraer_following` recorren el JSON **recursivamente** (no con una ruta fija) porque Instagram anida `string_list_data` a distinta profundidad según la versión del export. `extraer_usuario_desde_href` normaliza los dos formatos de URL que usa Instagram (`.../usuario` y `.../_u/usuario`).
3. **Calcular el resultado**: resta de conjuntos, `following - followers` = quién no te sigue de vuelta. (Antes también se calculaban `mutuos` y `te_siguen_pero_no_sigues`; se eliminaron por no usarse — el script solo tiene sentido para el primer cálculo.)
4. **Detectar el usuario propio**: `buscar_nombre_cuenta` busca `personal_information.json`; si no existe en el export, se pregunta por teclado.
5. **Verificación opcional en línea** (si se activa): ver sección dedicada abajo.
6. **Escribir el resultado**: `construir_filas` arma una lista de `Fila` (usuario + categoría + motivo), y según `--format` se llama a `escribir_txt` / `escribir_csv` / `escribir_json`. Las tres parten de los mismos datos, así que nunca pueden desincronizarse entre sí.

## La verificación en línea (Playwright)

- Abre cada perfil en un Chromium real y sin sesión iniciada — nunca llama a la API interna de Instagram (la API bloquea clientes automatizados casi al instante; cargar la página real no).
- Decide si una cuenta existe con **dos señales** (`verificar_cuenta_instagram`): el `<title>` de la pestaña, y un texto del propio contenido del DOM como respaldo. Si Instagram cambia una de las dos formas, la otra sigue funcionando. Esto no acelera nada (el cuello de botella es la carga de página + la pausa deliberada, no el chequeo en sí) — es solo resiliencia añadida.
- Pausa aleatoria de 2-5s entre cuenta y cuenta, a propósito, para no parecer un bot.
- `MAX_FALLOS_SEGUIDOS = 3`: si 3 comprobaciones seguidas dan "no_verificable" (no 3 en total, sino 3 **consecutivas**), se asume que Instagram está poniendo trabas y se para, dejando el resto como no verificado.
- Ctrl+C en cualquier momento no pierde progreso: cada resultado se guarda en la caché al momento (`actualizar_cache`), no al final.

## La caché (`verificacion_cache.json`)

Archivo junto a `checker.py` (gitignorado) con `{usuario: {estado, verificado_en}}`. En cada ejecución, `separar_por_cache` divide la lista a comprobar en 4 grupos:

- **ya_activas / ya_fantasma**: ya se sabían, no se tocan.
- **a_reintentar**: quedaron como `no_verificable` la última vez — se comprueban **primero**.
- **nuevas**: nunca se comprobaron — se comprueban después de los reintentos.

Efecto práctico: solo la primera ejecución con muchas cuentas es realmente lenta. Se decidió explícitamente NO reintentar dentro de la misma ejecución (ver Decisiones.md) — el reintento ocurre entre ejecuciones, gratis.

## CLI

`--verify` / `--no-verify` saltan la pregunta interactiva. `--format {txt,csv,json}` elige el formato de salida (por defecto txt). Sin flags, se comporta igual que la versión original (todo por teclado).

## Tests

`tests/test_checker.py`, `unittest` estándar (sin pytest, para no añadir una dependencia). Cubren las funciones puras: `limpiar_usuario`, `extraer_usuario_desde_href`, `extraer_followers`, `extraer_following`, `nombre_archivo_seguro`, `separar_por_cache`, `construir_filas`. No se testean `verificar_cuenta_instagram`/`verificar_cuentas` porque necesitan un navegador real — fuera de alcance para tests unitarios de este tamaño de proyecto.
