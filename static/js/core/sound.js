/* صدای Web Audio — از مرجع. پیش‌فرض خاموش؛ ترجیح بین صفحه‌ها با کلید مشترک */
export const SOUND_KEY = "lr_sound";

export const Sound = {
  ctx: null,
  on: false,
  ensure() {
    if (!this.ctx) {
      const AC = window.AudioContext || window.webkitAudioContext;
      if (AC) this.ctx = new AC();
    }
    if (this.ctx && this.ctx.state === "suspended") this.ctx.resume();
  },
  tone(f, d = 0.06, v = 0.07, s = 0) {
    if (!this.on || !this.ctx) return;
    const t0 = this.ctx.currentTime;
    const o = this.ctx.createOscillator(),
      g = this.ctx.createGain();
    o.type = "square";
    o.frequency.setValueAtTime(f, t0);
    if (s) o.frequency.linearRampToValueAtTime(s, t0 + d);
    g.gain.setValueAtTime(v, t0);
    g.gain.exponentialRampToValueAtTime(0.0001, t0 + d);
    o.connect(g);
    g.connect(this.ctx.destination);
    o.start(t0);
    o.stop(t0 + d + 0.02);
  },
  key() {
    this.tone(1500 + Math.random() * 300, 0.018, 0.024);
  },
  blip() {
    this.tone(660, 0.05, 0.06);
  },
  ok() {
    this.tone(784, 0.06);
    setTimeout(() => this.tone(1175, 0.1), 55);
  },
  err() {
    this.tone(200, 0.15, 0.08, 120);
  },
  eat() {
    this.tone(520 + Math.random() * 180, 0.04, 0.05);
  },
  shoot() {
    this.tone(900, 0.07, 0.05, 240);
  },
  hit() {
    this.tone(220, 0.07, 0.08, 70);
  },
  boom() {
    this.tone(120, 0.3, 0.1, 40);
  },
  jingle() {
    [523, 659, 784, 1047].forEach((f, i) =>
      setTimeout(() => this.tone(f, 0.09, 0.07), i * 95),
    );
  },
};

document.addEventListener("pointerdown", () => Sound.ensure(), { once: true });
