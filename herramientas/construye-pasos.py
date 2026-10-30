"""Construye los 10 pasos del juego de Scratch «Masclet a masclet».

Uso: python -I construye-pasos.py <carpeta de recursos> <carpeta scratch de la formación>

Cada paso se define una sola vez (los bloques, en el árbol de abajo). De esa definición salen:
  - scratch/paso-NN.sb3: el proyecto de Scratch de ese paso.
  - scratch/pasos.js: el código de cada guion en formato scratchblocks, para dibujarlo en las diapositivas,
    el id de cada bloque en el orden en que se dibuja (para iluminar el que se está ejecutando) y los
    ids de los bloques que añade ese paso respecto al anterior (para marcarlos como nuevos).
  - scratch/paso-03-error.sb3: la primera idea del paso 3, con el error de la mecha, para probarlo.
  - scratch/plantilla.sb3 y scratch/tiempos.txt: el punto de partida del alumnado (ver fichas/).
Así, lo que se ve en la formación es exactamente lo que hay dentro de cada .sb3.

El código está escrito como lo haría un niño con la ayuda del docente, no de la forma más corta.
"""
import copy
import hashlib
import json
import sys
import zipfile
from pathlib import Path

REC = Path(sys.argv[1])
SALIDA = Path(sys.argv[2])
DATOS = json.loads((REC / 'mapa.json').read_text(encoding='utf-8'))
MAPA = DATOS['mapa']


# ======================= Árbol de bloques =======================
class V:
    """Una variable dentro de un hueco: (n), (decibelios)…"""
    def __init__(self, nombre):
        self.nombre = nombre


class B:
    """Un bloque. tipo: 'pila', 'hat', 'cap', 'r' (redondo) o 'b' (hexagonal).
    sb: plantilla scratchblocks en inglés; {NOMBRE} se cambia por el hueco, el menú o el campo."""
    def __init__(self, op, sb, tipo='pila', huecos=None, campos=None, menus=None, ver=None, subs=None, mutation=None, sb_c=None):
        self.op, self.sb, self.tipo = op, sb, tipo
        self.huecos = huecos or {}   # NOMBRE -> (tipo de sombra, valor)
        self.campos = campos or {}   # NOMBRE -> [valor, id] o ('var'|'lista', nombre)
        self.menus = menus or {}     # NOMBRE -> (opcode del menú, campo, valor)
        self.ver = ver or {}         # NOMBRE -> cómo se lee en castellano en el desplegable
        self.subs = subs or {}       # SUBSTACK, SUBSTACK2 -> [bloques]
        self.mutation = mutation
        self.sb_c = sb_c             # bloques en C: texto entre las dos bocas ('else')
        self.comentario = None


def fmt(v):
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    return str(v)


