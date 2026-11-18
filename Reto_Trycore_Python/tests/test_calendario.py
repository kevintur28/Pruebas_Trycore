import json
import os
import unittest

from mercadeo.calendario import programar

BASE = os.path.dirname(os.path.dirname(__file__))


def cargar_config():
    ruta = os.path.join(BASE, "insumos", "configuracion", "config.json")
    with open(ruta, encoding="utf-8") as archivo:
        return json.load(archivo)


class CalendarioTests(unittest.TestCase):
    def test_no_programa_en_festivo(self):
        cfg = cargar_config()
        ventana = {"inicio": "2026-12-08", "fin": "2026-12-08"}
        pieza = {
            "id": "p1", "estado": "pendiente_aprobacion", "formato": "post_linkedin",
            "tema": "rpa", "partes": {"gancho": "Prueba"}, "problemas": [],
        }
        agenda, no = programar([pieza], [], ventana, cfg, lambda p, h: 50)
        self.assertEqual(agenda, [])
        self.assertEqual(len(no), 1)

    def test_respeta_capacidad_diaria(self):
        cfg = cargar_config()
        ventana = {"inicio": "2026-11-30", "fin": "2026-11-30"}
        piezas = [
            {
                "id": f"p{i}", "estado": "pendiente_aprobacion", "formato": "post_linkedin",
                "tema": f"tema{i}", "partes": {"gancho": "Gancho"}, "problemas": [],
            }
            for i in range(3)
        ]
        agenda, no = programar(piezas, [], ventana, cfg, lambda p, h: 50)
        self.assertLessEqual(len(agenda), cfg["calendario"]["capacidad_max_por_dia"])
