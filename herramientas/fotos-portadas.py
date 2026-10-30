"""Fotos de mascletà para las portadas de los módulos, sacadas de Wikimedia Commons.

Baja cada foto, la recorta a la mitad derecha de la portada (960 × 1080, proporción 8:9) alrededor
de un punto de interés y la guarda en assets/img/portadas/temaN.webp. Apunta autor y licencia
en assets/img/portadas/creditos.json.

    python herramientas/fotos-portadas.py
"""
import io
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
DESTINO = RAIZ / 'assets' / 'img' / 'portadas'
UA = {'User-Agent': 'MascletFormacion/1.0 (formacion para docentes; raulibaper@gmail.com)'}
ANCHO, ALTO = 960, 1080

# módulo: (archivo de Commons, centro del recorte en fracciones de la imagen (x, y))
FOTOS = {
    'tema0': ('File:Congregation during a Mascletà, Valencia (Spain) 2018.jpg', (0.5, 0.55)),
    'tema1': ('File:Mascletà at Valencia, Spain, 2010 (DSC7155).jpg', (0.55, 0.5)),
    'tema2': ('File:104 - Mascletà Calle Pelayo Matemático Marzal.jpg', (0.5, 0.35)),
    'tema3': ("File:Masclets a punt d'esclatar.jpg", (0.5, 0.5)),
    'tema4': ('File:La atmosfera despues de una mascletá en la Plaza del Ayuntamiento, Valencia 2017.jpg', (0.62, 0.5)),
    'tema5': ('File:Fallas2017 Mascletà 06.jpg', (0.5, 0.5)),
}


def api(titulos):
    q = {'action': 'query', 'titles': '|'.join(titulos), 'prop': 'imageinfo', 'iiprop': 'url|extmetadata',
         'iiurlwidth': 2000, 'format': 'json'}
    url = 'https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode(q)
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return {p['title']: p['imageinfo'][0] for p in json.load(r)['query']['pages'].values()}


def recorta(im, xc, yc):
    """El mayor recorte 8:9 que cabe en la imagen, centrado lo más cerca posible de (xc, yc)."""
    W, H = im.size
    w, h = (W, W * ALTO / ANCHO) if W * ALTO / ANCHO <= H else (H * ANCHO / ALTO, H)
    x0 = min(max(0, xc * W - w / 2), W - w)
    y0 = min(max(0, yc * H - h / 2), H - h)
    return im.crop((round(x0), round(y0), round(x0 + w), round(y0 + h))).resize((ANCHO, ALTO), Image.LANCZOS)


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    DESTINO.mkdir(parents=True, exist_ok=True)
    info = api([titulo for titulo, _ in FOTOS.values()])
    limpia = lambda s: re.sub(r'<[^>]+>', '', s or '').strip()
    creditos = {}
    for tema, (titulo, (xc, yc)) in FOTOS.items():
        ii = info[titulo.replace('_', ' ')]
        m = ii['extmetadata']
        creditos[tema] = {'archivo': titulo[5:], 'autor': limpia(m['Artist']['value']),
                          'licencia': limpia(m['LicenseShortName']['value']), 'pagina': ii['descriptionurl']}
        with urllib.request.urlopen(urllib.request.Request(ii.get('thumburl') or ii['url'], headers=UA), timeout=300) as r:
            im = Image.open(io.BytesIO(r.read())).convert('RGB')
        recorta(im, xc, yc).save(DESTINO / f'{tema}.webp', 'WEBP', quality=82, method=6)
        print(f'{tema}: {im.size} · {creditos[tema]["autor"]} · {creditos[tema]["licencia"]}')
    (DESTINO / 'creditos.json').write_text(json.dumps(creditos, ensure_ascii=False, indent=2), encoding='utf-8')
    print('ok creditos.json')


if __name__ == '__main__':
    main()
