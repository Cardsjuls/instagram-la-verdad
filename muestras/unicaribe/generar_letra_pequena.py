from pathlib import Path
import subprocess,sys
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
TITLE='UNICARIBE inaugura Auditorio Dr. Joaqu\u00edn Balaguer: Reconoce su legado y contribuci\u00f3n al nacimiento de la universidad'
photo=Image.open(HERE/'foto-original.jpg').convert('RGB')
photo=photo.resize((1080,round(photo.height*1080/photo.width)),Image.Resampling.LANCZOS)
canvas=Image.new('RGB',(1080,1350),(14,30,48))
canvas.paste(photo,(0,0))
canvas.save(HERE/'base-encuadrada.png')
subprocess.run([sys.executable,str(ROOT/'degradado_hola.py'),str(HERE/'base-encuadrada.png'),str(HERE/'letra-mas-pequena.png'),
'--text',TITLE,'--out-size','1080x1350','--fade-start','0.34','--solid-start','0.437',
'--top-color','14,30,48','--blue','16,47,84','--bottom-color','18,65,126',
'--text-top','0.44','--text-bottom','0.98','--text-start-font','0.09','--text-x-scale','0.65',
'--text-max-width','0.94','--text-line-spacing','0.88','--text-stroke','3','--text-tracking=-0.015'],check=True)
(HERE/'fuente.txt').write_text('Articulo: https://laverdadrd.com.do/unicaribe-inaugura-auditorio-dr-joaquin-balaguer-reconoce-su-legado-y-contribucion-al-nacimiento-de-la-universidad/\nTitular original: '+TITLE+'\nFoto completa de grupo; degradado adaptado a la altura de la fotografia.\n',encoding='utf-8')
