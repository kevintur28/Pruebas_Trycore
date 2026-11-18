"""Punto de entrada del sistema táctico de contenidos Trycore."""

import argparse
import os

from mercadeo.pipeline import ejecutar


def construir_argumentos():
    parser = argparse.ArgumentParser(
        description="Sistema táctico de contenidos Trycore"
    )
    parser.add_argument(
        "--url",
        default=None,
        help="URL de la pieza madre; por defecto usa insumos/pieza_madre/url.txt",
    )
    parser.add_argument("--insumos", default="insumos", help="Carpeta de archivos de entrada")
    parser.add_argument("--salida", default="salidas", help="Carpeta donde se guardan los resultados")
    parser.add_argument(
        "--sin-respaldo",
        action="store_true",
        help="No usar el HTML local si falla la descarga de la URL",
    )
    return parser


def main():
    argumentos = construir_argumentos().parse_args()

    if argumentos.url:
        url = argumentos.url
    else:
        ruta_url = os.path.join(argumentos.insumos, "pieza_madre", "url.txt")
        with open(ruta_url, encoding="utf-8") as archivo:
            url = archivo.read().strip()

    respaldo = None
    if not argumentos.sin_respaldo:
        respaldo = os.path.join(
            argumentos.insumos,
            "pieza_madre",
            "guia_rpa_respaldo.html",
        )

    resumen = ejecutar(url, respaldo, argumentos.insumos, argumentos.salida)

    print("Ejecución terminada")
    for nombre, valor in resumen.items():
        print(f"{nombre}: {valor}")
    print(f"Archivos generados en: {argumentos.salida}/")


if __name__ == "__main__":
    main()
