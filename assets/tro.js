/* Componentes propios de la formación «Masclet a masclet» (se carga después de cdc.js).
 *
 *  1. Bloques de Scratch con scratchblocks. Se escriben en inglés y se ven en castellano:
 *       <pre class="sb">when flag clicked …</pre>
 *       <div class="sb" data-paso="3" data-guion="clic"></div>   código del paso 3, sacado de scratch/pasos.js
 *     data-escala cambia el tamaño (por defecto 1.6). Los bloques que añade ese paso respecto al
 *     anterior salen con borde verde («Lo nuevo de este paso»).
 *  2. Jugador de Scratch dentro de la diapositiva (Scaffolding, el motor de TurboWarp):
 *       <div class="jugador" data-sb3="../scratch/paso-03.sb3" data-nota="Haz clic en el petardo"></div>
 *     Se carga al pulsar «Probar», se para al cambiar de diapositiva y, mientras está activo,
 *     recibe el teclado (las flechas y la barra espaciadora no pasan de diapositiva).
 *     Ocupa el ancho de su columna; los botones van debajo del escenario, fuera del marco.
 *     data-portada pone una captura del juego de portada mientras no se ha pulsado «Probar».
 *     Si en la misma diapositiva están los bloques de ese paso (data-paso), el bloque que se está
 *     ejecutando se ilumina en amarillo mientras se juega. En los pasos sin música hay un selector
 *     de velocidad (Normal, Lenta, Muy lenta) para seguirlo bloque a bloque.
 *  3. Botón «Copiar» en los prompts: <div class="prompt"><div class="p-cab">…</div><pre>…</pre></div>
 *  4. Piezas pulsables: <div class="piezas"> con <button class="pieza" data-titulo="…">…<span class="que">explicación</span></button>.
 *  5. Vídeos con data-auto: se reproducen al llegar a su diapositiva y se paran al salir (sin autoplay,
 *     para que las miniaturas del carril no los reproduzcan).
 *  6. Ampliar: un <button class="ampliar"> dentro de un .ampliable le pone o le quita .ampliado
 *     (el CSS de cada diapositiva decide cómo se ve en grande). Esc o cambiar de diapositiva lo cierra.
 */