# ---------- Bloques que usamos (nombres en castellano, como se ven en Scratch) ----------
def al_hacer_clic_bandera(): return B('event_whenflagclicked', 'when flag clicked', 'hat')
def al_hacer_clic_objeto(): return B('event_whenthisspriteclicked', 'when this sprite clicked', 'hat')
def al_presionar_tecla(k, ver): return B('event_whenkeypressed', 'when {KEY_OPTION} key pressed', 'hat', campos={'KEY_OPTION': [k, None]}, ver={'KEY_OPTION': ver})
def al_comenzar_como_clon(): return B('control_start_as_clone', 'when I start as a clone', 'hat')
def mostrar(): return B('looks_show', 'show')
def ir_a_capa_trasera(): return B('looks_gotofrontback', 'go to {FRONT_BACK} layer', campos={'FRONT_BACK': ['back', None]}, ver={'FRONT_BACK': 'trasera'})
def esconder(): return B('looks_hide', 'hide')
def cambiar_disfraz(n): return B('looks_switchcostumeto', 'switch costume to {COSTUME}', menus={'COSTUME': ('looks_costume', 'COSTUME', n)})
def siguiente_disfraz(): return B('looks_nextcostume', 'next costume')
def cambiar_fondo(n): return B('looks_switchbackdropto', 'switch backdrop to {BACKDROP}', menus={'BACKDROP': ('looks_backdrops', 'BACKDROP', n)})
def numero_de_disfraz(): return B('looks_costumenumbername', '(costume {NUMBER_NAME})', 'r', campos={'NUMBER_NAME': ['number', None]}, ver={'NUMBER_NAME': 'número'})
def iniciar_sonido(n): return B('sound_play', 'start sound {SOUND_MENU}', menus={'SOUND_MENU': ('sound_sounds_menu', 'SOUND_MENU', n)})
def detener_sonidos(): return B('sound_stopallsounds', 'stop all sounds')
def esperar(s): return B('control_wait', 'wait {DURATION} seconds', huecos={'DURATION': (5, s)})
def repetir(n, cuerpo): return B('control_repeat', 'repeat {TIMES}', huecos={'TIMES': (6, n)}, subs={'SUBSTACK': cuerpo})
def si(cond, cuerpo): return B('control_if', 'if {CONDITION} then', huecos={'CONDITION': (None, cond)}, subs={'SUBSTACK': cuerpo})
def esperar_hasta(cond): return B('control_wait_until', 'wait until {CONDITION}', huecos={'CONDITION': (None, cond)})
def detener_otros_programas():
    return B('control_stop', 'stop {STOP_OPTION}', campos={'STOP_OPTION': ['other scripts in sprite', None]},
             ver={'STOP_OPTION': 'otros programas en el objeto'}, mutation={'tagName': 'mutation', 'children': [], 'hasnext': 'true'})
def crear_clon(): return B('control_create_clone_of', 'create clone of {CLONE_OPTION}', menus={'CLONE_OPTION': ('control_create_clone_of_menu', 'CLONE_OPTION', '_myself_')}, ver={'CLONE_OPTION': 'mí mismo'})
def eliminar_clon(): return B('control_delete_this_clone', 'delete this clone', 'cap')
def ir_a(x, y): return B('motion_gotoxy', 'go to x: {X} y: {Y}', huecos={'X': (4, x), 'Y': (4, y)})
def aleatorio(a, b): return B('operator_random', '(pick random {FROM} to {TO})', 'r', huecos={'FROM': (4, a), 'TO': (4, b)})
def mayor(a, b): return B('operator_gt', '<{OPERAND1} > {OPERAND2}>', 'b', huecos={'OPERAND1': (10, a), 'OPERAND2': (10, b)})
def resta(a, b): return B('operator_subtract', '({NUM1} - {NUM2})', 'r', huecos={'NUM1': (4, a), 'NUM2': (4, b)})
def cronometro(): return B('sensing_timer', '(timer)', 'r')
def reiniciar_cronometro(): return B('sensing_resettimer', 'reset timer')
def raton_x(): return B('sensing_mousex', '(mouse x)', 'r')
def raton_y(): return B('sensing_mousey', '(mouse y)', 'r')
def dar_valor(var, v): return B('data_setvariableto', 'set {VARIABLE} to {VALUE}', huecos={'VALUE': (10, v)}, campos={'VARIABLE': ('var', var)})
def sumar(var, v): return B('data_changevariableby', 'change {VARIABLE} by {VALUE}', huecos={'VALUE': (4, v)}, campos={'VARIABLE': ('var', var)})
def elemento(i, lista): return B('data_itemoflist', '(item {INDEX} of {LIST})', 'r', huecos={'INDEX': (7, i)}, campos={'LIST': ('lista', lista)})
def longitud(lista): return B('data_lengthoflist', '(length of {LIST})', 'r', campos={'LIST': ('lista', lista)})
def anadir(v, lista): return B('data_addtolist', 'add {ITEM} to {LIST}', huecos={'ITEM': (10, v)}, campos={'LIST': ('lista', lista)})
def borrar_todo(lista): return B('data_deletealloflist', 'delete all of {LIST}', campos={'LIST': ('lista', lista)})


# ======================= De árbol a scratchblocks =======================
def sb_hueco(valor):
    if isinstance(valor, B):
        return sb_reporter(valor)
    if isinstance(valor, V):
        return f'({valor.nombre})' if len(valor.nombre) > 1 else f'({valor.nombre} :: variables)'
    return f'({fmt(valor)})'


