import csv, re
from datetime import datetime
from pathlib import Path

MESES={"ene":1,"feb":2,"mar":3,"abr":4,"may":5,"jun":6,"jul":7,"ago":8,"sep":9,"oct":10,"nov":11,"dic":12}
def fecha(s):
    s=(s or "").strip()
    for fmt in ("%Y-%m-%d","%d/%m/%Y","%d-%m-%Y"):
        try: return datetime.strptime(s,fmt).date()
        except ValueError: pass
    m=re.match(r"(\d{1,2})-([a-záéíóúñ]{3})-(\d{4})",s,re.I)
    if m and m.group(2).lower()[:3] in MESES:
        return datetime(int(m.group(3)),MESES[m.group(2).lower()[:3]],int(m.group(1))).date()
    raise ValueError(f"Fecha no reconocida: {s}")

def booleano(s):
    return str(s or "").strip().lower() in ("1","si","sí","true","verdadero","yes")

def numero(s):
    if s is None or str(s).strip()=="": return None
    return float(str(s).strip().replace(",", "."))

def cargar_historial(path):
    with open(path,encoding="utf-8-sig",newline="") as f: rows=list(csv.DictReader(f))
    unicos={}
    duplicados=0; invalidas=0
    for r in rows:
        try:
            r["fecha_normalizada"]=fecha(r["fecha"])
            r["tiene_cifra_normalizada"]=booleano(r.get("tiene_cifra"))
            r["tasa_normalizada"]=numero(r.get("tasa_interaccion"))
            r["impresiones_n"]=numero(r.get("impresiones"))
            r["reacciones_n"]=numero(r.get("reacciones"))
            r["comentarios_n"]=numero(r.get("comentarios"))
            r["clics_n"]=numero(r.get("clics"))
            # Si la tasa falta, se calcula cuando hay impresiones.
            if r["tasa_normalizada"] is None and r["impresiones_n"]:
                inter=sum(r[k] or 0 for k in ("reacciones_n","comentarios_n","clics_n"))
                r["tasa_normalizada"]=inter/r["impresiones_n"]
            key=r.get("id_publicacion") or (r["fecha"],r["hora"],r["formato"])
            if key in unicos: duplicados+=1
            else: unicos[key]=r
        except (ValueError,KeyError,TypeError): invalidas+=1
    return list(unicos.values()),{"filas_originales":len(rows),"filas_validas":len(unicos),"duplicados_omitidos":duplicados,"filas_invalidas":invalidas}

def tema_de(texto, config):
    low=texto.lower()
    hits=[p.lower().replace(" ","_") for p in config["productos_vigentes"] if p.lower() in low]
    return hits[0] if hits else "rpa" if "rpa" in low else "general"
