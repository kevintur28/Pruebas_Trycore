"""Construcción del HTML del calendario usando plantilla, CSS y JS externos."""

import html
from pathlib import Path
from datetime import timedelta

FORMATO_NOMBRES = {
    "post_linkedin": "Post LinkedIn",
    "carrusel_linkedin": "Carrusel LinkedIn",
    "newsletter": "Newsletter",
    "guion_video_corto": "Guion de video",
    "infografia": "Infografía",
    "caso_de_exito": "Caso de éxito",
}

RAIZ_PROYECTO = Path(__file__).resolve().parents[1]
RUTA_PLANTILLA = RAIZ_PROYECTO / "web" / "plantillas" / "calendario.html"


def _escapar(valor):
    return html.escape(str(valor), quote=True)


def _nombre_formato(formato):
    return FORMATO_NOMBRES.get(formato, formato.replace("_", " ").capitalize())


def _clase_formato(formato):
    """Devuelve una clase segura para las reglas CSS por tipo de pieza."""
    slug = "".join(
        caracter for caracter in formato.lower()
        if caracter.isalnum() or caracter == "_"
    )
    return f"format--{slug or 'sin_clasificar'}"


def _crear_semanas(inicio, fin, agenda):
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
    semanas = []
    lunes = inicio - timedelta(days=inicio.weekday())

    while lunes <= fin:
        celdas = []
        for indice_dia in range(5):
            fecha_dia = lunes + timedelta(days=indice_dia)
            if fecha_dia < inicio or fecha_dia > fin:
                continue

            publicaciones = [item for item in agenda if item["fecha"] == fecha_dia]
            tarjetas = []

            for publicacion in sorted(publicaciones, key=lambda item: item["hora"]):
                formato = publicacion["formato"]
                estado = publicacion.get("estado", "")
                es_registro_previo = estado == "agendada"
                nombre_estado = {
                    "agendada": "Ya estaba programada",
                    "pendiente_aprobacion": "Pendiente de aprobación",
                }.get(estado, estado.replace("_", " ").capitalize())

                if es_registro_previo:
                    puntaje_html = '<span class="score score-muted">Registro previo</span>'
                else:
                    puntaje_html = (
                        '<span class="score">Puntaje '
                        + _escapar(publicacion.get("puntaje", "—"))
                        + "/100</span>"
                    )

                tarjetas.append(
                    f'''<article class="event {_clase_formato(formato)}" data-format="{_escapar(formato)}">
                        <div class="event-top">
                            <span class="event-time">{_escapar(publicacion["hora"])}</span>
                            <span class="event-format">{_escapar(_nombre_formato(formato))}</span>
                        </div>
                        <h4>{_escapar(publicacion["titulo"])}</h4>
                        <div class="event-meta">
                            <span>Tema: {_escapar(publicacion["tema"])}</span>
                            <span class="status">{_escapar(nombre_estado)}</span>
                        </div>
                        <div class="event-bottom">{puntaje_html}</div>
                    </article>'''
                )

            contenido = "".join(tarjetas)
            mensaje_dia_libre = '<p class="empty">Día libre</p>' if not tarjetas else ""
            celdas.append(
                f'''<section class="day">
                    <div class="day-heading">
                        <h3>{dias[indice_dia]}</h3>
                        <span>{fecha_dia.strftime("%d/%m")}</span>
                    </div>
                    <div class="day-events">
                        {contenido}
                        {mensaje_dia_libre}
                        <p class="filter-empty" hidden>No hay piezas de este formato.</p>
                    </div>
                </section>'''
            )

        semanas.append(
            f'''<section class="week-section">
                <div class="week-title"><h2>Semana del {lunes.strftime("%d/%m/%Y")}</h2></div>
                <div class="week">{"".join(celdas)}</div>
            </section>'''
        )
        lunes += timedelta(days=7)

    return "\n".join(semanas)


def _crear_leyenda():
    elementos = []
    for formato, nombre in FORMATO_NOMBRES.items():
        clase = _clase_formato(formato)
        elementos.append(
            f'''<span class="legend-item {clase}">
                <i class="dot" aria-hidden="true"></i>{_escapar(nombre)}
            </span>'''
        )
    return "\n".join(elementos)


def _crear_lista_no_ubicadas(piezas_no_ubicadas):
    if not piezas_no_ubicadas:
        return '<li class="empty-list">Todas las piezas encontraron espacio.</li>'

    return "".join(
        f'<li><strong>{_escapar(pieza["id"])}</strong>'
        f'<span>{_escapar(pieza["razon"])}</span></li>'
        for pieza in piezas_no_ubicadas
    )


def _crear_lista_conflictos(conflictos):
    if not conflictos:
        return '<li class="empty-list">No se detectaron conflictos en las piezas programadas.</li>'
    return "".join(f"<li>{_escapar(conflicto)}</li>" for conflicto in conflictos)


def generar_html(inicio, fin, agenda, no, conflictos, asset_base="../web"):
    """Genera la página final y enlaza archivos estáticos externos."""
    total = len(agenda)
    pendientes = sum(1 for item in agenda if item.get("estado") == "pendiente_aprobacion")
    previas = sum(1 for item in agenda if item.get("estado") == "agendada")

    reemplazos = {
        "ASSET_BASE": _escapar(asset_base.rstrip("/")),
        "START_DATE": inicio.strftime("%d/%m/%Y"),
        "END_DATE": fin.strftime("%d/%m/%Y"),
        "TOTAL": str(total),
        "PENDING": str(pendientes),
        "PREVIOUS": str(previas),
        "NOT_PLACED": str(len(no)),
        "LEGEND": _crear_leyenda(),
        "WEEKS": _crear_semanas(inicio, fin, agenda),
        "NOT_PLACED_LIST": _crear_lista_no_ubicadas(no),
        "CONFLICTS_LIST": _crear_lista_conflictos(conflictos),
    }

    plantilla = RUTA_PLANTILLA.read_text(encoding="utf-8")
    for clave, valor in reemplazos.items():
        plantilla = plantilla.replace(f"@@{clave}@@", valor)

    return plantilla
