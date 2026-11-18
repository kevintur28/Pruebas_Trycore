import re
from .validacion import buscar_terminos, buscar_confidenciales

def diagnosticar(doc, config):
    texto=doc.texto
    palabras=re.findall(r"\b[\wÁÉÍÓÚáéíóúÑñÜü]+\b",texto)
    frases=[x for x in re.split(r"(?<=[.!?])\s+",texto) if x.strip()]
    prom=sum(len(x.split()) for x in frases)/max(len(frases),1)
    listas=re.findall(r"(?:^|\n)(?:[-•*]\s*.+\n?){3,}",texto)
    cifras=re.findall(r"\b\d+(?:[.,]\d+)?%?\b",texto)
    secciones=len(re.findall(r"(?im)^.{4,80}$",texto))
    indicadores=[
      {"nombre":"Palabras detectadas","valor":len(palabras),"unidad":"palabras","estado":"ok" if len(palabras)>=500 else "atencion"},
      {"nombre":"Promedio de palabras por frase","valor":round(prom,1),"unidad":"palabras","estado":"ok" if prom<=25 else "atencion"},
      {"nombre":"Listas detectadas","valor":len(listas),"unidad":"listas","estado":"ok" if listas else "atencion"},
      {"nombre":"Cifras detectadas","valor":len(cifras),"unidad":"cifras","estado":"revision"},
      {"nombre":"Secciones/líneas de contenido","valor":secciones,"unidad":"bloques","estado":"ok" if secciones>=5 else "atencion"},
    ]
    alertas=[]
    if doc.fuente=="respaldo": alertas.append({"severidad":"atencion","mensaje":"Se utilizó el HTML de respaldo; verifica que esté actualizado."})
    for x in buscar_terminos(texto,config): alertas.append({"severidad":"error","mensaje":f"Término prohibido en la pieza madre: {x['termino']}"})
    for n in buscar_confidenciales(texto,config): alertas.append({"severidad":"error","mensaje":f"Nombre confidencial detectado: {n}"})
    for c in cifras:
        alertas.append({"severidad":"revision","mensaje":f"Cifra detectada ({c}); comprueba que tenga fuente antes de reutilizarla."})
    if not any(p.lower() in texto.lower() for p in config["productos_vigentes"]):
        alertas.append({"severidad":"info","mensaje":"La pieza madre no menciona productos vigentes; no se añadirá uno por inferencia."})
    return {"pieza_madre":{"url":doc.url,"titulo":doc.titulo,"fuente":doc.fuente},
            "indicadores":indicadores,"alertas":alertas}
