"""Coordina la ingesta, análisis, transformación, puntaje y calendario."""

import csv
import json
import os
from datetime import date, datetime
from pathlib import Path

from .calendario import programar
from .diagnostico import diagnosticar
from .historial import cargar_historial, tema_de
from .ingesta import cargar_madre
from .puntaje import calificar, entrenar
from .transformacion import transformar
from .vista import generar_html


RAIZ_PROYECTO = Path(__file__).resolve().parents[1]


def _leer_json(ruta):
    """Carga un archivo JSON en UTF-8."""
    with open(ruta, encoding="utf-8") as archivo:
        return json.load(archivo)


def _guardar_json(carpeta, nombre, contenido):
    """Guarda un resultado JSON con formato legible."""
    ruta = carpeta / nombre
    with open(ruta, "w", encoding="utf-8") as archivo:
        json.dump(contenido, archivo, ensure_ascii=False, indent=2, default=str)


def _leer_calendario_ocupado(ruta):
    with open(ruta, encoding="utf-8-sig", newline="") as archivo:
        return list(csv.DictReader(archivo))


def _combinar_agendas(publicaciones_previas, publicaciones_nuevas):
    """Convierte las fechas a date y combina registros existentes y nuevos."""
    agenda_completa = []

    for publicacion in publicaciones_previas:
        agenda_completa.append(
            {
                "fecha": date.fromisoformat(publicacion["fecha"]),
                "hora": publicacion["hora"],
                "formato": publicacion["formato"],
                "tema": publicacion["tema"],
                "titulo": publicacion["titulo"],
                "estado": "agendada",
                "puntaje": None,
            }
        )

    for publicacion in publicaciones_nuevas:
        agenda_completa.append(
            {
                **publicacion,
                "fecha": date.fromisoformat(str(publicacion["fecha"])),
            }
        )

    return agenda_completa


def _detectar_conflictos(agenda, separacion_minima_horas):
    """Comprueba que las publicaciones de un mismo tema mantengan su distancia."""
    conflictos = []

    for indice, primera in enumerate(agenda):
        for segunda in agenda[indice + 1 :]:
            if primera["tema"] != segunda["tema"]:
                continue

            fecha_hora_primera = datetime.combine(
                primera["fecha"], datetime.strptime(primera["hora"], "%H:%M").time()
            )
            fecha_hora_segunda = datetime.combine(
                segunda["fecha"], datetime.strptime(segunda["hora"], "%H:%M").time()
            )
            diferencia = abs((fecha_hora_primera - fecha_hora_segunda).total_seconds())

            if diferencia < separacion_minima_horas * 3600:
                conflictos.append(
                    f"{primera['titulo']} / {segunda['titulo']}: "
                    "separación menor a la permitida."
                )

    return conflictos


def _guardar_piezas_markdown(ruta, piezas):
    with open(ruta, "w", encoding="utf-8") as archivo:
        for pieza in piezas:
            archivo.write(
                f"## {pieza['id']} — {pieza['estado']}\n\n"
                f"{pieza['texto']}\n\n"
            )
            if pieza["problemas"]:
                problemas = "; ".join(pieza["problemas"])
                archivo.write(f"Revisar: {problemas}\n\n")


def ejecutar(url, respaldo, insumos, salida):
    """Ejecuta el flujo completo y devuelve un resumen de resultados."""
    carpeta_insumos = Path(insumos)
    carpeta_salida = Path(salida)
    carpeta_salida.mkdir(parents=True, exist_ok=True)

    configuracion = _leer_json(carpeta_insumos / "configuracion" / "config.json")
    ventana = _leer_json(carpeta_insumos / "calendario" / "ventana.json")
    calendario_ocupado = _leer_calendario_ocupado(
        carpeta_insumos / "calendario" / "calendario_ocupado.csv"
    )

    historial, reporte_historial = cargar_historial(
        carpeta_insumos / "historial" / "historial_publicaciones.csv"
    )
    documento = cargar_madre(url, respaldo)
    tema_principal = tema_de(documento.texto, configuracion)
    diagnostico = diagnosticar(documento, configuracion)
    piezas = transformar(
        documento,
        configuracion,
        tema_principal,
        ventana["inicio"][:7].replace("-", ""),
    )

    modelo_puntaje = entrenar(historial)

    def calcular_puntaje(pieza, hora):
        resultado = calificar(
            modelo_puntaje,
            pieza["formato"],
            hora,
            pieza["tema"],
        )
        return resultado["puntaje"]

    agenda_nueva, piezas_no_ubicadas = programar(
        piezas,
        calendario_ocupado,
        ventana,
        configuracion,
        calcular_puntaje,
    )

    for publicacion in agenda_nueva:
        publicacion["estimacion"] = calificar(
            modelo_puntaje,
            publicacion["formato"],
            publicacion["hora"],
            publicacion["tema"],
        )

    _guardar_json(carpeta_salida, "diagnostico.json", diagnostico)
    _guardar_json(carpeta_salida, "piezas_derivadas.json", piezas)
    _guardar_json(
        carpeta_salida,
        "calendario.json",
        {
            "ventana": ventana,
            "programadas": agenda_nueva,
            "no_ubicadas": piezas_no_ubicadas,
            "ya_agendadas": calendario_ocupado,
        },
    )
    _guardar_json(
        carpeta_salida,
        "puntaje.json",
        {
            "metodo": (
                "Tasa de interacción histórica por formato, hora y tema. "
                "Se aplica suavizado con cinco observaciones equivalentes "
                "a la media global; puntaje = tasa estimada × 1000, "
                "limitado a 0–100."
            ),
            "modelo": {
                "media_global": modelo_puntaje["media_global"],
                "muestras": modelo_puntaje["n"],
            },
            "calidad_historial": reporte_historial,
            "piezas": agenda_nueva,
        },
    )

    agenda_completa = _combinar_agendas(calendario_ocupado, agenda_nueva)
    conflictos = _detectar_conflictos(
        agenda_completa,
        configuracion["calendario"]["separacion_minima_mismo_tema_horas"],
    )

    inicio = date.fromisoformat(ventana["inicio"])
    fin = date.fromisoformat(ventana["fin"])
    carpeta_web = RAIZ_PROYECTO / "web"
    ruta_recursos = Path(os.path.relpath(carpeta_web, carpeta_salida.resolve())).as_posix()
    documento_html = generar_html(
        inicio,
        fin,
        agenda_completa,
        piezas_no_ubicadas,
        conflictos,
        asset_base=ruta_recursos,
    )

    with open(carpeta_salida / "calendario.html", "w", encoding="utf-8") as archivo:
        archivo.write(documento_html)

    _guardar_piezas_markdown(carpeta_salida / "piezas_derivadas.md", piezas)

    return {
        "piezas": len(piezas),
        "programadas": len(agenda_nueva),
        "no_ubicadas": len(piezas_no_ubicadas),
        "fuente": documento.fuente,
        "alertas": len(diagnostico["alertas"]),
    }