def sb_reporter(b):
    t = b.sb
    for n, (_, v) in b.huecos.items():
        t = t.replace('{' + n + '}', sb_hueco(v))
    for n, v in b.campos.items():
        visto = b.ver.get(n) or (v[1] if isinstance(v, tuple) else v[0])
        t = t.replace('{' + n + '}', f'[{visto} v]')
    for n, (_, _, v) in b.menus.items():
        t = t.replace('{' + n + '}', f'[{b.ver.get(n, v)} v]')
    return t


def sb_pila(bloques, nivel=0):
    lineas = []
    for b in bloques:
        lineas.append('  ' * nivel + sb_reporter(b))
        if b.subs:
            lineas += sb_pila(b.subs.get('SUBSTACK', []), nivel + 1)
            if 'SUBSTACK2' in b.subs:
                lineas.append('  ' * nivel + 'else')
                lineas += sb_pila(b.subs['SUBSTACK2'], nivel + 1)
            lineas.append('  ' * nivel + 'end')
    return lineas


# ======================= De árbol a project.json =======================
class Emisor:
    def __init__(self, prefijo, ids_var, ids_lista):
        self.bloques, self.n, self.prefijo = {}, 0, prefijo
        self.ids_var, self.ids_lista, self.comentarios = ids_var, ids_lista, {}
        # Los bloques en el orden en que scratchblocks los dibuja (cada bloque, luego sus reporteros y sus
        # bocas). Una variable dentro de un hueco se dibuja como bloque pero no tiene id: va como None.
        self.orden = []
        # Cada bloque de pila con su texto y sus ids (el suyo y los de sus reporteros), para saber qué es nuevo
        self.grupos, self.fin_propios = [], {}

    def nid(self):
        self.n += 1
        return f'{self.prefijo}{self.n}'

    def campo(self, v):
        if isinstance(v, tuple):
            clase, nombre = v
            return [nombre, (self.ids_var if clase == 'var' else self.ids_lista)[nombre]]
        return v

    def hueco(self, valor, sombra, padre):
        if isinstance(valor, B):
            hijo = self.bloque(valor, padre)
            return [2, hijo] if valor.tipo == 'b' else [3, hijo, [sombra, '']]
        if isinstance(valor, V):
            self.orden.append(None)
            return [3, [12, valor.nombre, self.ids_var[valor.nombre]], [sombra, '']]
        return [1, [sombra, fmt(valor)]]

    def bloque(self, b, padre, arriba=False, x=0, y=0):
        bid = self.nid()
        self.orden.append(bid)
        d = {'opcode': b.op, 'next': None, 'parent': padre, 'inputs': {}, 'fields': {}, 'shadow': False, 'topLevel': arriba}
        if arriba:
            d['x'], d['y'] = x, y
        if b.mutation:
            d['mutation'] = b.mutation
        self.bloques[bid] = d
        for n, (sombra, v) in b.huecos.items():
            d['inputs'][n] = self.hueco(v, sombra, bid)
        for n, (op_menu, campo, v) in b.menus.items():
            mid = self.nid()
            self.bloques[mid] = {'opcode': op_menu, 'next': None, 'parent': bid, 'inputs': {}, 'fields': {campo: [v, None]}, 'shadow': True, 'topLevel': False}
            d['inputs'][n] = [1, mid]
        for n, v in b.campos.items():
            d['fields'][n] = self.campo(v)
        self.fin_propios[bid] = len(self.orden)
        for n, pila in b.subs.items():
            if pila:
                d['inputs'][n] = [2, self.pila(pila, bid)]
        return bid

    def pila(self, bloques, padre, x=None, y=None):
        ids = []
        for i, b in enumerate(bloques):
            hueco_grupo, ini = len(self.grupos), len(self.orden)
            self.grupos.append(None)  # se reserva el sitio: los bloques de dentro de un C van después
            if i == 0:
                bid = self.bloque(b, padre, arriba=x is not None, x=x or 0, y=y or 0)
            else:
                bid = self.bloque(b, ids[-1])
                self.bloques[ids[-1]]['next'] = bid
            self.grupos[hueco_grupo] = (sb_reporter(b), [k for k in self.orden[ini:self.fin_propios[bid]] if k])
            ids.append(bid)
        return ids[0]

    def comentar(self, bid, texto, x, y):
        cid = f'{self.prefijo}c{len(self.comentarios) + 1}'
        self.comentarios[cid] = {'blockId': bid, 'x': x, 'y': y, 'width': 330, 'height': 150, 'minimized': False, 'text': texto}
        if bid:
            self.bloques[bid]['comment'] = cid


