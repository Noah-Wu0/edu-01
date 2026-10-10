// Unit cubes drawn flat, textbook style: front, top and right faces, depth going up and to the right.
// (x, y) is the bottom-front-left corner on screen; s is one edge in pixels. Fading mixes toward paper,
// because p5.brush strokes have no alpha.
const CUBE_COL = { front: '#C9D3EC', top: '#E6EAF5', side: '#9FB0DA', ink: '#1C3D8F', paper: '#F3EBDC', gold: '#C8922A' };

function cubeCorner(x, y, s, i, j, k) { return [x + (i + j * .5) * s, y - (k + j * .5) * s]; }

function unitCube(x, y, s, o = {}) {
  const a = o.a ?? 1, fade = c => mixCol(CUBE_COL.paper, c, a), sw = o.sw ?? 1.2;
  const c = (i, j, k) => cubeCorner(x, y, s, i, j, k);
  const tone = o.tone || CUBE_COL;
  boilSeed(o.key || `cube${x | 0},${y | 0}`);
  paint([c(0, 0, 0), c(1, 0, 0), c(1, 0, 1), c(0, 0, 1)], { wash: fade(tone.front), ink: fade(CUBE_COL.ink), sw });
  paint([c(0, 0, 1), c(1, 0, 1), c(1, 1, 1), c(0, 1, 1)], { wash: fade(tone.top), ink: fade(CUBE_COL.ink), sw });
  paint([c(1, 0, 0), c(1, 1, 0), c(1, 1, 1), c(1, 0, 1)], { wash: fade(tone.side), ink: fade(CUBE_COL.ink), sw });
}

// n×n×n block of unit cubes. each(i, j, k) returns null to skip a cube, or { a, dx, dy, tone }.
// Painted back to front, bottom to top, left to right, so nearer faces cover farther ones.
function cubeStack(x, y, s, n, each = () => ({})) {
  for (let j = n - 1; j >= 0; j--)
    for (let k = 0; k < n; k++)
      for (let i = 0; i < n; i++) {
        const o = each(i, j, k);
        if (!o || (o.a ?? 1) < .02) continue;
        const [cx, cy] = cubeCorner(x, y, s, i, j, k);
        unitCube(cx + (o.dx || 0), cy + (o.dy || 0), s, { ...o, key: `stack${i}${j}${k}` });
      }
}

// The outline of an n-edge cube, as nine visible edges. k reveals edges in order, 0..1.
function cubeEdges(x, y, S, k = 1, col = CUBE_COL.ink, sw = 1.6) {
  const c = (i, j, kk) => cubeCorner(x, y, S, i, j, kk);
  const edges = [
    [c(0, 0, 0), c(1, 0, 0)], [c(1, 0, 0), c(1, 0, 1)], [c(1, 0, 1), c(0, 0, 1)], [c(0, 0, 1), c(0, 0, 0)],
    [c(0, 0, 1), c(0, 1, 1)], [c(1, 0, 1), c(1, 1, 1)], [c(0, 1, 1), c(1, 1, 1)],
    [c(1, 0, 0), c(1, 1, 0)], [c(1, 1, 0), c(1, 1, 1)],
  ];
  const shown = k * edges.length;
  edges.forEach(([p, q], e) => {
    const f = clamp(shown - e);
    if (f < .02) return;
    boilSeed(`edge${e}`);
    inkLine([p, [lerp(p[0], q[0], f), lerp(p[1], q[1], f)]], sw, col, 'ink', 0);
  });
}
