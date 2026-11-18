import unittest, os
from mercadeo.historial import fecha, booleano, cargar_historial
BASE=os.path.dirname(os.path.dirname(__file__))
class HistorialTests(unittest.TestCase):
    def test_fecha_iso(self): self.assertEqual(str(fecha("2026-03-05")),"2026-03-05")
    def test_fecha_colombiana(self): self.assertEqual(str(fecha("16/03/2026")),"2026-03-16")
    def test_fecha_mes_espanol(self): self.assertEqual(str(fecha("17-mar-2026")),"2026-03-17")
    def test_booleanos(self):
        self.assertTrue(booleano("sí")); self.assertTrue(booleano("1")); self.assertFalse(booleano("No"))
    def test_deduplica_historial(self):
        rows,rep=cargar_historial(os.path.join(BASE,"insumos","historial","historial_publicaciones.csv"))
        self.assertGreater(len(rows),40); self.assertGreater(rep["duplicados_omitidos"],0)