# ======================= Recursos (disfraces, fondos, sonidos) =======================
archivos = {}


def recurso(nombre):
    data = (REC / nombre).read_bytes()
    md5 = hashlib.md5(data).hexdigest()
    ext = nombre.rsplit('.', 1)[1]
    archivos[f'{md5}.{ext}'] = data
    return md5, ext


def disfraz(nombre, archivo, centro):
    md5, ext = recurso(archivo)
    return {'name': nombre, 'bitmapResolution': 2, 'dataFormat': ext, 'assetId': md5, 'md5ext': f'{md5}.{ext}',
            'rotationCenterX': centro[0], 'rotationCenterY': centro[1]}


def sonido(nombre):
    info = DATOS['sonidos'][nombre]
    md5, ext = recurso(f"{nombre}.{info['ext']}")
    return {'name': nombre, 'assetId': md5, 'dataFormat': ext, 'format': '', 'rate': info['rate'],
            'sampleCount': info['muestras'], 'md5ext': f'{md5}.{ext}'}


CENTRO = DATOS['centro']['petard']
DISFRACES = ([disfraz(f'mecha{k}', f'mecha{k}.png', CENTRO) for k in range(1, 10)]
             + [disfraz('pum', 'pum.png', DATOS['centro']['pum']), disfraz('fallado', 'fallado.png', CENTRO)])
FONDOS = {n: disfraz(n, f'fondo-{n}.jpg', [480, 360]) for n in ('inicio', 'plaza', 'final')}
IDS_VAR = {'decibelios': 'vDecibelios', 'n': 'vN', 'traca': 'vTraca'}
IDS_LISTA = {'tiempos': 'lTiempos', 'x': 'lX', 'y': 'lY'}


# ======================= Los 10 pasos =======================
def la_mecha():
    return repetir(8, [esperar(0.125), siguiente_disfraz()])


def a_tiempo():
    return mayor(numero_de_disfraz(), 6)


def posicion_aleatoria():
    return ir_a(aleatorio(-180, 180), aleatorio(-80, 80))


