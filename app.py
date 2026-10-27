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

# Ruta absoluta del script (no depende del cwd)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPT_PATH = os.path.join(SCRIPT_DIR, "degradado_hola.py")

# ✅ Defaults para que SIEMPRE salga igual (misma “altura” y “tamaño”)
OUT_SIZE = os.getenv("OUT_SIZE", "1080x1350")

# Estos son los que tú vienes usando y te gustaron:
TEXT_LINE_SPACING = os.getenv("TEXT_LINE_SPACING", "0.88")
TEXT_START_FONT = os.getenv("TEXT_START_FONT", "0.09")
TEXT_X_SCALE = os.getenv("TEXT_X_SCALE", "0.65")
TEXT_MAX_WIDTH = os.getenv("TEXT_MAX_WIDTH", "0.94")

# Para que el resultado sea consistente:
TEXT_MIN_FONT = os.getenv("TEXT_MIN_FONT", "28")
TEXT_STROKE = os.getenv("TEXT_STROKE", "3")
TEXT_TRACKING = os.getenv("TEXT_TRACKING", "-0.015")
TEXT_TOP = os.getenv("TEXT_TOP", "0.44")
TEXT_BOTTOM = os.getenv("TEXT_BOTTOM", "0.98")


def safe_delete(path: str) -> None:
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except Exception:
        pass


@app.get("/")
def root():
    return {"ok": True, "docs": "/docs", "post": "/render"}


@app.post("/render")
async def render_image(
    background_tasks: BackgroundTasks,
    image: UploadFile = File(...),
    text: str = Form(...)
):
    uid = str(uuid.uuid4())

    # Mantener extensión real para que PIL detecte bien
    ext = os.path.splitext(image.filename or "")[1].lower()
    if ext not in [".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"]:
        ext = ".png"

    input_path = os.path.join(BASE_DIR, f"{uid}_input{ext}")
    output_path = os.path.join(BASE_DIR, f"{uid}_output.png")

    try:
        # Guardar archivo recibido
        with open(input_path, "wb") as f:
            f.write(await image.read())

        # ✅ OJO: aquí SOLO flags que EXISTEN en degradado_hola.py
        cmd = [
            sys.executable,
            SCRIPT_PATH,
            input_path,
            output_path,

            "--out-size", OUT_SIZE,
            "--text", text,

            "--text-line-spacing", TEXT_LINE_SPACING,
            "--text-start-font", TEXT_START_FONT,
            "--text-x-scale", TEXT_X_SCALE,
            "--text-max-width", TEXT_MAX_WIDTH,
            "--text-top", TEXT_TOP,
            "--text-bottom", TEXT_BOTTOM,

            "--text-min-font", TEXT_MIN_FONT,
            "--text-stroke", TEXT_STROKE,
            "--text-tracking", TEXT_TRACKING,
        ]

        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            raise HTTPException(
                status_code=500,
                detail=f"Render failed (exit {r.returncode}). STDERR: {r.stderr[-1500:]}"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Borrar temporales al terminar de enviar la respuesta
    background_tasks.add_task(safe_delete, input_path)
    background_tasks.add_task(safe_delete, output_path)

    return FileResponse(
        output_path,
        media_type="image/png",
        filename="render.png",
        background=background_tasks
    )
