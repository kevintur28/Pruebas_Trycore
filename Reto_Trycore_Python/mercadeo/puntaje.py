from statistics import mean
def entrenar(rows):
    vals=[r["tasa_normalizada"] for r in rows if r.get("tasa_normalizada") is not None and r.get("canal")=="linkedin"]
    base=mean(vals) if vals else 0.03
    grupos={}
    for campo in ("formato","tema","hora"):
        grupos[campo]={}
        for r in rows:
            if r.get("tasa_normalizada") is None or r.get("canal")!="linkedin": continue
            k=r.get(campo,"")
            grupos[campo].setdefault(k,[]).append(r["tasa_normalizada"])
    return {"media_global":base,"grupos":grupos,"n":len(vals)}

def calificar(modelo, formato, hora, tema):
    base=modelo["media_global"]
    factores={}
    # Suavizado hacia la media global para evitar que grupos pequeños dominen.
    for campo,valor in (("formato",formato),("hora",hora),("tema",tema)):
        datos=modelo["grupos"][campo].get(valor,[])
        n=len(datos)
        estimada=(sum(datos)+base*5)/(n+5) if n else base
        factores[campo]={"muestras":n,"tasa_estimada":round(estimada,5)}
        if n: base=0.5*base+0.5*estimada
    score=max(0,min(100,round(base*1000)))
    return {"puntaje":score,"tasa_estimada":round(base,5),"confianza":"media" if modelo["n"]>=20 else "baja","factores":factores}