def pasos():
    """Devuelve, para cada paso: título, guiones (objeto, bloques, comentario), variables, listas, sonidos, fondos."""
    P = {}

    # 1. Un petardo en la plaza
    g_bandera = [al_hacer_clic_bandera(), ir_a(0, 0), cambiar_disfraz('mecha1'), mostrar()]
    P[1] = dict(titulo='Un petardo en la plaza', guiones=[('bandera', g_bandera, 'Al pulsar la bandera verde, el petardo va al centro, se pone el primer disfraz y aparece.')])

    # 2. La mecha se quema
    g_bandera = [al_hacer_clic_bandera(), ir_a(0, 0), cambiar_disfraz('mecha1'), mostrar(), la_mecha()]
    P[2] = dict(titulo='La mecha se quema', guiones=[('bandera', g_bandera, 'La mecha se quema: 8 veces, espera 0,125 segundos y pasa al disfraz siguiente. 8 × 0,125 = 1 segundo.')])

    # 3. ¡PUM! al hacer clic
    g_clic = [al_hacer_clic_objeto(), detener_otros_programas(), cambiar_disfraz('pum'), iniciar_sonido('pum'), esperar(0.3), esconder()]
    # La primera idea, con el error que sale siempre en clase: sin «detener otros programas», la mecha sigue
    g_clic_error = [al_hacer_clic_objeto(), cambiar_disfraz('pum'), iniciar_sonido('pum'), esperar(0.3), esconder()]
    P[3] = dict(titulo='¡PUM! al hacer clic', guiones=[('bandera', copy.deepcopy(g_bandera), None),
                                                     ('clic', g_clic, 'Al hacer clic: primero para la mecha (detener otros programas). Después, PUM.')],
                variante=('03-error', dict(titulo='¡PUM! al hacer clic (primera idea, con un error)', guiones=[
                    ('bandera', copy.deepcopy(g_bandera), None),
                    ('clic', g_clic_error, 'Primera idea: al hacer clic, PUM. Haz clic pronto: ¿qué le pasa a la mecha?')])))

    # 4. Los decibelios: una variable
    g_bandera = [al_hacer_clic_bandera(), dar_valor('decibelios', 0), ir_a(0, 0), cambiar_disfraz('mecha1'), mostrar(), la_mecha()]
    g_clic = [al_hacer_clic_objeto(), detener_otros_programas(), cambiar_disfraz('pum'), iniciar_sonido('pum'), sumar('decibelios', 100), esperar(0.3), esconder()]
    P[4] = dict(titulo='Los decibelios: una variable', variables=['decibelios'],
                guiones=[('bandera', g_bandera, 'Al empezar, los decibelios valen 0.'), ('clic', g_clic, 'Cada PUM suma 100 decibelios.')])

    # 5. ¿A tiempo o fallado?
    g_bandera = [al_hacer_clic_bandera(), dar_valor('decibelios', 0), ir_a(0, 0), cambiar_disfraz('mecha1'), mostrar(), la_mecha(),
                 esperar(0.2), cambiar_disfraz('fallado'), iniciar_sonido('fsss'), esperar(0.5), esconder()]
    g_clic = [al_hacer_clic_objeto(), si(a_tiempo(), [detener_otros_programas(), cambiar_disfraz('pum'), iniciar_sonido('pum'),
                                                      sumar('decibelios', 100), esperar(0.3), esconder()])]
    P[5] = dict(titulo='¿A tiempo o fallado?', variables=['decibelios'],
                guiones=[('bandera', g_bandera, 'Si la mecha se acaba y nadie ha hecho clic, el petardo falla: fsss.'),
                         ('clic', g_clic, 'Solo explota si la mecha está casi acabada: disfraz 7, 8 o 9.')])

    # 6. Muchos petardos: clones
    g_bandera = [al_hacer_clic_bandera(), esconder(), dar_valor('decibelios', 0),
                 repetir(20, [posicion_aleatoria(), crear_clon(), esperar(1)])]
    g_clon = [al_comenzar_como_clon(), cambiar_disfraz('mecha1'), ir_a_capa_trasera(), mostrar(), la_mecha(),
              esperar(0.2), cambiar_disfraz('fallado'), iniciar_sonido('fsss'), esperar(0.5), eliminar_clon()]
    g_clic = [al_hacer_clic_objeto(), si(a_tiempo(), [detener_otros_programas(), cambiar_disfraz('pum'), iniciar_sonido('pum'),
                                                      sumar('decibelios', 100), esperar(0.3), eliminar_clon()])]
    # El programa del clon es el de la bandera del paso 5, trasladado: lo nuevo se busca comparándolo con ese
    P[6] = dict(titulo='Muchos petardos: clones', variables=['decibelios'], compara={'clon': 'bandera'},
                guiones=[('bandera', g_bandera, 'El objeto original no se ve: es la fábrica. Cada segundo, va a un sitio al azar y crea un clon.'),
                         ('clic', g_clic, 'Cada clon es un petardo. Al explotar, el clon se elimina.'),
                         ('clon', g_clon, 'Lo que hace cada petardo: aparece detrás de los demás, quema la mecha y, si nadie le hace clic, falla y desaparece.')])

    # 7. Con música (y el problema de «esperar»)
    g_bandera = [al_hacer_clic_bandera(), esconder(), dar_valor('decibelios', 0), iniciar_sonido('pasodoble'), esperar(3),
                 repetir(100, [posicion_aleatoria(), crear_clon(), esperar(0.5)])]
    P[7] = dict(titulo='Con música', variables=['decibelios'], musica=True,
                guiones=[('bandera', g_bandera, 'La música va a 120 golpes por minuto: un golpe cada 0,5 segundos. Un petardo en cada golpe… pero se va retrasando.'),
                         ('clic', copy.deepcopy(g_clic), None), ('clon', copy.deepcopy(g_clon), None)])

    # 8. Al ritmo: cronómetro y lista
    g_bandera = [al_hacer_clic_bandera(), esconder(), dar_valor('decibelios', 0), dar_valor('n', 1), iniciar_sonido('pasodoble'), reiniciar_cronometro(),
                 repetir(longitud('tiempos'), [esperar_hasta(mayor(cronometro(), resta(elemento(V('n'), 'tiempos'), 1))),
                                               posicion_aleatoria(), crear_clon(), sumar('n', 1)])]
    P[8] = dict(titulo='Al ritmo: cronómetro y lista', variables=['decibelios', 'n'], listas=['tiempos'], musica=True,
                guiones=[('bandera', g_bandera, 'La lista «tiempos» dice en qué segundo de la canción explota cada petardo. Se crea 1 segundo antes, cuando el cronómetro llega.'),
                         ('clic', copy.deepcopy(g_clic), None), ('clon', copy.deepcopy(g_clon), None)])

    # 9. Modo pirotécnico: graba tu mascletà
    g_bandera = [al_hacer_clic_bandera(), esconder(), dar_valor('decibelios', 0), dar_valor('n', 1), iniciar_sonido('pasodoble'), reiniciar_cronometro(),
                 repetir(longitud('tiempos'), [esperar_hasta(mayor(cronometro(), resta(elemento(V('n'), 'tiempos'), 1))),
                                               ir_a(elemento(V('n'), 'x'), elemento(V('n'), 'y')), crear_clon(), sumar('n', 1)])]
    g_grabar = [al_presionar_tecla('g', 'g'), borrar_todo('tiempos'), borrar_todo('x'), borrar_todo('y'),
                detener_sonidos(), iniciar_sonido('pasodoble'), reiniciar_cronometro()]
    g_espacio = [al_presionar_tecla('space', 'espacio'), anadir(cronometro(), 'tiempos'), anadir(raton_x(), 'x'), anadir(raton_y(), 'y')]
    P[9] = dict(titulo='Modo pirotécnico: graba tu mascletà', variables=['decibelios', 'n'], listas=['tiempos', 'x', 'y'], musica=True,
                guiones=[('bandera', g_bandera, 'Ahora cada petardo sale en su sitio: las listas x e y.'),
                         ('clic', copy.deepcopy(g_clic), None), ('clon', copy.deepcopy(g_clon), None),
                         ('tecla g', g_grabar, 'MODO PIROTÉCNICO. Tecla G: borra el mapa y empieza la canción para grabar uno nuevo.'),
                         ('tecla espacio', g_espacio, 'Mientras suena, pon el ratón donde quieras un petardo y pulsa ESPACIO al ritmo. Se guarda el segundo y el sitio.')])

    # 10. Remate: traca, pantallas y final
    g_bandera = [al_hacer_clic_bandera(), cambiar_fondo('plaza'), esconder(), dar_valor('decibelios', 0), dar_valor('traca', 0), dar_valor('n', 1),
                 iniciar_sonido('pasodoble'), reiniciar_cronometro(),
                 repetir(longitud('tiempos'), [esperar_hasta(mayor(cronometro(), resta(elemento(V('n'), 'tiempos'), 1))),
                                               ir_a(elemento(V('n'), 'x'), elemento(V('n'), 'y')), crear_clon(), sumar('n', 1)]),
                 esperar_hasta(mayor(cronometro(), 62)), cambiar_fondo('final')]
    g_clon = [al_comenzar_como_clon(), cambiar_disfraz('mecha1'), ir_a_capa_trasera(), mostrar(), la_mecha(),
              esperar(0.2), cambiar_disfraz('fallado'), iniciar_sonido('fsss'), dar_valor('traca', 0), esperar(0.5), eliminar_clon()]
    g_clic = [al_hacer_clic_objeto(), si(a_tiempo(), [detener_otros_programas(), cambiar_disfraz('pum'), iniciar_sonido('pum'),
                                                      sumar('decibelios', 100), sumar('traca', 1), esperar(0.3), eliminar_clon()])]
    P[10] = dict(titulo='Remate: traca, pantallas y final', variables=['decibelios', 'traca', 'n'], listas=['tiempos', 'x', 'y'], musica=True,
                 fondos=['inicio', 'plaza', 'final'],
                 guiones=[('bandera', g_bandera, 'Pantalla de la plaza al empezar y pantalla final cuando acaba la canción (segundo 62).'),
                          ('clic', g_clic, 'La traca cuenta los aciertos seguidos.'),
                          ('clon', g_clon, 'Si un petardo falla, la traca vuelve a 0.'),
                          ('tecla g', copy.deepcopy(g_grabar), None), ('tecla espacio', copy.deepcopy(g_espacio), None)])
    return P


