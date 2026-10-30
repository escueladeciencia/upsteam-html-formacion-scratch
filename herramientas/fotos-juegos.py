"""Imágenes de juegos de ritmo y de la mascletà (módulo 1), sacadas de Wikimedia Commons.

Baja cada foto (o un fotograma de un vídeo), la recorta en 2:1 por la pantalla del juego y la guarda
en assets/img/juegos/ como WebP. Recorta también el vídeo de osu! (6,5 s, sin sonido) en
assets/video/osu.mp4 y apunta autor y licencia en assets/img/juegos/creditos.json.

    python herramientas/fotos-juegos.py

Necesita conexión a internet y ffmpeg. El vídeo de Taiko pesa unos 120 MB.
"""
import io
import json
import re
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
DESTINO = RAIZ / 'assets' / 'img' / 'juegos'
VIDEO = RAIZ / 'assets' / 'video' / 'osu.mp4'
UA = {'User-Agent': 'MascletFormacion/1.0 (formacion para docentes; raulibaper@gmail.com)'}
LADO = 1100  # ancho máximo de cada imagen, en píxeles

# clave: (archivo de Commons, recorte 2:1 (x0, x1, centro y) en fracciones de la imagen o None, segundo del fotograma si es vídeo)
IMAGENES = {
    'ddr': ('File:DDR A player.jpg', (0.05, 0.65, 0.62), None),
    'taiko': ('File:(Taiko) ARMAGEΔDON (Extreme 10* - Full Combo).webm', (0.18, 0.92, 0.38), 30),
    'guitar-hero': ('File:Guitar Hero 3 (1295821195).jpg', (0.42, 1, 0.55), None),
    'osu': ('File:Osu!standard gameplay.webm', (0, 1, 0.5), 1.4),
    'just-dance': ('File:IMGP3928 (just dance 2) (1280 1024 wm W) (5136647541).jpg', (0, 0.62, 0.27), None),
    'beat-saber': ('File:InclusiveGameLab Person-Playing-Virtual-Reality 4 CC-BY-SA.jpg', (0.15, 1, 0.6), None),
    'mascleta': ('File:Mascletà at Valencia, Spain, 2010 (DSC7155).jpg', None, None),
}


def api(titulos):
    q = {'action': 'query', 'titles': '|'.join(titulos), 'prop': 'imageinfo', 'iiprop': 'url|extmetadata',
         'iiurlwidth': 1600, 'format': 'json'}
    url = 'https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode(q)
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return {p['title']: p['imageinfo'][0] for p in json.load(r)['query']['pages'].values()}


def baja(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=600) as r:
        return r.read()


def fotograma(video, segundo, destino):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(segundo), '-i', str(video), '-frames:v', '1', str(destino)], check=True)
    return Image.open(destino)


def recorta(im, caja):
    if not caja:
        return im
    x0, x1, yc = caja
    W, H = im.size
    w = (x1 - x0) * W
    h = w / 2
    y0 = max(0, min(H - h, yc * H - h / 2))
    return im.crop((round(x0 * W), round(y0), round(x1 * W), round(y0 + h)))


def guarda(im, clave):
    im = im.convert('RGB')
    im.thumbnail((LADO, LADO), Image.LANCZOS)
    im.save(DESTINO / f'{clave}.webp', 'WEBP', quality=80, method=6)
    return im.size


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    DESTINO.mkdir(parents=True, exist_ok=True)
    VIDEO.parent.mkdir(parents=True, exist_ok=True)
    info = api([titulo for titulo, _, _ in IMAGENES.values()])
    limpia = lambda s: re.sub(r'<[^>]+>', '', s or '').strip()
    creditos = {}
    for clave, (titulo, caja, segundo) in IMAGENES.items():
        ii = info[titulo.replace('_', ' ')]
        m = ii['extmetadata']
        creditos[clave] = {'archivo': titulo[5:], 'autor': limpia(m['Artist']['value']),
                           'licencia': limpia(m['LicenseShortName']['value']), 'pagina': ii['descriptionurl']}
        if segundo is None:
            im = Image.open(io.BytesIO(baja(ii.get('thumburl') or ii['url'])))
        else:
            with tempfile.TemporaryDirectory() as tmp:
                original = Path(tmp) / 'video.webm'
                original.write_bytes(baja(ii['url']))
                if clave == 'osu':
                    # El clip acaba antes de la ruleta final (6,7 s): solo círculos y aros
                    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(original), '-t', '6.5', '-an',
                                    '-vf', 'scale=960:-2,fps=30', '-c:v', 'libx264', '-crf', '27', '-preset', 'slow',
                                    '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(VIDEO)], check=True)
                    print(f'osu: vídeo {VIDEO.stat().st_size // 1024} KB')
                im = fotograma(original, segundo, Path(tmp) / 'fotograma.png')
                im.load()
        tam = guarda(recorta(im, caja), clave)
        print(f'{clave}: {tam} · {creditos[clave]["autor"]} · {creditos[clave]["licencia"]}')
    (DESTINO / 'creditos.json').write_text(json.dumps(creditos, ensure_ascii=False, indent=2), encoding='utf-8')
    print('ok creditos.json')


if __name__ == '__main__':
    main()
