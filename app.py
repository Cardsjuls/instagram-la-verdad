from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
import subprocess
import uuid
import os

app = FastAPI()

BASE_DIR = "/tmp"

@app.post("/render")
async def render_image(
    image: UploadFile = File(...),
    text: str = Form(...)
):
    uid = str(uuid.uuid4())

    input_path = f"{BASE_DIR}/{uid}_input.png"
    output_path = f"{BASE_DIR}/{uid}_output.png"

    with open(input_path, "wb") as f:
        f.write(await image.read())

    cmd = [
        "python",
        "degradado_hola.py",
        input_path,
        output_path,
        "--out-size", "1638x2048",
        "--text", text,
        "--text-line-spacing", "0.74",
        "--text-start-font", "0.135",
        "--text-x-scale", "0.78",
        "--text-max-width", "0.86"
    ]

    subprocess.run(cmd, check=True)

    return FileResponse(output_path, media_type="image/png")