(function () {
  'use strict';

  /* ---------- 1. Bloques ---------- */
  function guionDePaso(paso, guion) {
    const p = (window.TRO_PASOS || {})[paso];
    return (p && p.guiones.find((x) => x.guion === guion)) || { codigo: '' };
  }
  // Cada vista de bloque guarda su <g> al dibujarse (scratchblocks solo lo guarda en los anidados)
  function guardaElementos(vista) {
    const b = vista.scripts[0] && vista.scripts[0].blocks[0];
    const proto = b && Object.getPrototypeOf(b);
    if (!proto || proto.troGuarda) return;
    const draw = proto.draw;
    proto.draw = function () { const g = draw.apply(this, arguments); this.el = g; return g; };
    proto.troGuarda = true;
  }
  // Los bloques en el orden en que se dibujan: cada bloque, luego sus reporteros y sus bocas.
  // Es el mismo orden que apunta construye-pasos.py en «ids».
  // Los bloques que añade este paso respecto al anterior («nuevos») se marcan en verde; si es todo el
  // programa, la caja dice «Programa nuevo». En una diapositiva concreta se puede elegir qué se marca
  // y con qué texto: data-nuevos="p10" data-etiqueta="La solución".
  function marcaBloques(vista, g, el) {
    const lista = [];
    const visita = (v) => {
      lista.push(v);
      v.children.forEach((c) => { if (c.isBlock) visita(c); else if (c.isScript) c.blocks.forEach(visita); });
    };
    vista.scripts.forEach((s) => s.blocks.forEach(visita));
    if (lista.length !== g.ids.length) return;
    const nuevos = new Set(el.dataset.nuevos !== undefined ? el.dataset.nuevos.split(/\s+/).filter(Boolean) : g.nuevos || []);
    lista.forEach((v, i) => {
      if (!g.ids[i] || !v.el) return;
      v.el.setAttribute('data-bid', g.ids[i]);
      if (nuevos.has(g.ids[i])) v.el.classList.add('sb-nuevo');
    });
    if (!nuevos.size) return;
    const todo = g.ids.every((id) => !id || nuevos.has(id));
    el.classList.add(todo ? 'todo-nuevo' : 'con-nuevos');
    el.dataset.etiquetaNuevo = el.dataset.etiqueta || (todo ? 'Programa nuevo' : 'Lo nuevo de este paso');
  }
  function dibujaBloques() {
    if (!window.scratchblocks) return;
    scratchblocks.appendStyles();
    document.querySelectorAll('.sb:not([data-dibujado])').forEach((el) => {
      const g = el.dataset.paso ? guionDePaso(el.dataset.paso, el.dataset.guion) : { codigo: el.textContent };
      if (!g.codigo.trim()) return;
      try {
        const doc = scratchblocks.parse(g.codigo.trim(), { languages: ['en'] });
        doc.translate(scratchblocks.allLanguages.es);
        const vista = scratchblocks.newView(doc, { style: 'scratch3', scale: parseFloat(el.dataset.escala || '1.6') });
        guardaElementos(vista);
        const svg = vista.render();
        svg.classList.add('scratchblocks-style-scratch3');
        if (g.ids) marcaBloques(vista, g, el);
        el.textContent = '';
        el.appendChild(svg);
        el.dataset.dibujado = '';
        el.setAttribute('role', 'img');
        el.setAttribute('aria-label', 'Bloques de Scratch: ' + svg.textContent.replace(/\s+/g, ' ').trim());
      } catch (e) { /* si falla, se queda el texto */ }
    });
  }

  /* ---------- 2. Jugador de Scratch ---------- */
  const jugadores = new Map();
  const sinServidor = location.protocol === 'file:';

  // Velocidades: en lento, los «esperar» duran más y cada bloque se para un momento antes de ejecutarse,
  // para seguir con la vista el bloque iluminado. No se ofrece en los pasos que van con la música
  // (cronómetro y pasodoble): la canción no se puede frenar y se descuadraría.
  const VELOCIDADES = [
    { nombre: 'Normal', espera: 1, pausa: 0 },
    { nombre: 'Lenta', espera: 3, pausa: 350 },
    { nombre: 'Muy lenta', espera: 6, pausa: 900 },
  ];
  const CON_PAUSA = ['motion_gotoxy', 'looks_switchcostumeto', 'looks_nextcostume', 'looks_show', 'looks_hide', 'looks_gotofrontback',
    'looks_switchbackdropto', 'sound_play', 'sound_stopallsounds', 'data_setvariableto', 'data_changevariableby', 'data_addtolist',
    'data_deletealloflist', 'control_create_clone_of', 'control_delete_this_clone', 'sensing_resettimer'];
  // El paso de un jugador sale del nombre del .sb3: paso-03.sb3 → «3»; paso-03-error.sb3 → «3-error»
  function pasoDe(el) {
    const m = /paso-([\w-]+)\.sb3/.exec(el.dataset.sb3 || '');
    return m ? m[1].replace(/^0+/, '') : null;
  }
  function admiteLento(el) {
    const p = (window.TRO_PASOS || {})[pasoDe(el)];
    return !!p && !p.guiones.some((g) => /\btimer\b|pasodoble/.test(g.codigo));
  }
  // Se cambian las funciones de los bloques antes de la primera ejecución (Scratch las guarda al ejecutar)
  function frena(runtime, el) {
    const p = runtime._primitives;
    const espera = p.control_wait;
    p.control_wait = (args, util) => espera(Object.assign({}, args, { DURATION: Number(args.DURATION) * el.troVel.espera }), util);
    CON_PAUSA.forEach((op) => {
      const original = p[op];
      if (!original) return;
      p[op] = (args, util) => {
        const ms = el.troVel.pausa;
        if (ms && util.stackTimerNeedsInit()) { util.startStackTimer(ms); util.yield(); return; }
        if (ms && !util.stackTimerFinished()) { util.yield(); return; }
        return original(args, util);
      };
    });
  }

  function montaJugador(el) {
    if (el.dataset.montado !== undefined) return;
    el.dataset.montado = '';
    el.tabIndex = 0;
    el.setAttribute('aria-label', 'Proyecto de Scratch para probar');
    el.troVel = VELOCIDADES[0];
    const sb3 = el.dataset.sb3, lento = admiteLento(el);
    // .minimo (el portal): solo un botón de jugar y «Descargar .sb3»; al acabar la partida vuelve el botón
    const minimo = el.classList.contains('minimo');
    const nota = (el.dataset.nota || '') + (bloquesDelJugador(el).size ? ' Mientras se juega, el bloque que se está ejecutando se ilumina en amarillo.' : '');
    const tapa = minimo ? '<button class="j-play j-play-icono" type="button" aria-label="Jugar">▶</button>'
      : '<button class="btn j-play" type="button">▶ Probar</button>' + (nota ? '<p>' + nota + '</p>' : '');
    el.innerHTML =
      '<div class="j-marco"><div class="j-escena"></div>' +
      '<div class="j-tapa">' + tapa + '</div>' +
      '<div class="j-aviso">Para probar el juego aquí, abre la formación desde la web o con un servidor local. También puedes descargar el .sb3 y abrirlo en Scratch.</div></div>' +
      (minimo ? '<p class="j-nota"><a href="' + sb3 + '" download>Descargar .sb3</a></p>'
        : '<div class="j-barra"><button class="j-ban" type="button">⚑ Empezar</button><button class="j-stop" type="button">■ Parar</button>' +
          (lento ? '<div class="j-vel" role="group" aria-label="Velocidad"><span>Velocidad</span>' +
            VELOCIDADES.map((v, i) => '<button type="button" data-v="' + i + '" aria-pressed="' + (i === 0) + '">' + v.nombre + '</button>').join('') + '</div>' : '') +
          '</div>' +
          '<p class="j-nota"><a href="' + sb3 + '" download>Descargar .sb3</a> · Haz clic dentro del juego para usar el teclado. Esc para salir.</p>');
    if (el.dataset.portada) el.querySelector('.j-escena').style.backgroundImage = 'url("' + el.dataset.portada + '")';
    el.querySelector('.j-play').addEventListener('click', () => arranca(el));
    if (minimo) return;
    el.querySelector('.j-ban').addEventListener('click', () => arranca(el));
    el.querySelector('.j-stop').addEventListener('click', () => { const j = jugadores.get(el); if (j) j.s.stopAll(); });
    el.querySelectorAll('.j-vel button').forEach((b) => b.addEventListener('click', () => {
      el.troVel = VELOCIDADES[Number(b.dataset.v)];
      el.querySelectorAll('.j-vel button').forEach((o) => o.setAttribute('aria-pressed', String(o === b)));
    }));
  }

  async function arranca(el) {
    if (sinServidor) { el.classList.add('sin-servidor'); return; }
    let j = jugadores.get(el);
    if (!j) {
      if (!window.Scaffolding) return;
      el.classList.add('cargando');
      const s = new Scaffolding.Scaffolding();
      s.width = 480; s.height = 360; s.resizeMode = 'preserve-ratio';
      s.setup();
      s.vm.setCompilerOptions({ enabled: false }); // sin compilar, cada hilo dice en qué bloque está
      if (admiteLento(el)) frena(s.vm.runtime, el);
      s.appendTo(el.querySelector('.j-escena'));
      try {
        const r = await fetch(el.dataset.sb3);
        await s.loadProject(await r.arrayBuffer());
      } catch (e) {
        el.classList.add('sin-servidor');
        return;
      }
      j = { s };
      jugadores.set(el, j);
      el.classList.remove('cargando');
      if (el.classList.contains('minimo')) s.vm.runtime.on('PROJECT_RUN_STOP', () => el.classList.remove('cargado'));
    }
    el.classList.add('cargado');
    j.s.greenFlag();
    el.focus({ preventScroll: true });
    ilumina(el, j);
  }

  // El bloque que se está ejecutando, iluminado en los bloques de la diapositiva
  const RASTRO = 300; // ms que sigue iluminado un bloque instantáneo (siguiente disfraz, mostrar…)
  const rastros = new WeakMap(); // runtime → (id del bloque → momento en que se ejecutó)
  function bloquesDelJugador(el) {
    const paso = pasoDe(el), s = el.closest('section');
    const nodos = new Map();
    if (paso && s) s.querySelectorAll('.sb[data-paso="' + paso + '"] [data-bid]').forEach((g) => {
      if (!nodos.has(g.dataset.bid)) nodos.set(g.dataset.bid, []);
      nodos.get(g.dataset.bid).push(g);
    });
    return nodos;
  }
  // Los bloques instantáneos empiezan y acaban dentro del mismo fotograma: se apuntan al pasar por ellos
  function apuntaPasos(hilo) {
    const proto = Object.getPrototypeOf(hilo);
    if (proto.troApunta) return;
    ['pushStack', 'reuseStackForNextBlock'].forEach((nombre) => {
      const original = proto[nombre];
      proto[nombre] = function (id) {
        const r = this.target && rastros.get(this.target.runtime);
        if (r && id) r.set(id, performance.now());
        return original.apply(this, arguments);
      };
    });
    proto.troApunta = true;
  }
  function ilumina(el, j) {
    if (j.iluminando) return;
    const nodos = bloquesDelJugador(el), s = el.closest('section'), runtime = j.s.vm.runtime;
    if (!nodos.size) return;
    if (!rastros.has(runtime)) rastros.set(runtime, new Map());
    const vistos = rastros.get(runtime);
    j.iluminando = true;
    const cajas = new Set();
    nodos.forEach((gs) => gs.forEach((g) => cajas.add(g.closest('.sb'))));
    const pinta = (estado) => {
      let alguno = false;
      nodos.forEach((gs, id) => {
        const e = estado.get(id);
        if (e) alguno = true;
        gs.forEach((g) => {
          g.classList.toggle('sb-ahora', e === 'ahora');
          g.classList.toggle('sb-guion', e === 'guion');
          g.classList.toggle('sb-rastro', e === 'rastro');
        });
      });
      cajas.forEach((c) => c.classList.toggle('en-marcha', alguno));
    };
    const paso = () => {
      if (!s.hasAttribute('data-deck-active')) { pinta(new Map()); j.iluminando = false; return; }
      const estado = new Map(), ahora = performance.now();
      runtime.threads.forEach((h) => {
        if (h.status === 4 || !h.stack.length) return; // 4: hilo acabado
        apuntaPasos(h);
        // el último de la pila es el que se ejecuta; los de debajo lo contienen (repetir, si…)
        h.stack.forEach((id, i) => estado.set(id, i === h.stack.length - 1 ? 'ahora' : 'guion'));
        if (!estado.has(h.topBlock)) estado.set(h.topBlock, 'guion');
      });
      vistos.forEach((t, id) => {
        if (ahora - t > RASTRO) vistos.delete(id);
        else if (!estado.has(id)) estado.set(id, 'rastro');
      });
      pinta(estado);
      requestAnimationFrame(paso);
    };
    requestAnimationFrame(paso);
  }

  // El teclado va al juego mientras el foco está dentro del jugador
  function jugadorConFoco() {
    const el = document.activeElement && document.activeElement.closest && document.activeElement.closest('.jugador');
    return el ? { el, j: jugadores.get(el) } : null;
  }
  function teclado(isDown) {
    return (e) => {
      const a = jugadorConFoco();
      if (!a || e.ctrlKey || e.metaKey || e.altKey) return;
      if (e.key === 'Escape') { if (isDown) a.el.blur(); return; }
      e.stopPropagation(); // con el foco en el jugador, ninguna tecla pasa de diapositiva
      if (e.target.tagName === 'BUTTON' && (e.key === 'Enter' || e.key === ' ')) return; // el botón hace lo suyo
      e.preventDefault();
      if (a.j) a.j.s.vm.postIOData('keyboard', { key: e.key, isDown });
    };
  }
  window.addEventListener('keydown', teclado(true), true);
  window.addEventListener('keyup', teclado(false), true);

  // Al cambiar de diapositiva, para los juegos que se quedan atrás
  document.addEventListener('slidechange', (e) => {
    const actual = e.detail && e.detail.slide;
    jugadores.forEach((j, el) => { if (!actual || !actual.contains(el)) j.s.stopAll(); });
  });

  /* ---------- 3. Prompts ---------- */
  function botonesCopiar() {
    document.querySelectorAll('.prompt:not([data-copiar])').forEach((p) => {
      p.dataset.copiar = '';
      const b = document.createElement('button');
      b.type = 'button';
      b.className = 'btn peq copiar';
      b.textContent = 'Copiar el prompt';
      b.addEventListener('click', async () => {
        try { await navigator.clipboard.writeText(p.querySelector('pre').textContent.trim()); b.textContent = 'Copiado'; }
        catch (e) { b.textContent = 'Selecciónalo y cópialo'; }
        setTimeout(() => { b.textContent = 'Copiar el prompt'; }, 1800);
      });
      p.appendChild(b);
    });
  }

  /* ---------- 4. Piezas pulsables con su explicación ---------- */
  function relativa(n, cont) {
    let x = 0, y = 0;
    const w = n.offsetWidth, h = n.offsetHeight;
    while (n && n !== cont) { x += n.offsetLeft; y += n.offsetTop; n = n.offsetParent; }
    return { x, y, w, h };
  }
  function piezas() {
    document.querySelectorAll('.piezas').forEach((cont) => {
      const info = document.createElement('div');
      info.className = 'pieza-info';
      info.hidden = true;
      info.setAttribute('role', 'status');
      cont.appendChild(info);
      const cierra = () => { info.hidden = true; cont.querySelectorAll('.pieza').forEach((o) => o.setAttribute('aria-expanded', 'false')); };
      cont.querySelectorAll('.pieza').forEach((b) => {
        b.setAttribute('aria-expanded', 'false');
        b.addEventListener('click', (e) => {
          e.stopPropagation();
          const abierta = b.getAttribute('aria-expanded') === 'true';
          cierra();
          if (abierta) return;
          b.setAttribute('aria-expanded', 'true');
          info.innerHTML = '<b>' + (b.dataset.titulo || '') + '</b>' + b.querySelector('.que').innerHTML;
          info.hidden = false;
          const r = relativa(b, cont), ancho = info.offsetWidth, alto = info.offsetHeight;
          const izq = Math.max(0, Math.min(r.x + r.w / 2 - ancho / 2, cont.offsetWidth - ancho));
          info.style.left = izq + 'px';
          info.style.setProperty('--flecha', Math.max(16, Math.min(ancho - 44, r.x + r.w / 2 - izq - 14)) + 'px');
          const arriba = r.y + r.h + 18 + alto > cont.offsetHeight + 60 && r.y - alto - 18 > -200;
          info.classList.toggle('arriba', arriba);
          info.style.top = (arriba ? r.y - alto - 18 : r.y + r.h + 18) + 'px';
        });
      });
      document.addEventListener('click', (e) => { if (!cont.contains(e.target)) cierra(); });
      document.addEventListener('slidechange', cierra);
    });
  }

  /* ---------- 5. Vídeos que se reproducen solos en su diapositiva ---------- */
  const sinMovimiento = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  document.addEventListener('slidechange', (e) => {
    const actual = e.detail && e.detail.slide;
    document.querySelectorAll('video[data-auto]').forEach((v) => {
      if (actual && actual.contains(v) && !sinMovimiento) { const p = v.play(); if (p) p.catch(() => {}); }
      else v.pause();
    });
  });

  /* ---------- 6. Ampliar ---------- */
  function ampliables() {
    document.querySelectorAll('.ampliable').forEach((el) => {
      const b = el.querySelector('.ampliar');
      const pon = (si) => {
        el.classList.toggle('ampliado', si);
        b.textContent = si ? '✕ Cerrar' : '⤢ Ampliar';
        b.setAttribute('aria-pressed', String(si));
        // una explicación abierta se quedaría en su sitio de antes
        el.querySelectorAll('.pieza-info').forEach((i) => { i.hidden = true; });
        el.querySelectorAll('.pieza').forEach((p) => p.setAttribute('aria-expanded', 'false'));
      };
      b.addEventListener('click', () => pon(!el.classList.contains('ampliado')));
      window.addEventListener('keydown', (e) => { if (e.key === 'Escape' && el.classList.contains('ampliado')) pon(false); });
      document.addEventListener('slidechange', () => pon(false));
    });
  }

  dibujaBloques();
  document.querySelectorAll('.jugador').forEach(montaJugador);
  botonesCopiar();
  piezas();
  ampliables();
})();