POSICION = {'bandera': (40, 40), 'clic': (1100, 40), 'clon': (40, 1000), 'tecla g': (1100, 640), 'tecla espacio': (1100, 1000)}
COMENTARIO_X = {'bandera': 640, 'clic': 1640, 'clon': 640, 'tecla g': 1640, 'tecla espacio': 1640}


def nuevos(antes, ahora):
    """Posiciones de «ahora» que no están en la subsecuencia común más larga con «antes» (listas de textos de bloque)."""
    n, m = len(antes), len(ahora)
    L = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n - 1, -1, -1):
        for j in range(m - 1, -1, -1):
            L[i][j] = L[i + 1][j + 1] + 1 if antes[i] == ahora[j] else max(L[i + 1][j], L[i][j + 1])
    i = j = 0
    comunes = set()
    while i < n and j < m:
        if antes[i] == ahora[j]:
            comunes.add(j)
            i, j = i + 1, j + 1
        elif L[i + 1][j] >= L[i][j + 1]:
            i += 1
        else:
            j += 1
    return [k for k in range(m) if k not in comunes]


def construye(nombre, etiqueta, p, anterior, archivo=None):
    """anterior: los textos de los bloques de cada guion del paso anterior (None en el paso 1). Con ellos
    se apunta en «nuevos» qué bloques añade este paso, para marcarlos en las diapositivas."""
    variables, listas = p.get('variables', []), p.get('listas', [])
    em = Emisor('p', IDS_VAR, IDS_LISTA)
    textos = []
    for clave, bloques, comentario in p['guiones']:
        x, y = POSICION[clave]
        em.orden, em.grupos = [], []
        cabeza = em.pila(bloques, None, x, y)
        if comentario:
            em.comentar(cabeza, comentario, COMENTARIO_X[clave], y)
        lineas = [texto for texto, _ in em.grupos]
        origen = p.get('compara', {}).get(clave, clave)  # el guion del paso anterior del que sale este
        marcados = [] if anterior is None else nuevos(anterior.get(origen, []), lineas)
        textos.append({'guion': clave, 'codigo': '\n'.join(sb_pila(bloques)), 'ids': em.orden, 'lineas': lineas,
                       'nuevos': [k for i in marcados for k in em.grupos[i][1]]})
    valores = {'tiempos': [m['t'] for m in MAPA], 'x': [m['x'] for m in MAPA], 'y': [m['y'] for m in MAPA]}
    nombres_fondo = p.get('fondos', ['plaza'])
    escenario = {
        'isStage': True, 'name': 'Stage',
        'variables': {IDS_VAR[v]: [v, 0] for v in variables},
        'lists': {IDS_LISTA[l]: [l, valores[l]] for l in listas},
        'broadcasts': {}, 'blocks': {}, 'comments': {}, 'currentCostume': 0,
        'costumes': [FONDOS[n] for n in nombres_fondo], 'sounds': [], 'volume': 100, 'layerOrder': 0,
        'tempo': 60, 'videoTransparency': 50, 'videoState': 'on', 'textToSpeechLanguage': None,
    }
    sonidos = [sonido('pum'), sonido('fsss')] + ([sonido('pasodoble')] if p.get('musica') else [])
    petardo = {
        'isStage': False, 'name': 'Petardo', 'variables': {}, 'lists': {}, 'broadcasts': {},
        'blocks': em.bloques, 'comments': em.comentarios, 'currentCostume': 0, 'costumes': DISFRACES, 'sounds': sonidos,
        'volume': 100, 'layerOrder': 1, 'visible': False, 'x': 0, 'y': 0, 'size': 100, 'direction': 90,
        'draggable': False, 'rotationStyle': 'all around',
    }
    monitores = [{'id': IDS_VAR[v], 'mode': 'default', 'opcode': 'data_variable', 'params': {'VARIABLE': v}, 'spriteName': None,
                  'value': 0, 'width': 0, 'height': 0, 'x': 5, 'y': 5 + 27 * i, 'visible': True, 'sliderMin': 0, 'sliderMax': 100,
                  'isDiscrete': True} for i, v in enumerate(x for x in variables if x != 'n')]
    proyecto = {'targets': [escenario, petardo], 'monitors': monitores, 'extensions': [],
                'meta': {'semver': '3.0.0', 'vm': '0.2.0', 'agent': f'Masclet a masclet · paso {etiqueta}'}}
    usados = {d['md5ext'] for d in petardo['costumes'] + escenario['costumes'] + sonidos}
    ruta = SALIDA / (archivo or f'paso-{nombre}.sb3')
    with zipfile.ZipFile(ruta, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('project.json', json.dumps(proyecto, ensure_ascii=False))
        for nombre in sorted(usados):
            z.writestr(nombre, archivos[nombre])
    return ruta, textos


SALIDA.mkdir(parents=True, exist_ok=True)
todos = {}
anterior = None
for numero, p in pasos().items():
    if 'variante' in p:  # otra versión del paso (la del error del paso 3), comparada con el paso anterior
        nombre, pv = p['variante']
        ruta, textos = construye(nombre, f'{numero} ({pv["titulo"]})', pv, anterior)
        todos[nombre.lstrip('0')] = {'titulo': pv['titulo'], 'sb3': ruta.name, 'guiones': textos}
        print(f'paso {nombre} · {ruta.stat().st_size // 1024:5d} KB · {pv["titulo"]}')
    ruta, textos = construye(f'{numero:02d}', numero, p, anterior)
    todos[numero] = {'titulo': p['titulo'], 'sb3': ruta.name, 'guiones': textos}
    anterior = {t['guion']: t['lineas'] for t in textos}
    print(f'paso {numero:2d} · {ruta.stat().st_size // 1024:5d} KB · {p["titulo"]}')
for paso in todos.values():  # las líneas solo servían para comparar
    for g in paso['guiones']:
        del g['lineas']
(SALIDA / 'pasos.js').write_text('/* Generado por herramientas/construye-pasos.py: no lo edites a mano. */\nwindow.TRO_PASOS = '
                                 + json.dumps(todos, ensure_ascii=False, indent=1) + ';\n', encoding='utf-8')
print('pasos.js escrito')

# Para el alumnado: el proyecto de partida (todos los disfraces, sonidos y fondos, y la lista «tiempos» ya llena,
# pero sin programas) y los 99 tiempos en un .txt, para importarlos en una lista si hace falta.
ruta, _ = construye('plantilla', 'plantilla para el alumnado', dict(titulo='Plantilla', guiones=[], listas=['tiempos'], musica=True,
                                                                  fondos=['plaza', 'inicio', 'final']), None, archivo='plantilla.sb3')
print(f'plantilla · {ruta.stat().st_size // 1024:5d} KB')
(SALIDA / 'tiempos.txt').write_text(''.join(fmt(m['t']) + '\n' for m in MAPA), encoding='utf-8')
print('tiempos.txt ·', len(MAPA), 'tiempos')
