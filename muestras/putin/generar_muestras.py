from pathlib import Path
import subprocess
import sys
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
TITLE = 'Putin acepta reanudar las conversaciones de paz con Ucrania'
SCRIPT = ROOT / 'degradado_hola.py'

def render(source, output, args):
    subprocess.run([sys.executable, str(SCRIPT), str(source), str(HERE / output), '--text', TITLE, *args], check=True)

# Same parameters used by app.py, without changing the project defaults.
render(HERE / 'foto-original.png', '01-estilo-actual.png', [
    '--out-size', '1638x2048', '--text-line-spacing', '0.74',
    '--text-start-font', '0.075', '--text-x-scale', '0.78',
    '--text-max-width', '0.86', '--text-min-font', '28',
    '--text-stroke', '6', '--text-tracking=-0.015',
])

# Remove the white side margins and retain both people in the upper photo.
photo = Image.open(HERE / 'foto-original.png').convert('RGB')
photo = photo.crop((301, 0, 876, 575)).resize((1080, 1080), Image.Resampling.LANCZOS)
canvas = Image.new('RGB', (1080, 1350), (18, 65, 126))
canvas.paste(photo, (0, 0))
canvas.save(HERE / 'base-encuadrada.png')
render(HERE / 'base-encuadrada.png', '02-encuadre-ajustado.png', [
    '--out-size', '1080x1350', '--fade-start', '0.46', '--solid-start', '0.63',
    '--top-color', '14,30,48', '--blue', '16,47,84', '--bottom-color', '18,65,126',
    '--text-top', '0.54', '--text-bottom', '0.98', '--text-start-font', '0.12',
    '--text-x-scale', '0.65', '--text-max-width', '0.94',
    '--text-line-spacing', '0.88', '--text-stroke', '4', '--text-tracking=-0.015',
])
(HERE / 'fuente.txt').write_text(
    'Articulo: https://laverdadrd.com.do/putin-acepta-reanudar-las-conversaciones-de-paz-con-ucrania/\n'
    'Foto: https://laverdadrd.com.do/wp-content/uploads/2026/10/putin.png\n'
    'Titular: ' + TITLE + '\n'
    '01: parametros predeterminados de app.py en Windows.\n'
    '02: encuadre y parametros ajustados mediante el mismo renderizador.\n', encoding='utf-8')
