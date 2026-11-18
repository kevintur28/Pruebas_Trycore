import re, unicodedata

def slug(texto):
    t=unicodedata.normalize("NFKD",str(texto)).encode("ascii","ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+","-",t).strip("-")

def buscar_terminos(texto, config):
    hallados=[]
    for item in config.get("terminos_prohibidos",[]):
        term=item["termino"]
        if re.search(re.escape(term),texto,re.I):
            hallados.append({"termino":term,"motivo":item.get("motivo","")})
    return hallados

def buscar_confidenciales(texto, config):
    return [n for n in config.get("nombres_confidenciales",[]) if re.search(re.escape(n),texto,re.I)]

def validar_pieza(texto, config, madre):
    errores=[]
    for x in buscar_terminos(texto,config): errores.append(f"Término prohibido «{x['termino']}»: {x['motivo']}")
    for n in buscar_confidenciales(texto,config): errores.append(f"Nombre confidencial: {n}")
    # Las cifras no presentes en la madre no se aceptan. Se excluyen números de UTM/URLs.
    texto_sin_indices=re.sub(r"(?i)lámina\s+\d+","",texto)
    nums=set(re.findall(r"(?<![A-Za-z])\d+(?:[.,]\d+)?%?", re.sub(r"https?://\S+","",texto_sin_indices)))
    nums_madre=set(re.findall(r"(?<![A-Za-z])\d+(?:[.,]\d+)?%?",madre))
    inventadas=sorted(nums-nums_madre)
    if inventadas: errores.append("Cifras no encontradas en la pieza madre: "+", ".join(inventadas))
    for p in config.get("productos_vigentes",[]):
        pass
    return errores
