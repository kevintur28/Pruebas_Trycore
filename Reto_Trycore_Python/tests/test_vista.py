import unittest
from datetime import date
from pathlib import Path

from mercadeo.vista import generar_html, RAIZ_PROYECTO


class VistaTests(unittest.TestCase):
    def test_enlaza_css_y_javascript_externos(self):
        html = generar_html(date(2026, 11, 30), date(2026, 12, 11), [], [], [])
        self.assertIn('href="../web/css/calendario.css"', html)
        self.assertIn('src="../web/js/calendario.js"', html)
        self.assertNotIn("<style", html)
        self.assertNotIn("onclick=", html)

    def test_recursos_separados_existen(self):
        self.assertTrue((RAIZ_PROYECTO / "web" / "plantillas" / "calendario.html").is_file())
        self.assertTrue((RAIZ_PROYECTO / "web" / "css" / "calendario.css").is_file())
        self.assertTrue((RAIZ_PROYECTO / "web" / "js" / "calendario.js").is_file())

    def test_texto_dinamico_escapado(self):
        agenda = [{
            "fecha": date(2026, 12, 1),
            "hora": "08:30",
            "formato": "post_linkedin",
            "tema": "rpa",
            "titulo": "Título <prueba>",
            "estado": "pendiente_aprobacion",
            "puntaje": 41,
        }]
        html = generar_html(date(2026, 11, 30), date(2026, 12, 11), agenda, [], [])
        self.assertIn("Título &lt;prueba&gt;", html)
        self.assertIn('data-format="post_linkedin"', html)
        self.assertIn("Puntaje 41/100", html)


if __name__ == "__main__":
    unittest.main()
