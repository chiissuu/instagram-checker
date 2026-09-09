import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import checker


class TestLimpiarUsuario(unittest.TestCase):
    def test_quita_espacios_arroba_y_pone_minusculas(self):
        self.assertEqual(checker.limpiar_usuario("  @Usuario_Test "), "usuario_test")

    def test_valores_vacios_devuelven_none(self):
        self.assertIsNone(checker.limpiar_usuario(""))
        self.assertIsNone(checker.limpiar_usuario(None))
        self.assertIsNone(checker.limpiar_usuario("   "))
        self.assertIsNone(checker.limpiar_usuario("@"))


class TestExtraerUsuarioDesdeHref(unittest.TestCase):
    def test_url_normal(self):
        self.assertEqual(
            checker.extraer_usuario_desde_href("https://www.instagram.com/alguien/"),
            "alguien",
        )

    def test_url_con_query_string(self):
        self.assertEqual(
            checker.extraer_usuario_desde_href("https://www.instagram.com/alguien?hl=en"),
            "alguien",
        )

    def test_formato_con_prefijo_u(self):
        self.assertEqual(
            checker.extraer_usuario_desde_href("https://www.instagram.com/_u/alguien/"),
            "alguien",
        )

    def test_href_vacio_devuelve_none(self):
        self.assertIsNone(checker.extraer_usuario_desde_href(""))
        self.assertIsNone(checker.extraer_usuario_desde_href(None))


class TestExtraerFollowers(unittest.TestCase):
    def test_lee_usuarios_desde_string_list_data(self):
        data = [
            {
                "string_list_data": [
                    {"href": "https://www.instagram.com/persona_uno/", "value": "persona_uno", "timestamp": 1},
                ]
            },
            {
                # Sin "value": debe caer al usuario extraído del href.
                "string_list_data": [
                    {"href": "https://www.instagram.com/persona_dos/", "timestamp": 2},
                ]
            },
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "followers_1.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            resultado = checker.extraer_followers(path)

        self.assertEqual(resultado, {"persona_uno", "persona_dos"})


class TestExtraerFollowing(unittest.TestCase):
    def test_lee_usuarios_desde_relationships_following(self):
        data = {
            "relationships_following": [
                {
                    "title": "persona_tres",
                    "string_list_data": [
                        {"href": "https://www.instagram.com/persona_tres/", "timestamp": 1},
                    ],
                },
            ]
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "following.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            resultado = checker.extraer_following(path)

        self.assertEqual(resultado, {"persona_tres"})

    def test_sin_relationships_following_devuelve_vacio(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "following.json"
            path.write_text(json.dumps({}), encoding="utf-8")
            resultado = checker.extraer_following(path)

        self.assertEqual(resultado, set())


class TestNombreArchivoSeguro(unittest.TestCase):
    def test_sustituye_caracteres_no_validos(self):
        self.assertEqual(checker.nombre_archivo_seguro('usuario:test/raro?'), "usuario_test_raro")


class TestSepararPorCache(unittest.TestCase):
    def test_clasifica_segun_estado_guardado_en_cache(self):
        cache = {
            "activo": {"estado": "existe", "verificado_en": "2026-01-01T00:00:00+00:00"},
            "fantasma_uno": {"estado": "no_existe", "verificado_en": "2026-01-01T00:00:00+00:00"},
            "dudoso": {"estado": "no_verificable", "verificado_en": "2026-01-01T00:00:00+00:00"},
        }

        ya_activas, ya_fantasma, a_reintentar, nuevas = checker.separar_por_cache(
            ["activo", "fantasma_uno", "dudoso", "nunca_visto"], cache
        )

        self.assertEqual(ya_activas, ["activo"])
        self.assertEqual(ya_fantasma, ["fantasma_uno"])
        self.assertEqual(a_reintentar, ["dudoso"])
        self.assertEqual(nuevas, ["nunca_visto"])


class TestConstruirFilas(unittest.TestCase):
    def test_sin_verificacion_todas_van_como_sin_verificar(self):
        filas = checker.construir_filas(["a", "b"], False, [], [], [], None)

        self.assertEqual([f.categoria for f in filas], ["sin_verificar", "sin_verificar"])

    def test_con_verificacion_separa_por_categoria(self):
        filas = checker.construir_filas(
            ["a", "b", "c"], True, activas=["a"], fantasma=["b"], no_verificadas=["c"], motivo_no_verificado="bloqueo"
        )

        por_usuario = {f.usuario: (f.categoria, f.motivo) for f in filas}
        self.assertEqual(por_usuario["a"], ("activa", None))
        self.assertEqual(por_usuario["b"], ("fantasma", None))
        self.assertEqual(por_usuario["c"], ("no_verificada", "bloqueo"))


if __name__ == "__main__":
    unittest.main()
