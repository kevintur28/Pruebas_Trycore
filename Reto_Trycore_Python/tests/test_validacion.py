import json
import os
import unittest

from mercadeo.validacion import buscar_terminos, buscar_confidenciales, slug

BASE = os.path.dirname(os.path.dirname(__file__))
CFG_PATH = os.path.join(BASE, "insumos", "configuracion", "config.json")
with open(CFG_PATH, encoding="utf-8") as archivo:
    CFG = json.load(archivo)


class ValidacionTests(unittest.TestCase):
    def test_detecta_termino_prohibido(self):
        self.assertTrue(buscar_terminos("integración inmediata con cualquier ERP", CFG))

    def test_detecta_cliente_confidencial(self):
        self.assertIn("Banco Andino del Sur", buscar_confidenciales("Proyecto Banco Andino del Sur", CFG))

    def test_slug(self):
        self.assertEqual(slug("Guía de Automatización RPA"), "guia-de-automatizacion-rpa")
