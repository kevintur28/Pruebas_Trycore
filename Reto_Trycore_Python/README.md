# Sistema táctico de contenidos — Reto Trycore

Proyecto en Python que recibe una pieza madre y genera diagnóstico, contenidos derivados, calendario HTML y puntajes históricos. Está diseñado para usar las reglas de `insumos/configuracion/config.json`, el historial y la ventana como entradas, sin publicar automáticamente.

## Estructura del proyecto

```text
Reto_Trycore_Python/
├── main.py                  # Punto único de ejecución
├── mercadeo/                # Lógica del proceso, separada por responsabilidad
│   ├── ingesta.py           # Descarga y lectura de la pieza madre
│   ├── diagnostico.py       # Indicadores y alertas
│   ├── transformacion.py    # Adaptación a formatos
│   ├── validacion.py        # Reglas de contenido
│   ├── historial.py         # Lectura y normalización del histórico
│   ├── puntaje.py           # Estimación del puntaje
│   ├── calendario.py        # Asignación de fechas y horas
│   ├── vista.py             # Datos dinámicos para la página HTML
│   └── pipeline.py          # Orquestación del flujo completo
├── web/                     # Presentación web, separada del backend
│   ├── plantillas/          # Estructura HTML sin estilos incrustados
│   ├── css/                 # Apariencia y diseño del calendario
│   └── js/                  # Interacciones del calendario
├── insumos/                 # Archivos de entrada entregados para el reto
├── tests/                   # Pruebas automáticas
├── docs/                    # Análisis y sustentación
└── salidas/                 # Resultados creados al ejecutar (no se versionan)
```

### Separación de la interfaz

- `web/plantillas/calendario.html`: estructura y contenido semántico de la página.
- `web/css/calendario.css`: colores, tipografía, distribución, adaptación móvil e impresión.
- `web/js/calendario.js`: filtro por formato e impresión del calendario. No utiliza librerías externas.
- `mercadeo/vista.py`: inserta los datos de Python en la plantilla; no contiene CSS ni JavaScript.

La hoja de estilos y el JavaScript se enlazan como archivos externos desde el HTML generado. El programa calcula la ruta relativa de esos recursos para que también funcione al personalizar la carpeta de salida con `--salida`.

## Requisitos
- Python 3.10 o superior.
- No requiere librerías externas: utiliza la biblioteca estándar.

## Instalación
```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Linux/macOS:
source .venv/bin/activate
```

## Ejecución
Desde la raíz del proyecto:
```bash
python main.py
```
Para probar otra pieza madre:
```bash
python main.py --url "https://ejemplo.com/articulo"
```
Si la URL falla, se usa el HTML de respaldo incluido y el diagnóstico lo advierte. Para exigir descarga directa:
```bash
python main.py --sin-respaldo
```

Los resultados aparecen en `salidas/`: `diagnostico.json`, `piezas_derivadas.json`, `piezas_derivadas.md`, `calendario.json`, `calendario.html` y `puntaje.json`. Abre `salidas/calendario.html` en el navegador. El HTML carga los archivos de `web/css/` y `web/js/`; por eso conserva la carpeta `web` junto al resto del proyecto.

## Pruebas
```bash
python -m unittest discover -s tests -v
```

## Decisiones y límites
- La extracción HTML usa `HTMLParser`; no necesita servicios pagos ni credenciales.
- Las piezas derivadas se construyen con fragmentos del texto fuente. La validación bloquea términos prohibidos, nombres confidenciales y cifras no halladas en la madre. El resultado siempre requiere aprobación humana.
- El calendario respeta días hábiles, festivos, franjas, capacidades y separación temática definidos en JSON.
- El puntaje es una estimación heurística: combina la media histórica con medias por formato, hora y tema, suavizadas con cinco observaciones equivalentes a la media global. No es una predicción causal ni garantiza resultados.
- El historial puede tener duplicados, fechas y booleanos inconsistentes; el cargador normaliza esos campos y reporta duplicados.
- El reto exige explicar en el video las contradicciones de las notas, riesgos y límites del modelo. El sistema no publica en LinkedIn.

## Flujo
1. Ingesta de la pieza madre.
2. Diagnóstico y alertas.
3. Transformación y validación por formato.
4. Puntaje basado en el historial.
5. Programación y generación de la vista web.
6. Aprobación humana antes de cualquier publicación.

## Documentación para la sustentación
- `docs/analisis_requisitos.md`: prioridades, contradicciones, preguntas y riesgos.
- `docs/guion_video.md`: estructura sugerida del video y diagrama del flujo.
