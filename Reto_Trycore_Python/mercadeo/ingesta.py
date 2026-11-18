from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.request import Request, urlopen
from pathlib import Path

@dataclass
class Documento:
    url: str
    titulo: str
    texto: str
    fuente: str

class Extractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts=[]
        self.title=[]
        self.in_title=False
        self.skip=0
    def handle_starttag(self, tag, attrs):
        if tag in ("script","style","nav","footer","header"):
            self.skip += 1
        if tag=="title":
            self.in_title=True
        if not self.skip:
            if tag=="li": self.parts.append("\n• ")
            elif tag in ("p","h1","h2","h3","br"): self.parts.append("\n")
    def handle_endtag(self, tag):
        if tag=="title":
            self.in_title=False
        if tag in ("script","style","nav","footer","header") and self.skip:
            self.skip-=1
        if not self.skip and tag in ("p","h1","h2","h3","li"):
            self.parts.append("\n")
    def handle_data(self, data):
        if self.skip: return
        if self.in_title: self.title.append(data)
        self.parts.append(data)

def limpiar(texto):
    return " ".join((texto or "").replace("\xa0"," ").split())

def desde_html(html, url):
    x=Extractor()
    x.feed(html)
    bloques=[limpiar(v) for v in "".join(x.parts).splitlines()]
    texto="\n".join(v for v in bloques if v)
    titulo=limpiar(" ".join(x.title)) or (texto[:100] if texto else "Pieza sin título")
    return Documento(url,titulo,texto,"url")

def cargar_madre(url, respaldo=None, timeout=12):
    error=None
    try:
        req=Request(url,headers={"User-Agent":"Mozilla/5.0 (compatible; RetoTrycore/1.0)"})
        with urlopen(req,timeout=timeout) as r:
            html=r.read().decode("utf-8",errors="replace")
        doc=desde_html(html,url)
        if len(doc.texto)<200: raise ValueError("La URL devolvió poco contenido legible")
        return doc
    except Exception as exc:
        error=str(exc)
    if respaldo and Path(respaldo).exists():
        html=Path(respaldo).read_text(encoding="utf-8",errors="replace")
        doc=desde_html(html,url)
        doc.fuente="respaldo"
        return doc
    raise RuntimeError(f"No fue posible obtener la pieza madre: {error}")
