import { Sound } from '../core/sound.js';
import { drawMat, CHOM_C, CHOM_O, CHOM_P, GHOST_A, GHOST_B, HEART, HEART_P } from '../core/sprites.js';
const PACMAP = [
  "###############",
  "#....#...#....#",
  "#.##.#.#.#.##.#",
  "#.#.........#.#",
  "#.#.###.###.#.#",
  "#G....#.#....G#",
  "#.#.###.###.#.#",
  "#.#.........#.#",
  "#.##.#.#.#.##.#",
  "#....#...#....#",
  "###############",
];
const Pac = {
  key: "pac",
  T: 14,
  map: null,
  dots: null,
  total: 0,
  eaten: 0,
  player: null,
  ghosts: null,
  lives: 3,
  score: 0,
  elapsed: 0,
  freeze: 0,
  stepT: 0,
  gstep: [0, 0],
  reset(full) {
    this.map = PACMAP.map((r) => r.split(""));
    this.dots = new Set();
    this.eaten = 0;
    for (let r = 0; r < this.map.length; r++)
for (let c = 0; c < this.map[r].length; c++) {
  if (this.map[r][c] === ".") this.dots.add(c + "," + r);
  if (this.map[r][c] === "G") this.map[r][c] = " ";
}
    this.total = this.dots.size;
    this.ghosts = [
{ c: 1, r: 5, px: 0, py: 0, col: "#e05b4a", stepT: 0, int: 0.16 },
{ c: 13, r: 5, px: 0, py: 0, col: "#4f8fd0", stepT: 0, int: 0.13 },
    ];
    this.place();
    if (full) {
this.lives = 3;
this.score = 0;
    }
    this.elapsed = 0;
    this.freeze = 0;
    this.stepT = 0;
    this.gstep = [0, 0];
  },
  place() {
    const p =
this.player ||
(this.player = { c: 7, r: 9, px: 0, py: 0, want: null, dir: null });
    p.c = 7;
    p.r = 9;
    p.want = null;
    p.dir = null;
    p.px = p.c * this.T + 2;
    p.py = p.r * this.T + 2;
    for (const g of this.ghosts) {
g.px = g.c * this.T + 2;
g.py = g.r * this.T + 2;
g.dir = null;
g.stepT = 0;
    }
  },
  walkable(c, r) {
    if (r < 0 || r >= this.map.length || c < 0 || c >= this.map[r].length)
return false;
    return this.map[r][c] !== "#";
  },
  key(k, down) {
    if (!down) return;
    const m = {
ArrowLeft: "l",
ArrowRight: "r",
ArrowUp: "u",
ArrowDown: "d",
    };
    if (m[k]) this.player.want = m[k];
  },
  action() {},
  update(dt) {
    if (this.freeze > 0) {
this.freeze -= dt;
return;
    }
    this.elapsed += dt;
    const p = this.player;
    this.stepT += dt;
    while (this.stepT >= 0.115) {
this.stepT -= 0.115;
this.step(p);
    }
    this.gstep[0] += dt;
    this.gstep[1] += dt;
    while (this.gstep[0] >= this.ghosts[0].int) {
this.gstep[0] -= this.ghosts[0].int;
this.stepGhost(this.ghosts[0]);
    }
    while (this.gstep[1] >= this.ghosts[1].int) {
this.gstep[1] -= this.ghosts[1].int;
this.stepGhost(this.ghosts[1]);
    }
    const k = Math.min(1, dt * 16);
    p.px += (p.c * this.T + 2 - p.px) * k;
    p.py += (p.r * this.T + 2 - p.py) * k;
    for (const g of this.ghosts) {
g.px += (g.c * this.T + 2 - g.px) * k;
g.py += (g.r * this.T + 2 - g.py) * k;
    }
    for (const g of this.ghosts) {
if (Math.hypot(g.px - p.px, g.py - p.py) < 10) {
  this.caught();
  break;
}
    }
  },
  step(p) {
    const D = { l: [-1, 0], r: [1, 0], u: [0, -1], d: [0, 1] };
    if (p.want && this.walkable(p.c + D[p.want][0], p.r + D[p.want][1]))
p.dir = p.want;
    if (p.dir && this.walkable(p.c + D[p.dir][0], p.r + D[p.dir][1])) {
p.c += D[p.dir][0];
p.r += D[p.dir][1];
const key = p.c + "," + p.r;
if (this.dots.has(key)) {
  this.dots.delete(key);
  this.eaten++;
  this.score += 10;
  Sound.eat();
  if (this.eaten >= this.total) this.win();
}
    }
  },
  stepGhost(g) {
    const D = { l: [-1, 0], r: [1, 0], u: [0, -1], d: [0, 1] };
    const opp = { l: "r", r: "l", u: "d", d: "u" };
    const opts = Object.keys(D).filter(
(d) =>
  this.walkable(g.c + D[d][0], g.r + D[d][1]) &&
  d !== opp[g.dir || ""],
    );
    const all = Object.keys(D).filter((d) =>
this.walkable(g.c + D[d][0], g.r + D[d][1]),
    );
    let ch;
    if (!opts.length && !all.length) return;
    if (!opts.length) ch = all[0];
    else if (Math.random() < 0.7) {
let bd = 1e9;
for (const d of opts) {
  const dx = g.c + D[d][0] - this.player.c,
    dy = g.r + D[d][1] - this.player.r;
  const dist = dx * dx + dy * dy;
  if (dist < bd) {
    bd = dist;
    ch = d;
  }
}
    } else ch = opts[Math.floor(Math.random() * opts.length)];
    g.dir = ch;
    g.c += D[ch][0];
    g.r += D[ch][1];
  },
  caught() {
    this.lives--;
    Sound.err();
    this.freeze = 0.9;
    this.place();
    if (this.lives <= 0) {
Arcade.gameEnd({ win: false });
    }
  },
  win() {
    Arcade.gameEnd({ win: true, time: this.elapsed });
  },
  press(b) {
    if ("udlr".includes(b)) this.player.want = b;
  },
  draw(ctx, t) {
    const T = this.T;
    const OX = Math.floor((320 - 15 * T) / 2),
OY = 34;
    ctx.fillStyle = LCD.bg;
    ctx.fillRect(0, 0, 320, 224);
    /* HUD */
    ctx.fillStyle = LCD.ink;
    ctx.font = '8px "Press Start 2P",monospace';
    ctx.textAlign = "left";
    ctx.fillText("SCORE " + String(this.score).padStart(4, "0"), 8, 12);
    ctx.textAlign = "right";
    ctx.fillText(
"DOTS " +
  String(Math.max(0, this.total - this.eaten)).padStart(2, "0"),
312,
12,
    );
    for (let i = 0; i < this.lives; i++)
drawMat(ctx, HEART, HEART_P, 196 + i * 15, 4, 1.5);
    /* دیوارها */
    for (let r = 0; r < this.map.length; r++)
for (let c = 0; c < this.map[r].length; c++) {
  if (this.map[r][c] === "#") {
    const x = OX + c * T,
y = OY + r * T;
    ctx.fillStyle = LCD.mid;
    ctx.fillRect(x, y, T, T);
    ctx.fillStyle = LCD.dim;
    ctx.fillRect(x, y, T, 3);
    ctx.fillRect(x, y, 3, T);
    ctx.fillStyle = LCD.bg;
    ctx.fillRect(x + T - 3, y, 3, T);
    ctx.fillRect(x, y + T - 3, T, 3);
  }
}
    /* نقطه‌ها */
    ctx.fillStyle = LCD.ink;
    for (const key of this.dots) {
const [c, r] = key.split(",").map(Number);
ctx.fillRect(OX + c * T + T / 2 - 2, OY + r * T + T / 2 - 2, 4, 4);
    }
    /* بازیکن: نوش‌کروم */
    const p = this.player;
    const open = p.dir && Math.floor(t / 140) % 2 === 0 ? CHOM_O : CHOM_C;
    ctx.save();
    ctx.translate(OX + p.px + 6, OY + p.py + 6);
    if (p.dir === "l") ctx.scale(-1, 1);
    else if (p.dir === "u") ctx.rotate(-Math.PI / 2);
    else if (p.dir === "d") ctx.rotate(Math.PI / 2);
    drawMat(ctx, open, CHOM_P, -6, -6, 1);
    ctx.restore();
    /* روح‌ها */
    const gm = Math.floor(t / 210) % 2 === 0 ? GHOST_A : GHOST_B;
    for (const g of this.ghosts) {
drawMat(
  ctx,
  gm,
  { K: LCD.ink, V: g.col, W: "#ffffff" },
  OX + g.px + 1,
  OY + g.py + 1,
  1,
);
    }
    /* فلاشِ گرفته‌شدن */
    if (this.freeze > 0 && Math.floor(t / 90) % 2 === 0) {
ctx.globalAlpha = 0.12;
ctx.fillStyle = LCD.ink;
ctx.fillRect(0, 0, 320, 224);
ctx.globalAlpha = 1;
    }
  },
};
