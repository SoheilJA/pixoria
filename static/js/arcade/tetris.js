import { Sound } from '../core/sound.js';
const Tetris = {
  key: "tetris",
  COLS: 10,
  ROWS: 20,
  CELL: 11,
  OX: 16,
  OY: 2,
  grid: null,
  cur: null,
  next: null,
  bag: [],
  score: 0,
  lines: 0,
  level: 1,
  dropAcc: 0,
  dasDir: 0,
  dasT: 0,
  dasAcc: 0,
  SH: {
    I: [[1, 1, 1, 1]],
    O: [
[1, 1],
[1, 1],
    ],
    T: [
[1, 1, 1],
[0, 1, 0],
    ],
    S: [
[0, 1, 1],
[1, 1, 0],
    ],
    Z: [
[1, 1, 0],
[0, 1, 1],
    ],
    J: [
[1, 0, 0],
[1, 1, 1],
    ],
    L: [
[0, 0, 1],
[1, 1, 1],
    ],
  },
  reset(full) {
    this.grid = Array.from({ length: this.ROWS }, () =>
Array(this.COLS).fill(0),
    );
    this.bag = [];
    this.next = this.pull();
    this.cur = this.pull();
    if (full) {
this.score = 0;
this.lines = 0;
this.level = 1;
    }
    this.dropAcc = 0;
    this.dasDir = 0;
    this.dasT = 0;
    this.dasAcc = 0;
  },
  pull() {
    if (!this.bag.length) {
this.bag = Object.keys(this.SH);
shuffle(this.bag);
    }
    const k = this.bag.pop();
    return { k, m: this.SH[k].map((r) => r.slice()), x: 3, y: 0 };
  },
  collide(m, x, y) {
    for (let r = 0; r < m.length; r++)
for (let c = 0; c < m[r].length; c++) {
  if (!m[r][c]) continue;
  const gx = x + c,
    gy = y + r;
  if (gx < 0 || gx >= this.COLS || gy >= this.ROWS) return true;
  if (gy >= 0 && this.grid[gy][gx]) return true;
}
    return false;
  },
  rotate() {
    const m = this.cur.m;
    const n = m[0].length,
rows = m.length;
    const rm = Array.from({ length: n }, () => Array(rows).fill(0));
    for (let r = 0; r < rows; r++)
for (let c = 0; c < n; c++) rm[c][rows - 1 - r] = m[r][c];
    for (const off of [0, -1, 1, -2, 2]) {
if (!this.collide(rm, this.cur.x + off, this.cur.y)) {
  this.cur.m = rm;
  this.cur.x += off;
  Sound.blip();
  return;
}
    }
  },
  move(d) {
    if (!this.collide(this.cur.m, this.cur.x + d, this.cur.y)) {
this.cur.x += d;
Sound.key();
    }
  },
  drop() {
    if (!this.collide(this.cur.m, this.cur.x, this.cur.y + 1)) {
this.cur.y++;
return true;
    }
    this.lock();
    return false;
  },
  hardDrop() {
    let n = 0;
    while (!this.collide(this.cur.m, this.cur.x, this.cur.y + 1)) {
this.cur.y++;
n++;
    }
    this.score += n * 2;
    this.lock();
  },
  lock() {
    const { m, x, y, k } = this.cur;
    for (let r = 0; r < m.length; r++)
for (let c = 0; c < m[r].length; c++) {
  if (!m[r][c]) continue;
  const gy = y + r;
  if (gy < 0) {
    Arcade.gameEnd({ win: false });
    return;
  }
  this.grid[gy][x + c] = this.shadeOf(k);
}
    /* پاک‌کردن خط‌ها */
    let cleared = 0;
    for (let r = this.ROWS - 1; r >= 0; r--) {
if (this.grid[r].every((v) => v)) {
  this.grid.splice(r, 1);
  this.grid.unshift(Array(this.COLS).fill(0));
  cleared++;
  r++;
}
    }
    if (cleared) {
this.lines += cleared;
this.score += [0, 100, 300, 500, 800][cleared] * this.level;
this.level = 1 + Math.floor(this.lines / 8);
if (cleared === 4) Sound.jingle();
else Sound.ok();
    }
    this.cur = this.next;
    this.next = this.pull();
    this.dropAcc = 0;
    if (this.collide(this.cur.m, this.cur.x, this.cur.y)) {
Arcade.gameEnd({ win: false });
    }
  },
  shadeOf(k) {
    return { I: 1, O: 2, T: 3, S: 2, Z: 1, J: 3, L: 2 }[k] || 1;
  },
  press(b) {
    if (b === "l" || b === "r") {
const d = b === "l" ? -1 : 1;
this.move(d);
this.dasDir = d;
this.dasT = 0;
this.dasAcc = 0;
    } else if (b === "u" || b === "A") this.rotate();
    else if (b === "FIRE" || b === "B") this.hardDrop();
  },
  update(dt) {
    /* تکرار خودکار چپ/راست (DAS) */
    if (this.dasDir) {
const held = this.dasDir < 0 ? Arcade.held.l : Arcade.held.r;
if (!held) this.dasDir = 0;
else {
  this.dasT += dt;
  if (this.dasT > 0.17) {
    this.dasAcc += dt;
    while (this.dasAcc > 0.05) {
this.dasAcc -= 0.05;
this.move(this.dasDir);
    }
  }
}
    }
    const soft = Arcade.held.d;
    const interval = soft
? 0.045
: Math.max(0.08, 0.75 - (this.level - 1) * 0.07);
    this.dropAcc += dt;
    while (this.dropAcc >= interval) {
this.dropAcc -= interval;
this.drop();
if (soft) this.score += 1;
if (Arcade.state !== "play") return;
    }
  },
  drawCell(ctx, x, y, shade, s) {
    x = Math.round(x);
    y = Math.round(y);
    const b = Math.max(1, Math.round(s / 5));
    ctx.fillStyle = LCDSH[shade] || LCD.ink;
    ctx.fillRect(x, y, s, s);
    ctx.fillStyle = "rgba(255,255,255,.28)";
    ctx.fillRect(x, y, s, b);
    ctx.fillRect(x, y, b, s);
    ctx.fillStyle = "rgba(0,0,0,.28)";
    ctx.fillRect(x, y + s - b, s, b);
    ctx.fillRect(x + s - b, y, b, s);
  },
  draw(ctx, t) {
    ctx.fillStyle = LCD.bg;
    ctx.fillRect(0, 0, 320, 224);
    const { OX, OY, CELL, COLS, ROWS } = this;
    /* قاب میدان */
    ctx.fillStyle = LCD.mid;
    ctx.fillRect(OX - 3, OY - 3, COLS * CELL + 6, ROWS * CELL + 6);
    ctx.fillStyle = LCD.bg;
    ctx.fillRect(OX, OY, COLS * CELL, ROWS * CELL);
    /* نقاط شبکه */
    ctx.fillStyle = LCD.dim;
    for (let r = 1; r < ROWS; r++)
for (let c = 1; c < COLS; c++)
  ctx.fillRect(OX + c * CELL - 1, OY + r * CELL - 1, 1, 1);
    /* بلوک‌های ثابت */
    for (let r = 0; r < ROWS; r++)
for (let c = 0; c < COLS; c++)
  if (this.grid[r][c])
    this.drawCell(
ctx,
OX + c * CELL,
OY + r * CELL,
this.grid[r][c],
CELL,
    );
    /* قطعه‌ی فعلی */
    const { m, x, y } = this.cur;
    for (let r = 0; r < m.length; r++)
for (let c = 0; c < m[r].length; c++)
  if (m[r][c] && y + r >= 0)
    this.drawCell(
ctx,
OX + (x + c) * CELL,
OY + (y + r) * CELL,
this.shadeOf(this.cur.k),
CELL,
    );
    /* سایه‌ی فرود */
    let gy = y;
    while (!this.collide(m, x, gy + 1)) gy++;
    if (gy > y) {
ctx.globalAlpha = 0.22;
for (let r = 0; r < m.length; r++)
  for (let c = 0; c < m[r].length; c++)
    if (m[r][c] && gy + r >= 0)
this.drawCell(
  ctx,
  OX + (x + c) * CELL,
  OY + (gy + r) * CELL,
  this.shadeOf(this.cur.k),
  CELL,
);
ctx.globalAlpha = 1;
    }
    /* پنل اطلاعات */
    const px = OX + COLS * CELL + 18;
    ctx.fillStyle = LCD.ink;
    ctx.font = '8px "Press Start 2P",monospace';
    ctx.textAlign = "left";
    ctx.fillText("NEXT", px, 12);
    ctx.fillStyle = LCD.mid;
    ctx.fillRect(px - 4, 18, 48, 34);
    ctx.fillStyle = LCD.bg;
    ctx.fillRect(px - 3, 19, 46, 32);
    const nm = this.next.m;
    const nw = nm[0].length * 7,
nh = nm.length * 7;
    for (let r = 0; r < nm.length; r++)
for (let c = 0; c < nm[r].length; c++)
  if (nm[r][c])
    this.drawCell(
ctx,
px - 3 + (48 - nw) / 2 + c * 7,
19 + (34 - nh) / 2 + r * 7,
this.shadeOf(this.next.k),
7,
    );
    ctx.fillStyle = LCD.ink;
    ctx.font = '8px "Press Start 2P",monospace';
    ctx.fillText("SCORE", px, 76);
    ctx.font = '18px "Jersey 10",monospace';
    ctx.fillText(String(this.score), px, 94);
    ctx.font = '8px "Press Start 2P",monospace';
    ctx.fillText("LINES", px, 118);
    ctx.font = '18px "Jersey 10",monospace';
    ctx.fillText(String(this.lines), px, 136);
    ctx.font = '8px "Press Start 2P",monospace';
    ctx.fillText("LEVEL", px, 160);
    ctx.font = '18px "Jersey 10",monospace';
    ctx.fillText(String(this.level), px, 178);
    ctx.font = '8px "Press Start 2P",monospace';
    ctx.fillStyle = LCD.mid;
    ctx.fillText("[BRAND]", px, 214);
  },
};

export default Tetris;
