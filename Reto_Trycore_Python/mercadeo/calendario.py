from datetime import datetime, timedelta

def programar(piezas, ocupado, ventana, config, puntuar):
    cal=config["calendario"]; inicio=datetime.fromisoformat(ventana["inicio"]).date(); fin=datetime.fromisoformat(ventana["fin"]).date()
    festivos={x["fecha"] for x in cal["festivos"]}
    dias={"lunes":0,"martes":1,"miércoles":2,"jueves":3,"viernes":4}
    habiles=set(dias.values())
    slots=[]
    d=inicio
    while d<=fin:
        if d.weekday() in habiles and d.isoformat() not in festivos:
            for h in cal["franjas_de_publicacion"]: slots.append((d,h))
        d+=timedelta(days=1)
    agenda=[]
    for x in ocupado:
        try: agenda.append({"fecha":datetime.fromisoformat(x["fecha"]).date(),"hora":x["hora"],"tema":x["tema"],"formato":x["formato"],"titulo":x["titulo"],"estado":"agendada","ocupada":True})
        except Exception: pass
    asignadas=[]; no=[]
    max_dia=cal["capacidad_max_por_dia"]; max_sem=cal["capacidad_max_por_semana"]; separacion=cal["separacion_minima_mismo_tema_horas"]
    conteo_dia={}; conteo_sem={}; formatos_sem={}
    for a in agenda:
        k=a["fecha"]; sem=k.isocalendar()[:2]
        conteo_dia[k]=conteo_dia.get(k,0)+1; conteo_sem[sem]=conteo_sem.get(sem,0)+1
        formatos_sem[(sem,a["formato"])]=formatos_sem.get((sem,a["formato"]),0)+1
    for p in sorted(piezas,key=lambda x:(x["formato"],x["id"])):
        if p["estado"]!="pendiente_aprobacion":
            no.append({"id":p["id"],"titulo":p["partes"].get("gancho",p["formato"]),"razon":"Requiere revisión: "+("; ".join(p["problemas"]) or "validación pendiente")})
            continue
        ficha=next(x for x in config["matriz_formatos"] if x["id"]==p["formato"])
        elegido=None
        for fecha,hora in slots:
            sem=fecha.isocalendar()[:2]
            if conteo_dia.get(fecha,0)>=max_dia or conteo_sem.get(sem,0)>=max_sem: continue
            if formatos_sem.get((sem,p["formato"]),0)>=ficha.get("max_por_semana",99): continue
            dt=datetime.combine(fecha,datetime.strptime(hora,"%H:%M").time())
            conflicto=False
            for a in agenda+asignadas:
                if a["tema"]==p["tema"]:
                    adt=datetime.combine(a["fecha"],datetime.strptime(a["hora"],"%H:%M").time())
                    if abs((dt-adt).total_seconds())<separacion*3600: conflicto=True; break
            if conflicto: continue
            elegido=(fecha,hora); break
        if not elegido:
            no.append({"id":p["id"],"titulo":p["partes"].get("gancho",p["formato"]),"razon":"No existe una franja que cumpla capacidad, frecuencia y separación temática."})
            continue
        fecha,hora=elegido; sem=fecha.isocalendar()[:2]
        item={"id":p["id"],"fecha":fecha,"hora":hora,"formato":p["formato"],"tema":p["tema"],"titulo":p["partes"].get("gancho",p["partes"].get("portada",p["formato"])),"estado":"pendiente_aprobacion","puntaje":puntuar(p,hora)}
        asignadas.append(item); conteo_dia[fecha]=conteo_dia.get(fecha,0)+1; conteo_sem[sem]=conteo_sem.get(sem,0)+1; formatos_sem[(sem,p["formato"])]=formatos_sem.get((sem,p["formato"]),0)+1
    return asignadas,no
