"""Convierte a WebP y coloca en la formación las imágenes de bocetos/ y de las capturas.

Uso: python -I herramientas/coloca-imagenes.py <carpeta de capturas>
"""
import shutil
import sys
from pathlib import Path
from PIL import Image

R = Path(__file__).resolve().parent.parent
CAP = Path(sys.argv[1])
O = R / 'bocetos' / 'ia-originales'


def webp(origen, destino, ancho=None, calidad=86):
    im = Image.open(origen)
    im = im.convert('RGBA' if im.mode in ('RGBA', 'LA', 'P') else 'RGB')
    if ancho and im.width > ancho:
        im = im.resize((ancho, round(im.height * ancho / im.width)), Image.LANCZOS)
    destino.parent.mkdir(parents=True, exist_ok=True)
    im.save(destino, 'WEBP', quality=calidad, method=6)
    print(destino.relative_to(R), im.size)


I = R / 'assets' / 'img'
webp(R / 'bocetos' / 'maqueta-juego-v1.png', I / 'maqueta.webp', 1200)
webp(R / 'bocetos' / 'prototipo' / 'fondo-original.png', I / 'plaza.webp', 1280)
webp(O / 'ejemplo-petardo.png', I / 'ejemplo-petardo.webp', 640)
for origen, nombre in [('shots/2-joc.png', 'proto-1'), ('shots/v3-2-joc.png', 'proto-2'), ('shots/v5-4-tu.png', 'proto-3'), ('shots/v7-4-joc.png', 'proto-4')]:
    webp(CAP / origen, I / f'{nombre}.webp', 1280)
for nombre in ['editor-general', 'editor-archivo', 'editor-disfraces', 'editor-sonidos', 'editor-variables', 'editor-paso10']:
    webp(CAP / 'editor' / f'{nombre}.png', I / 'scratch' / f'{nombre}.webp', 1600)
S = I / 'sprites'
S.mkdir(parents=True, exist_ok=True)
for f in (R / 'herramientas' / 'recursos').glob('*.png'):
    shutil.copy(f, S / f.name)
print('sprites:', len(list(S.glob('*.png'))))
