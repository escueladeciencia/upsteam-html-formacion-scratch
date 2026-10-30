// Uso: node genera-recursos.js <carpeta con node_modules/playwright> <fondo.webp> <carpeta de salida>
// Abre genera-recursos.html en Chrome y guarda los disfraces (PNG), los fondos (JPG),
// los sonidos (MP3 y WAV) y el mapa de petardos (mapa.json).
const path = require('path');
const fs = require('fs');
const { chromium } = require(path.join(process.argv[2], 'node_modules', 'playwright'));

(async () => {
  const fondo = 'data:image/webp;base64,' + fs.readFileSync(process.argv[3]).toString('base64');
  const out = process.argv[4];
  fs.mkdirSync(out, { recursive: true });
  const b = await chromium.launch({ channel: 'chrome', headless: true });
  const p = await b.newPage();
  p.on('pageerror', (e) => console.error('ERROR', e.message));
  await p.goto('file:///' + path.join(__dirname, 'genera-recursos.html').replace(/\\/g, '/'));
  const r = await p.evaluate((f) => window.genera(f), fondo);
  const guarda = (nombre, dataUrl) => fs.writeFileSync(path.join(out, nombre), Buffer.from(dataUrl.split(',')[1], 'base64'));
  for (const [nombre, url] of Object.entries(r.costums)) guarda(nombre + '.png', url);
  for (const [nombre, url] of Object.entries(r.fons)) guarda('fondo-' + nombre + '.jpg', url);
  const sonidos = {};
  for (const [nombre, s] of Object.entries(r.sons)) {
    const ext = s.ext || 'wav';
    fs.writeFileSync(path.join(out, nombre + '.' + ext), Buffer.from(s.b64, 'base64'));
    sonidos[nombre] = { muestras: s.mostres, rate: s.rate, ext };
  }
  fs.writeFileSync(path.join(out, 'mapa.json'), JSON.stringify({ mapa: r.mapa, sonidos, centro: r.centre }, null, 1));
  console.log('disfraces:', Object.keys(r.costums).length, '· fondos:', Object.keys(r.fons).length, '· sonidos:', Object.keys(r.sons).length, '· petardos:', r.mapa.length);
  await b.close();
})();
