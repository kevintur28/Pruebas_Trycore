import unittest
from mercadeo.puntaje import entrenar,calificar
class PuntajeTests(unittest.TestCase):
    def test_puntaje_entre_cero_y_cien(self):
        rows=[{"tasa_normalizada":.04,"canal":"linkedin","formato":"post_linkedin","tema":"rpa","hora":"08:30"}]
        m=entrenar(rows); r=calificar(m,"post_linkedin","08:30","rpa")
        self.assertGreaterEqual(r["puntaje"],0); self.assertLessEqual(r["puntaje"],100)
    def test_sin_historial_usa_media(self):
        m=entrenar([]); r=calificar(m,"newsletter","11:00","general")
        self.assertEqual(r["puntaje"],30)
