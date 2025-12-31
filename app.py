from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
import subprocess
import uuid
import os
import sys
import tempfile

app = FastAPI()

# Carpeta temporal válida en Windows/Linux/Docker
BASE_DIR = tempfile.gettempdir()

# Ruta absoluta del script, para que no dependa del "cwd"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPT_PATH = os.path.join(SCRIPT_DIR, "degradado_hola.py")

# === CONFIGURACIÓN DE TEXTO (constantes del render) ===
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf"
TEXT_TOP = 560          # desde dónde empieza el bloque de texto (Y)
TEXT_BOTTOM = 1330      # hasta dónde llega (Y)
LINE_SPACING = 6         # interlineado en px
MAX_FONT = 118           # tamaño máximo de fuente
MIN_FONT = 28
PADDING_X = 70
PADDING_Y = 40
STROKE_W = 6


def safe_delete(path: str) -> None:
    """Elimina archivos temporales de forma segura."""
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except Exception:
        pass


@app.get("/")
def root():
    """Ruta principal de prueba."""
    return {"ok": True, "docs": "/docs", "post": "/render"}


@app.post("/render")
async def render_image(
    background_tasks: BackgroundTasks,
    image: UploadFile = File(...),
    text: str = Form(...)
):
    """Procesa la imagen y devuelve el resultado generado por degradado_hola.py"""
    uid = str(uuid.uuid4())

    # Mantén la extensión real (por ejemplo .webp) para que PIL la detecte bien
    ext = os.path.splitext(image.filename or "")[1].lower()
    if ext not in [".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"]:
        ext = ".png"

    input_path = os.path.join(BASE_DIR, f"{uid}_input{ext}")
    output_path = os.path.join(BASE_DIR, f"{uid}_output.png")

    try:
        # Guardar archivo recibido
        with open(input_path, "wb") as f:
            f.write(await image.read())

        # Comando para ejecutar el script de renderizado
        cmd = [
            sys.executable,
            SCRIPT_PATH,
            input_path,
            output_path,
            "--out-size", "1638x2048",
            "--text", text,

            # === Parámetros fijos de diseño ===
            "--font-path", FONT_PATH,
            "--text-line-spacing", str(LINE_SPACING),
            "--text-top", str(TEXT_TOP),
            "--text-bottom", str(TEXT_BOTTOM),
            "--text-start-font", "0.135",
            "--text-x-scale", "0.78",
            "--text-max-width", "0.86",
            "--max-font", str(MAX_FONT),
            "--min-font", str(MIN_FONT),
            "--stroke-width", str(STROKE_W)
        ]

        subprocess.run(cmd, check=True)

    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Render failed (exit code {e.returncode}).")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Eliminar archivos temporales después de enviar la respuesta
    background_tasks.add_task(safe_delete, input_path)
    background_tasks.add_task(safe_delete, output_path)

    return FileResponse(
        output_path,
        media_type="image/png",
        filename="render.png",
        background=background_tasks
    )
