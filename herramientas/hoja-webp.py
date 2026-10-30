"""Pasa a WebP una hoja de iconos original (para enseñarla en el módulo 2). Uso: python -I hoja-webp.py origen.png destino.webp"""
import sys
from PIL import Image
im = Image.open(sys.argv[1]).convert('RGBA')
im = im.resize((1600, round(im.height * 1600 / im.width)), Image.LANCZOS)
im.save(sys.argv[2], 'WEBP', quality=86, method=6)
print(sys.argv[2], im.size)
