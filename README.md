# Instagram La Verdad

Generador de imagenes para Instagram a partir de una fotografia y un titular, basado en el proyecto image-overlay.

## Funciones

- API FastAPI: `POST /render` recibe `image` y `text`, devuelve un PNG.
- Salida predeterminada de 1080 x 1350 pixeles (4:5).
- Degradado azul, texto blanco centrado y borde negro fino.
- Tamano fijo de letra: 9 % de la altura, con compresion horizontal de 0.65.
- Si el titular no cabe, se corta por palabras completas y se agregan tres puntos (...).
- Los titulares que caben se conservan completos.

El corte es por espacio disponible, no un resumen editorial: puede cortar nombres o frases. Conviene revisar la imagen antes de publicarla.

## Ejecutar localmente

Requiere Python 3.11 o posterior.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app:app --host 127.0.0.1 --port 8000
```

Abrir http://127.0.0.1:8000/docs y probar `POST /render` subiendo una foto e indicando el titular.

Tambien se puede ejecutar el renderizador directamente:

```powershell
python degradado_hola.py foto.jpg resultado.png --text "Titular de la noticia"
```

Consultar `python degradado_hola.py --help` para ajustar el encuadre, los colores y la posicion del texto.

## Docker

```sh
docker build -t instagram-la-verdad .
docker run --rm -p 8000:8000 instagram-la-verdad
```

La fuente utilizada depende del sistema: Docker instala DejaVu; Windows utiliza Arial cuando esta disponible. La tipografia puede variar entre entornos.

## Configuracion de la API

Variables de entorno opcionales:

| Variable | Predeterminado |
| --- | --- |
| OUT_SIZE | 1080x1350 |
| TEXT_START_FONT | 0.09 |
| TEXT_X_SCALE | 0.65 |
| TEXT_MAX_WIDTH | 0.94 |
| TEXT_LINE_SPACING | 0.88 |
| TEXT_STROKE | 3 |
| TEXT_TRACKING | -0.015 |
| TEXT_TOP | 0.44 |
| TEXT_BOTTOM | 0.98 |
| TEXT_MIN_FONT | 28 |

TEXT_MIN_FONT fija el minimo del tamano inicial; el titular se recorta si no cabe, sin reducir progresivamente la letra.

## Muestras

La carpeta `muestras/` incluye fotografias de los articulos, resultados y scripts reproducibles. Se conservan versiones anteriores para comparar estilos.

La version aprobada de UNICARIBE se reproduce con:

```powershell
python muestras/unicaribe/generar_letra_pequena.py
```

Ese ejemplo conserva la foto completa del grupo y ajusta la altura del degradado. Otros scripts muestran encuadres especificos de cada noticia; la API utiliza recorte centrado por defecto.

## Pruebas

```powershell
python -m unittest -v test_title_overflow
```

## Estado de la automatizacion

Este proyecto genera imagenes. La deteccion de nuevas noticias de WordPress y la publicacion automatica en Instagram todavia no estan implementadas. No requiere ni incluye credenciales de Instagram.

## Origen

Proyecto original: https://github.com/vielmaoliver/image-overlay
Las fuentes de los articulos y las fotografias utilizadas en los ejemplos se indican en `muestras/*/fuente.txt`.
