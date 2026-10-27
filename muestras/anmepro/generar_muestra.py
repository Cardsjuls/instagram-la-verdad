from pathlib import Path
import subprocess
import sys
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
TITLE = 'ANMEPRO respalda el proyecto de Ley Mirabal y destaca su aporte a la protecci\u00f3n laboral y la autonom\u00eda econ\u00f3mica de las mujeres'
photo = Image.open(HERE / 'foto-original.jpeg').convert('RGB')
photo = photo.crop((140, 0, 1206, 1066)).resize((1080, 1080), Image.Resampling.LANCZOS)
canvas = Image.new('RGB', (1080, 1350), (18, 65, 126))
canvas.paste(photo, (0, 0))
canvas.save(HERE / 'base-encuadrada.png')
subprocess.run([
    sys.executable, str(ROOT / 'degradado_hola.py'),
    str(HERE / 'base-encuadrada.png'), str(HERE / 'titular-completo.png'),
    '--text', TITLE, '--out-size', '1080x1350',
    '--fade-start', '0.46', '--solid-start', '0.63',
    '--top-color', '14,30,48', '--blue', '16,47,84', '--bottom-color', '18,65,126',
    '--text-top', '0.54', '--text-bottom', '0.98', '--text-start-font', '0.12',
    '--text-x-scale', '0.65', '--text-max-width', '0.94',
    '--text-line-spacing', '0.88', '--text-stroke', '4', '--text-tracking=-0.015',
], check=True)
(HERE / 'fuente.txt').write_text(
    'Articulo: https://laverdadrd.com.do/anmepro-respalda-el-proyecto-de-ley-mirabal-y-destaca-su-aporte-a-la-proteccion-laboral-y-la-autonomia-economica-de-las-mujeres/\n'
    'Titular completo: ' + TITLE + '\n'
    'Mismos parametros de estilo que muestras/putin/02-encuadre-ajustado.png.\n', encoding='utf-8')
