# Sobre los datos de esta rama

Esta rama (`demo`) es una excepción deliberada a la política normal del proyecto de no subir nunca datos personales al repositorio.

`followers_1.json`, `following.json` y `personal_information.json` en esta rama **no son datos reales**: son un export sintético, generado sustituyendo cada nombre de usuario real de un export auténtico por un identificador aleatorio (`cuenta_demo_0001`, `cuenta_demo_0002`, ...), conservando exactamente la misma estructura y las mismas relaciones de seguimiento que el export original, para que el resultado del script tenga un perfil realista (mismos totales: 813 seguidos, 1217 seguidores, 301 que no siguen de vuelta) sin exponer a ninguna persona real.

`ejemplo_resultado_demo.txt`, `.csv` y `.json` son la salida real de ejecutar:

```bash
python checker.py --no-verify --format txt
python checker.py --no-verify --format csv
python checker.py --no-verify --format json
```

sobre esos datos ficticios, incluidos aquí para que se pueda ver el resultado del script sin necesidad de ejecutarlo.

Si quieres probar la [verificación en línea](README.es.md#verificación-opcional-en-línea-cuentas-que-ya-no-existen) (`--verify`) con estos datos, funcionará de verdad: el script consultará Instagram por cada `cuenta_demo_XXXX`, y como esas cuentas no existen, las marcará (correctamente) como cuentas fantasma — es una forma más de comprobar que esa parte del script también funciona, sin usar cuentas de nadie.

La rama `main` sigue sin llevar nunca datos personales, reales ni ficticios: esta rama existe solo como demostración.
