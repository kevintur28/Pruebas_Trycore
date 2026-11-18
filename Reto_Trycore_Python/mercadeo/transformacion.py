import re
from .validacion import slug, validar_pieza

def frases(texto):
    return [x.strip() for x in re.split(r"(?<=[.!?])\s+",texto) if len(x.split())>=5]

def extraer_listas(texto):
    items=[]
    for line in texto.splitlines():
        m=re.match(r"^\s*(?:[-•*]|\d+[.)])\s+(.+)",line)
        if m and len(m.group(1).split())>=3: items.append(m.group(1).strip())
    return items

def enlace_utm(doc, fmt, numero, config, aaaamm):
    canal=next((x["canal"] for x in config["matriz_formatos"] if x["id"]==fmt),"linkedin")
    source=config["utm"]["utm_source"].get(canal,canal)
    medium=config["utm"]["utm_medium"].get(canal,"referido")
    campaign=config["utm"]["utm_campaign"].format(slug_pieza_madre=slug(doc.titulo),aaaamm=aaaamm)
    content=f"{fmt.replace('_','-')}-{numero}"
    from urllib.parse import urlencode, urlsplit, urlunsplit, parse_qsl
    u=urlsplit(doc.url); q=dict(parse_qsl(u.query))
    q.update({"utm_source":source,"utm_medium":medium,"utm_campaign":campaign,"utm_content":content})
    return urlunsplit((u.scheme,u.netloc,u.path,urlencode(q),u.fragment))

def transformar(doc, config, tema="general", aaaamm="202611"):
    texto=doc.texto
    fs=frases(texto)
    listas=extraer_listas(texto)
    piezas=[]
    # Post: seleccionar bloques suficientes para alcanzar el mínimo configurado.
    ficha=next(x for x in config["matriz_formatos"] if x["id"]=="post_linkedin")
    min_chars=ficha["longitud"]["min_caracteres"]
    chunks=[]; current=[]
    for sentence in fs:
        current.append(sentence)
        if len(" ".join(current))>=min_chars-180:
            chunks.append(current); current=[]
    if current and len(" ".join(current))>=min_chars-180: chunks.append(current)
    for i,chunk in enumerate(chunks[:2]):
        url=enlace_utm(doc,"post_linkedin",i+1,config,aaaamm)
        hook=f"¿Qué deberías revisar sobre {tema.replace('_',' ')}?"
        body=f"{hook}\n\n"+" ".join(chunk)+"\n\n¿Qué aspecto revisarías primero?\n"+url
        piezas.append({"id":f"post_linkedin-{i+1}","formato":"post_linkedin","tema":tema,
          "partes":{"gancho":hook,"desarrollo":" ".join(chunk),"cta":"¿Qué aspecto revisarías primero?","enlace":url},"texto":body})
    # Carrusel: el HTML original contiene listas; cada elemento se conserva como una lámina.
    fcar=next(x for x in config["matriz_formatos"] if x["id"]=="carrusel_linkedin")
    if len(listas)>=5:
        seleccion=listas[:8]
        laminas=[{"numero":i+1,"texto":s} for i,s in enumerate(seleccion)]
        url=enlace_utm(doc,"carrusel_linkedin",1,config,aaaamm)
        piezas.append({"id":"carrusel_linkedin-1","formato":"carrusel_linkedin","tema":tema,
          "partes":{"portada":"Ideas clave para entender "+doc.titulo,"laminas":laminas,"cierre":"Consulta la guía completa: "+url},
          "texto":"\n".join(["Portada: Ideas clave para entender "+doc.titulo]+[f"Lámina {x['numero']}: {x['texto']}" for x in laminas]+["Cierre: "+url])})
    # Newsletter: toma texto original hasta alcanzar la longitud mínima; no agrega hechos.
    if len(fs)>=6:
        seleccion=[]; count=0
        for sentence in fs:
            seleccion.append(sentence); count+=len(sentence.split())
            if count>=config["matriz_formatos"][2]["longitud"]["min_palabras"]-10: break
        secciones=[{"subtitulo":f"Idea {i+1}","texto":" ".join(seleccion[i::3])} for i in range(3)]
        url=enlace_utm(doc,"newsletter",1,config,aaaamm)
        intro="Esta edición reúne ideas de la pieza original para entender mejor el tema y reconocer dónde conviene empezar."
        piezas.append({"id":"newsletter-1","formato":"newsletter","tema":tema,
          "partes":{"asunto":doc.titulo[:60],"introduccion":intro,"secciones":secciones,"cta":"Lee la guía completa: "+url},
          "texto":doc.titulo[:60]+"\n\n"+intro+"\n\n"+"\n\n".join(s["subtitulo"]+"\n"+s["texto"] for s in secciones)+"\n\nLee la guía completa: "+url})
    # Guion: usar fragmentos consecutivos hasta alcanzar el mínimo de palabras.
    if len(fs)>=3:
        url=enlace_utm(doc,"guion_video_corto",1,config,aaaamm)
        seleccion=[]; count=0
        for sentence in fs:
            seleccion.append(sentence); count+=len(sentence.split())
            if count>=config["matriz_formatos"][3]["palabras"]["min"]-10: break
        grupos=[seleccion[i::3] for i in range(3)]
        puntos=[" ".join(g) for g in grupos if g]
        hook="¿Qué ideas de esta guía vale la pena revisar?"
        cierre="Consulta la guía completa y revisa cómo aplicar estas ideas: "+url
        guion={"gancho":hook,"puntos":puntos,"cierre":cierre}
        cuerpo=hook+" "+" ".join(puntos)+" "+cierre
        piezas.append({"id":"guion_video_corto-1","formato":"guion_video_corto","tema":tema,"partes":guion,"texto":cuerpo})
    # Validación por reglas globales y ficha específica.
    for p in piezas:
        f=next(x for x in config["matriz_formatos"] if x["id"]==p["formato"])
        problemas=validar_pieza(p["texto"],config,texto)
        palabras=len(p["texto"].split()); chars=len(p["texto"])
        if p["formato"]=="post_linkedin":
            if not f["longitud"]["min_caracteres"]<=chars<=f["longitud"]["max_caracteres"]: problemas.append("Longitud del post fuera del rango configurado.")
        elif p["formato"]=="carrusel_linkedin":
            n=len(p["partes"]["laminas"])
            if not f["laminas"]["min"]<=n<=f["laminas"]["max"]: problemas.append("Número de láminas fuera del rango.")
            if any(len(x["texto"].split())>f["max_palabras_por_lamina"] for x in p["partes"]["laminas"]): problemas.append("Una lámina supera el máximo de palabras.")
        elif p["formato"]=="newsletter":
            if not f["longitud"]["min_palabras"]<=palabras<=f["longitud"]["max_palabras"]: problemas.append("Newsletter fuera del rango de palabras.")
            if len(p["partes"]["asunto"])>f["asunto_max_caracteres"]: problemas.append("Asunto demasiado largo.")
        elif p["formato"]=="guion_video_corto":
            if not f["palabras"]["min"]<=palabras<=f["palabras"]["max"]: problemas.append("Guion fuera del rango de palabras.")
        p["problemas"]=problemas
        p["estado"]="requiere_revision" if problemas else "pendiente_aprobacion"
    return piezas
