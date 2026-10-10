(() => {
  const { P, FONT, word, L, E, K, fadeIn, fadeOut } = LOOK;
  const s = 122, X0 = 320, Y0 = 860, S = 3 * s, EQX = 1400, EQ0 = 340, ROW = 96;
  const len = i => E(i) - L(i);
  const at = (i, f) => L(i) + len(i) * f;
  const corner = (i, j, k, size = s) => cubeCorner(X0, Y0, size, i, j, k);
  const mc = document.createElement('canvas').getContext('2d');
  const width = (txt, size) => { mc.font = FONT(size); return mc.measureText(txt).width; };

  // A line written left to right in pieces; later pieces keep their place from the start.
  function line(y, pieces, size = 60) {
    const full = pieces.map(p => p.txt).join('');
    let x = EQX - width(full, size) / 2;
    for (const p of pieces) {
      word(p.txt, x, y, size, p.a, { align: 'left', col: p.col || P.blue });
      x += width(p.txt, size);
    }
  }
  function drop(t, t0) {
    const p = seg(t, t0, t0 + .45);
    return { a: ease(seg(t, t0, t0 + .2)), dy: -230 * (1 - easeOut(p)) + 7 * spring(t, t0 + .45, 7, 20) };
  }
  function edgeLabel(txt, p, q, off, a) { word(txt, (p[0] + q[0]) / 2 + off[0], (p[1] + q[1]) / 2 + off[1], 40, a); }

  LOOK.lesson('Объём куба', t => {
    const tFill = L(1) + .4, tB = L(2), tFly = L(5) - .15, tFlyEnd = tFly + .8, tE = L(11);
    const answer = K(12, ['восемь', '8']);

    // the empty cube: edges drawn, then swept gold while "все рёбра одинаковые"
    const fill = fadeIn(t, tFill, .8) * fadeOut(t, tB - .3, .5);
    if (fill > .02) cubeStack(X0, Y0, S, 1, () => ({ a: fill * .55 }));
    const cubes = [];
    for (let j = 0; j < 3; j++) for (let k = 0; k < 3; k++) for (let i = 0; i < 3; i++) cubes.push([i, j, k]);
    const startOf = (i, j, k) => {
      if (k === 0 && j === 0) return i === 0 ? tFlyEnd : at(5, .35) + (i - 1) * .4;
      if (k === 0) return at(6, .05) + (j - 1) * .7 + i * .12;
      return at(7, .05) + (k - 1) * .8 + (i + j * 3) * .04;
    };
    cubeStack(X0, Y0, s, 3, (i, j, k) => {
      const t0 = startOf(i, j, k);
      if (t < t0) return null;
      const o = drop(t, t0);
      if (i === 0 && j === 0 && k === 0) { o.dy = 0; o.a = 1; }
      if (t > tE && (i === 2 || j === 2 || k === 2)) {
        const q = easeIn(seg(t, tE + .3 + (i + j + k) * .05, tE + 1.3 + (i + j + k) * .05));
        o.dx = 420 * q; o.dy += -260 * q; o.a *= 1 - q;
      }
      return o;
    });
    const sizeNow = t < tE + .4 ? S : lerp(S, 2 * s, ease(seg(t, tE + .4, tE + 1.4)));
    cubeEdges(X0, Y0, sizeNow, ease(seg(t, L(0) - .6, L(0) + .6)));
    const gold = seg(t, at(0, .4), E(0));
    if (gold > 0 && t < tB) cubeEdges(X0, Y0, S, gold, P.gold, 2.2);

    // edge labels: a, then 3 см, then a again, then 2 см
    const c = (i, j, k) => corner(i, j, k, sizeNow / s * s);
    const C = (i, j, k) => cubeCorner(X0, Y0, sizeNow, i, j, k);
    const labA = fadeIn(t, at(0, .7)) * fadeOut(t, tB - .3) + fadeIn(t, at(8, .3)) * fadeOut(t, tE);
    const lab3 = fadeIn(t, at(4, .4)) * fadeOut(t, L(8));
    const lab2 = fadeIn(t, at(11, .3));
    for (const [txt, a] of [['a', labA], ['3 см', lab3], ['2 см', lab2]]) {
      if (a < .02) continue;
      edgeLabel(txt, C(0, 0, 0), C(1, 0, 0), [0, 44], a);
      edgeLabel(txt, C(0, 0, 0), C(0, 0, 1), [-24 - width(txt, 40) / 2, 0], a);
      edgeLabel(txt, C(1, 0, 0), C(1, 1, 0), [20 + width(txt, 40) / 2, 18], a);
    }
    word('Объём = ?', EQX, EQ0, 54, fadeIn(t, at(1, .55)) * fadeOut(t, tB - .3));

    // the measuring cube drops in on the right, then flies into the corner of the big one
    const ux = 1300, uy = 700, us = 140;
    if (t > tB && t < tFlyEnd) {
      const o = drop(t, tB + .2), f = ease(seg(t, tFly, tFlyEnd));
      const x = lerp(ux, X0, f), y = lerp(uy, Y0, f) + o.dy * (1 - f), size = lerp(us, s, f);
      unitCube(x, y + 6 * Math.sin(f * Math.PI) * -30, size, { a: o.a, key: 'measure' });
      const la = fadeIn(t, at(2, .55)) * fadeOut(t, tFly - .3, .3);
      word('1 см', ux + us / 2, uy + 44, 40, la);
      word('1 см³', ux + us * .75, uy - us * 1.75 - 30, 54, fadeIn(t, at(3, .45)) * fadeOut(t, tFly - .3, .3), { col: P.gold });
    }

    // counting turns into a product, line by line on one centre column
    const stage1 = fadeOut(t, L(8) + .1);
    line(EQ0, [{ txt: '3', a: fadeIn(t, at(5, .7)) * stage1 }]);
    line(EQ0 + ROW, [{ txt: '3 · 3 = 9', a: fadeIn(t, at(6, .55)) * stage1 }]);
    line(EQ0 + 2 * ROW, [{ txt: '9 · 3 = 27', a: fadeIn(t, at(7, .45)) * stage1 }]);

    const stage2 = fadeOut(t, tE + .1);
    line(EQ0 + ROW, [
      { txt: 'V = a · a · a', a: fadeIn(t, at(8, .45)) * stage2 },
      { txt: ' = a³', a: fadeIn(t, at(9, .55)) * stage2, col: P.gold },
    ]);
    const r = fadeIn(t, at(10, .2)) * stage2;
    if (r > .02) { boilSeed('rule1'); inkLine([[EQX - 120, EQ0 + 1.5 * ROW + 5], [EQX + 120, EQ0 + 1.5 * ROW + 5]], 1, mixCol(P.paper, P.soft, r), 'inkfine', 0); }
    line(EQ0 + 2 * ROW + 10, [
      { txt: 'V = 3³ = ', a: r },
      { txt: '27 см³', a: fadeIn(t, at(10, .6)) * stage2, col: P.gold },
    ]);

    // the check: what's left is a 2 cm cube
    line(EQ0, [{ txt: 'V = a³', a: fadeIn(t, tE + .3) }], 44);
    line(EQ0 + ROW, [{ txt: 'a = 2 см', a: fadeIn(t, at(11, .4)) }]);
    const qa = fadeIn(t, at(11, .8), .3) * fadeOut(t, answer - .2, .3);
    word('?', EQX, EQ0 + 2 * ROW + 20, 96, qa, { col: P.gold, pop: seg(t, at(11, .8), at(11, .8) + .3) });
    line(EQ0 + 2 * ROW + 20, [
      { txt: '2 · 2 · 2 = ', a: fadeIn(t, L(12) + .2) },
      { txt: '8 см³', a: fadeIn(t, answer, .35), col: P.gold },
    ]);
  });
})();
