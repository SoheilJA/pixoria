import { Sound } from '../core/sound.js';
import { drawMat } from '../core/sprites.js';
const Tank = {
  key: "tank",
  COLS: 20,
  ROWS: 13,
  map: null,
  player: null,
  enemies: [],
  bullets: [],
  parts: [],
  score: 0,
  lives: 3,
  wave: 0,
  toSpawn: 0,
  spawnT: 0,
  spawnCount: 0,
  freeze: 0,

  reset(full) {
    this.map = this.buildMap();
    this.player = { x: 9.5, y: 11.5, dir: "u", cool: 0, inv: 0 };
    this.enemies = [];
    this.bullets = [];
    this.parts = [];
    this.spawnCount = 0;
    this.freeze = 0;
    if (full) {
this.score = 0;
this.lives = 3;
    }
    this.startWave();
  },
  buildMap() {
    const R = this.ROWS,
C = this.COLS;
    const m = Array.from({ length: R }, () => Array(C).fill(0));
    const brick = (c, r) => {
if (r >= 0 && r < R && c >= 0 && c < C) m[r][c] = 1;
    };
    const steel = (c, r) => {
if (r >= 0 && r < R && c >= 0 && c < C) m[r][c] = 2;
    };
    /* قلعه‌ی مرکزی فولادی */
    steel(9, 5);
    steel(10, 5);
    steel(9, 6);
    steel(10, 6);
    /* خوشه‌های آجری */
    for (let k = 0; k < 4; k++) {
const bx = 2 + k * 5,
  by = 3 + (k % 2) * 3;
for (let i = 0; i < 3; i++) {
  brick(bx + i, by);
  brick(bx + i, by + 1);
}
    }
    /* دیوارهای کناری */
    for (let r = 4; r < 9; r += 2) {
brick(0, r);
brick(19, r);
brick(1, r);
brick(18, r);
    }
    /* سنگر پایین */
    brick(7, 10);
    brick(8, 10);
    brick(11, 10);
    brick(12, 10);
    brick(7, 9);
    brick(12, 9);
    /* پاشش متقارن تصادفی */
    for (let i = 0; i < 8; i++) {
const c = 1 + Math.floor(Math.random() * 9),
  r = 2 + Math.floor(Math.random() * 8);
brick(c, r);
brick(19 - c, r);
    }
    /* بازکردن ناحیه‌های ظهور */
    const clear = (c, r) => {
for (let dy = -1; dy <= 1; dy++)
  for (let dx = -1; dx <= 1; dx++) {
    const cc = c + dx,
rr = r + dy;
    if (rr >= 0 && rr < R && cc >= 0 && cc < C) m[rr][cc] = 0;
  }
    };
    clear(0, 0);
    clear(9, 0);
    clear(19, 0);
    clear(9, 11);
    return m;
  },
  startWave() {
    this.wave++;
    this.toSpawn = Math.min(3 + this.wave, 7);
    this.spawnT = 0.6;
  },
  solid(c, r) {
    if (r < 0 || r >= this.ROWS || c < 0 || c >= this.COLS) return true;
    return this.map[r][c] > 0;
  },
  canBe(x, y) {
    const cs = [Math.floor(x - 0.4), Math.floor(x + 0.4)];
    const rs = [Math.floor(y - 0.4), Math.floor(y + 0.4)];
    for (const c of cs)
for (const r of rs) if (this.solid(c, r)) return false;
    return true;
  },
  tryMove(o, dx, dy) {
    if (this.canBe(o.x + dx, o.y + dy)) {
o.x += dx;
o.y += dy;
return true;
    }
    if (dx && this.canBe(o.x + dx, o.y)) {
o.x += dx;
return true;
    }
    if (dy && this.canBe(o.x, o.y + dy)) {
o.y += dy;
return true;
    }
    return false;
  },
  pickDir(e) {
    let opts;
    if (Math.random() < 0.65) {
const dx = this.player.x - e.x,
  dy = this.player.y - e.y;
opts =
  Math.abs(dx) > Math.abs(dy)
    ? dx > 0
? ["r", "d", "u", "l"]
: ["l", "d", "u", "r"]
    : dy > 0
? ["d", "r", "l", "u"]
: ["u", "r", "l", "d"];
    } else {
opts = ["u", "d", "l", "r"];
shuffle(opts);
    }
    const D = { u: [0, -1], d: [0, 1], l: [-1, 0], r: [1, 0] };
    for (const d of opts) {
if (this.canBe(e.x + D[d][0] * 0.6, e.y + D[d][1] * 0.6)) {
  e.dir = d;
  return;
}
    }
  },
  spawnBullet(o) {
    const D = { u: [0, -1], d: [0, 1], l: [-1, 0], r: [1, 0] }[o.dir];
    this.bullets.push({
x: o.x + D[0] * 0.55,
y: o.y + D[1] * 0.55,
dx: D[0] * 8.5,
dy: D[1] * 8.5,
from: o === this.player ? "p" : "e",
    });
  },
  shoot() {
    const p = this.player;
    if (p.cool > 0) return;
    if (this.bullets.filter((b) => b.from === "p").length >= 2) return;
    this.spawnBullet(p);
    p.cool = 0.3;
    Sound.shoot();
  },
  hitPlayer() {
    this.lives--;
    Sound.boom();
    this.burst(this.player.x, this.player.y, 0);
    this.player.x = 9.5;
    this.player.y = 11.5;
    this.player.dir = "u";
    this.player.inv = 1.8;
    if (this.lives <= 0) {
Arcade.gameEnd({ win: false });
    } else this.freeze = 0.6;
  },
  burst(x, y, ci) {
    for (let i = 0; i < 7; i++)
this.parts.push({
  x,
  y,
  vx: (Math.random() - 0.5) * 5,
  vy: (Math.random() - 0.5) * 5,
  life: 0.5 + Math.random() * 0.3,
  ci: (ci + (Math.random() < 0.5 ? 1 : 0)) % 4,
});
  },
  press(b) {
    if (b === "A" || b === "FIRE" || b === "B") {
this.shoot();
return;
    }
    if ("udlr".includes(b)) {
const D = { u: [0, -1], d: [0, 1], l: [-1, 0], r: [1, 0] }[b];
this.player.dir = b;
this.tryMove(this.player, D[0] * 0.34, D[1] * 0.34);
    }
  },
  update(dt) {
    if (this.freeze > 0) {
this.freeze -= dt;
return;
    }
    const p = this.player;
    p.cool = Math.max(0, p.cool - dt);
    p.inv = Math.max(0, p.inv - dt);
    /* حرکت بازیکن */
    const sp = 3.8;
    const MV = { u: [0, -1], d: [0, 1], l: [-1, 0], r: [1, 0] };
    for (const d of ["u", "d", "l", "r"]) {
if (Arcade.held[d]) {
  p.dir = d;
  this.tryMove(p, MV[d][0] * sp * dt, MV[d][1] * sp * dt);
  break;
}
    }
    /* برخورد بدنه‌ی دشمن */
    if (p.inv <= 0) {
for (const e of this.enemies) {
  if (Math.abs(e.x - p.x) < 0.75 && Math.abs(e.y - p.y) < 0.75) {
    this.hitPlayer();
    return;
  }
}
    }
    /* دشمن‌ها */
    const esp = Math.min(3.4, 1.9 + this.wave * 0.14);
    for (const e of this.enemies) {
const D = MV[e.dir];
const moved = this.tryMove(e, D[0] * esp * dt, D[1] * esp * dt);
if (!moved || Math.random() < dt * 0.5) this.pickDir(e);
e.fireT -= dt;
if (e.fireT <= 0) {
  e.fireT = 1.3 + Math.random() * 1.9;
  const aligned =
    Math.abs(e.x - p.x) < 0.6 || Math.abs(e.y - p.y) < 0.6;
  if (
    (aligned || Math.random() < 0.4) &&
    this.bullets.filter((b) => b.from === "e").length < 6
  )
    this.spawnBullet(e);
}
    }
    /* ظهور موج */
    if (this.toSpawn > 0) {
this.spawnT -= dt;
if (this.spawnT <= 0 && this.enemies.length < 3) {
  this.spawnT = 1.5;
  this.toSpawn--;
  const spots = [
    [0.5, 0.5],
    [this.COLS - 0.5, 0.5],
    [9.5, 0.5],
  ];
  const s = spots[this.spawnCount++ % 3];
  this.enemies.push({
    x: s[0],
    y: s[1],
    dir: "d",
    fireT: 0.8 + Math.random(),
  });
}
    } else if (this.enemies.length === 0) {
this.score += 100;
Sound.jingle();
this.freeze = 0.8;
this.startWave();
return;
    }
    /* گلوله‌ها */
    for (const b of this.bullets) {
b.x += b.dx * dt;
b.y += b.dy * dt;
if (
  b.x < -0.2 ||
  b.x > this.COLS + 0.2 ||
  b.y < -0.2 ||
  b.y > this.ROWS + 0.2
) {
  b.dead = true;
  continue;
}
const c = Math.floor(b.x),
  r = Math.floor(b.y);
if (this.solid(c, r)) {
  b.dead = true;
  if (this.map[r][c] === 1) {
    this.map[r][c] = 0;
    this.burst(b.x, b.y, 1);
    Sound.hit();
  }
  continue;
}
if (b.from === "p") {
  for (const e of this.enemies) {
    if (Math.abs(e.x - b.x) < 0.55 && Math.abs(e.y - b.y) < 0.55) {
b.dead = true;
e.dead = true;
this.score += 50;
this.burst(e.x, e.y, 2);
Sound.boom();
break;
    }
  }
} else if (
  p.inv <= 0 &&
  Math.abs(p.x - b.x) < 0.55 &&
  Math.abs(p.y - b.y) < 0.55
) {
  b.dead = true;
  this.hitPlayer();
  return;
}
    }
    this.bullets = this.bullets.filter((b) => !b.dead);
    this.enemies = this.enemies.filter((e) => !e.dead);
    /* ذرات انفجار */
    for (const q of this.parts) {
q.x += q.vx * dt;
q.y += q.vy * dt;
q.life -= dt * 1.7;
    }
    this.parts = this.parts.filter((q) => q.life > 0);
  },
  drawTank(ctx, tx, ty, dir, body, tread, frame) {
    const x = Math.round(tx),
y = Math.round(ty);
    /* زنجیرها */
    ctx.fillStyle = tread;
    ctx.fillRect(x, y + 1, 4, 14);
    ctx.fillRect(x + 12, y + 1, 4, 14);
    ctx.fillStyle = LCD.bg;
    const off = frame ? 3 : 0;
    for (let i = 0; i < 14; i += 4) {
ctx.fillRect(x, y + 1 + ((i + off) % 14), 4, 1);
ctx.fillRect(x + 12, y + 1 + ((i + off) % 14), 4, 1);
    }
    /* بدنه */
    ctx.fillStyle = body;
    ctx.fillRect(x + 4, y + 2, 8, 12);
    ctx.fillStyle = LCD.bg;
    ctx.fillRect(x + 6, y + 4, 4, 3);
    /* لوله */
    ctx.fillStyle = body;
    if (dir === "u") ctx.fillRect(x + 6, y - 3, 4, 8);
    else if (dir === "d") ctx.fillRect(x + 6, y + 11, 4, 8);
    else if (dir === "l") ctx.fillRect(x - 3, y + 6, 8, 4);
    else ctx.fillRect(x + 11, y + 6, 8, 4);
  },
  draw(ctx, t) {
    ctx.fillStyle = LCD.bg;
    ctx.fillRect(0, 0, 320, 224);
    /* HUD */
    ctx.fillStyle = LCD.ink;
    ctx.font = '8px "Press Start 2P",monospace';
    ctx.textAlign = "left";
    ctx.fillText("SCORE " + String(this.score).padStart(4, "0"), 8, 11);
    ctx.fillText("WAVE " + String(this.wave).padStart(2, "0"), 112, 11);
    ctx.textAlign = "right";
    ctx.fillText("LEFT " + (this.enemies.length + this.toSpawn), 238, 11);
    for (let i = 0; i < this.lives; i++)
drawMat(ctx, HEART, HEART_P, 250 + i * 15, 3, 1.5);
    /* پس‌زمینه‌ی میدان */
    ctx.fillStyle = LCD.dim;
    ctx.globalAlpha = 0.18;
    ctx.fillRect(0, 16, 320, 208);
    ctx.globalAlpha = 1;
    /* کاشی‌ها */
    for (let r = 0; r < this.ROWS; r++)
for (let c = 0; c < this.COLS; c++) {
  const v = this.map[r][c];
  if (!v) continue;
  const x = c * 16,
    y = 16 + r * 16;
  if (v === 1) {
    /* آجر */
    ctx.fillStyle = LCDSH[1];
    ctx.fillRect(x, y, 16, 16);
    ctx.fillStyle = LCD.bg;
    ctx.fillRect(x, y + 7, 16, 1);
    ctx.fillRect(x + 3, y, 1, 7);
    ctx.fillRect(x + 11, y, 1, 7);
    ctx.fillRect(x + 7, y + 8, 1, 8);
    ctx.fillRect(x + 15, y + 8, 1, 8);
  } else {
    /* فولاد */
    ctx.fillStyle = LCDSH[3];
    ctx.fillRect(x, y, 16, 16);
    ctx.fillStyle = LCDSH[2];
    ctx.fillRect(x + 2, y + 2, 12, 12);
    ctx.fillStyle = LCDSH[3];
    ctx.fillRect(x + 5, y + 5, 6, 6);
  }
}
    /* ذرات */
    for (const q of this.parts) {
ctx.globalAlpha = clamp(q.life, 0, 1);
ctx.fillStyle = LCDSH[q.ci];
ctx.fillRect(
  Math.round(q.x * 16 - 2),
  Math.round(16 + q.y * 16 - 2),
  4,
  4,
);
    }
    ctx.globalAlpha = 1;
    /* گلوله‌ها */
    for (const b of this.bullets) {
if (b.from === "p") {
  ctx.fillStyle = LCD.ink;
  ctx.fillRect(
    Math.round(b.x * 16 - 2),
    Math.round(16 + b.y * 16 - 2),
    4,
    4,
  );
} else {
  ctx.fillStyle = LCDSH[2];
  ctx.fillRect(
    Math.round(b.x * 16 - 2),
    Math.round(16 + b.y * 16 - 2),
    5,
    5,
  );
}
    }
    /* تانک‌های دشمن */
    for (const e of this.enemies)
this.drawTank(
  ctx,
  e.x * 16 - 8,
  16 + e.y * 16 - 8,
  e.dir,
  LCDSH[2],
  LCDSH[3],
  Math.floor(t / 120 + e.x) % 2,
);
    /* تانک بازیکن (چشمک هنگام جانِ مجدد) */
    const p = this.player;
    if (p.inv <= 0 || Math.floor(t / 100) % 2 === 0)
this.drawTank(
  ctx,
  p.x * 16 - 8,
  16 + p.y * 16 - 8,
  p.dir,
  LCDSH[0],
  LCDSH[1],
  Math.floor(t / 120) % 2,
);
    /* بنر موج */
    if (this.freeze > 0) {
ctx.fillStyle = LCD.ink;
ctx.font = '14px "Press Start 2P",monospace';
ctx.textAlign = "center";
ctx.fillText("WAVE " + this.wave, 160, 122);
    }
  },
};
