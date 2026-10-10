// The euro look shared by K12 lessons: warm sheet, blue words, gold accent, one slowly drifting camera.
// LOOK.lesson(title, draw) registers the whole film as one shot; draw(t) paints everything in world space.
(() => {
  const P = { blue: '#1C3D8F', gold: '#C8922A', ring: '#D9A21B', paper: '#F3EBDC', soft: '#8A97BF' };
  const FONT = s => `700 ${Math.round(s)}px "Balsamiq Sans", "Pangolin", sans-serif`;
  function word(text, x, y, size = 54, a = 1, o = {}) {
    if (a < .02) return;
    letter(text, x, y, size, o.col || P.blue, { font: FONT(size), ink: false, alpha: clamp(a), ...o });
  }
  function ring(x, y, rx, ry, a = 1, key = 'focus') {
    if (a < .02) return;
    boilSeed(key);
    paint(ellPts(x, y, rx, ry, 40, 1), { ink: P.ring, sw: 2.2 * a });
  }
  function arrow(key, points, k = 1, col = P.gold) {
    if (k < .03) return;
    boilSeed(key);
    const curve = through(points, 16), n = Math.max(2, Math.floor(curve.length * clamp(k))), p = curve.slice(0, n);
    inkLine(p, 1.6, col, 'inkfine');
    const a = p[p.length - 2], b = p[p.length - 1], angle = Math.atan2(b[1] - a[1], b[0] - a[0]), h = 18;
    inkLine([[b[0] - h * Math.cos(angle - .48), b[1] - h * Math.sin(angle - .48)], b, [b[0] - h * Math.cos(angle + .48), b[1] - h * Math.sin(angle + .48)]], 1.4, col, 'inkfine', 0);
  }
  function sheet() {
    if (sheet.g) return sheet.g;
    const g = createGraphics(W, H); g.pixelDensity(1); const c = g.drawingContext, rnd = lcg(41);
    c.fillStyle = '#F8F2E6'; c.fillRect(0, 0, W, H);
    for (let i = 0; i < 16; i++) { const x = rnd() * W, y = rnd() * H, r = 320 + rnd() * 560, gr = c.createRadialGradient(x, y, 0, x, y, r); gr.addColorStop(0, `rgba(214,186,142,${.035 + rnd() * .05})`); gr.addColorStop(1, 'rgba(214,186,142,0)'); c.fillStyle = gr; c.fillRect(x - r, y - r, 2 * r, 2 * r); }
    const vig = c.createRadialGradient(W / 2, H / 2, H * .28, W / 2, H / 2, H * .82); vig.addColorStop(0, 'rgba(168,124,72,0)'); vig.addColorStop(.62, 'rgba(176,136,86,.05)'); vig.addColorStop(1, 'rgba(148,104,58,.42)'); c.fillStyle = vig; c.fillRect(0, 0, W, H);
    const im = c.getImageData(0, 0, W, H), rnd2 = lcg(7); for (let i = 0; i < im.data.length; i += 4) { const n = (rnd2() - .5) * 18; im.data[i] += n; im.data[i + 1] += n * .85; im.data[i + 2] += n * .55; } c.putImageData(im, 0, 0);
    return sheet.g = g;
  }
  // Line starts and ends come from the measured recording, so timing follows the voice.
  const L = i => CUES.lines[i], E = i => CUES.lines[i] + CUES.len[i];
  // Whisper writes some numbers as digits, so a keyword can be given as ['восемь', '8'].
  function K(i, token, occurrence = 0) {
    const norm = s => s.toLowerCase().replace(/ё/g, 'е').replace(/[^а-яa-z0-9әғқңөұүһі]/g, '');
    const tokens = [].concat(token).map(norm);
    const found = CUES.words[i].filter(w => tokens.some(tok => norm(w.word).includes(tok)));
    if (!found[occurrence]) throw Error(`Missing measured keyword L${i} ${token}`);
    return found[occurrence].start;
  }
  const fadeIn = (t, t0, d = .5) => ease(seg(t, t0, t0 + d));
  const fadeOut = (t, t0, d = .5) => 1 - ease(seg(t, t0, t0 + d));
  function lesson(title, draw) {
    shots([[0, t => {
      push(); resetMatrix(); translate(-W / 2, -H / 2); image(sheet(), 0, 0); pop();
      camBegin(960 + 7 * Math.sin(t * .31), 540 + 5 * Math.sin(t * .23 + 1), 1 + .012 * Math.sin(t * .17));
      draw(t);
      camEnd();
      if (title) word(title, 1724, 70, 26, .85, { screen: true });
      flushLetters();
    }]]);
  }
  window.LOOK = { P, FONT, word, ring, arrow, L, E, K, fadeIn, fadeOut, lesson };
})();
