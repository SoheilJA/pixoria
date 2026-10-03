/* PixoriaBackground — one fixed full-viewport WebGL canvas behind all content.

Renders flowing silk ribbons of light (lime + cyan/teal threads) that twist
into a glowing vortex, driven by scroll progress and per-section `data-bg-*`
keyframes. Sits in `#bg-shell` (position: fixed; inset: 0; z-index: -1) which
is `hx-preserve`d, so a single instance survives every HTMX navigation.

Public API (module singleton, see boot.js):
  PixoriaBackground.init({ preset: 'home' })   boot / re-scan sections
  .enterPreload()                              show hero state inside preloader
  .exitPreload()                               tween into the page state
  .refresh()                                   rebuild scroll keyframes
  .dispose()

Fallbacks: no WebGL, `prefers-reduced-motion` or a software/low-end renderer
→ the CSS gradient twin (.bg-fallback) stays and the canvas is never created.
Rendering pauses when the tab is hidden and the resolution scale adapts down
if the frame budget is missed.
*/
import { PRESETS, FOOTER_REST, BG_ATTRS } from "./presets.js";

const MAX_LAYERS = 12;

const VERT = /* glsl */ `
  void main() {
    gl_Position = vec4(position, 1.0);
  }
`;

const FRAG = /* glsl */ `
  precision highp float;

  uniform float uTime;
  uniform vec2  uResolution;
  uniform float uIntensity;
  uniform float uSwirl;
  uniform float uScale;
  uniform vec2  uOffset;
  uniform float uHue;
  uniform float uSpeed;
  uniform float uGlow;
  uniform float uCoreY;
  uniform float uAspect;
  uniform vec3  uColorLime;
  uniform vec3  uColorCyan;
  uniform vec3  uColorAzure;
  uniform int   uLayers;

  float hash(vec2 p) {
    p = fract(p * vec2(123.34, 456.21));
    p += dot(p, p + 45.32);
    return fract(p.x * p.y);
  }

  float noise(vec2 p) {
    vec2 i = floor(p), f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    return mix(mix(hash(i), hash(i + vec2(1.0, 0.0)), f.x),
               mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), f.x), f.y);
  }

  float fbm(vec2 p) {
    float v = 0.0, a = 0.5;
    mat2 m = mat2(1.6, 1.2, -1.2, 1.6);
    for (int i = 0; i < 5; i++) {
      v += a * noise(p);
      p = m * p;
      a *= 0.5;
    }
    return v;
  }

  /* Twist the domain around the vortex core: rotation grows toward the centre
     plus a slow spin, with a gentle inward pull so the streaks converge. */
  vec2 twist(vec2 p) {
    vec2 c = vec2(0.5, uCoreY) + uOffset;
    vec2 d = p - c;
    float r = length(d);
    float a = atan(d.y, d.x);
    float near = 1.0 - smoothstep(0.0, 0.85, r);
    a += uSwirl * near * 1.1 + uTime * 0.05 * uSwirl * near;
    r *= 1.0 - 0.16 * uSwirl * near;
    return c + r * vec2(cos(a), sin(a));
  }

  /* Layered aurora bands: each ribbon drifts on sine wobble + fbm, lit by a
     soft smoothstep tube and pulsed by its own phase. */
  float ribbons(vec2 uv) {
    float t = uTime * uSpeed;
    float v = 0.0;
    for (int i = 0; i < MAX_LAYERS; i++) {
      if (i >= uLayers) break;
      float fi = float(i);
      float base = 0.10 + 0.80 * fract(fi * 0.6180339 + 0.13);
      float wob = 0.16 * sin(uv.x * 2.1 + t * 0.35 + fi * 1.7)
                + 0.10 * sin(uv.x * 4.7 - t * 0.23 + fi * 2.9)
                + 0.22 * fbm(vec2(uv.x * 1.6 + t * 0.12, fi * 5.1));
      float y = base + wob - 0.15;
      float d = abs(uv.y - y);
      float w = 0.05 + 0.02 * sin(fi * 2.1 + t * 0.5);
      v += smoothstep(w, 0.0, d) * (0.55 + 0.45 * sin(fi * 1.3 + t * 0.6));
    }
    return v;
  }

  void main() {
    vec2 frag = gl_FragCoord.xy / uResolution.xy;
    /* Normalised, aspect-corrected UV space centred on the core. */
    vec2 uv = (frag - 0.5) * vec2(uAspect, 1.0) * (2.2 / uScale) + 0.5;
    uv = twist(uv);

    float silk = ribbons(uv);
    /* Second, domain-warped sample gives the silk its liquid depth. */
    vec2 uv2 = uv + 0.05 * vec2(fbm(uv * 3.0 + uTime * 0.05),
                                fbm(uv * 3.0 + 7.3 - uTime * 0.04)) - 0.03;
    silk = max(silk, ribbons(uv2) * 0.8);

    /* Glowing core where the ribbons converge. */
    vec2 core = vec2(0.5, uCoreY) + uOffset;
    float cd = length((frag - core) * vec2(uAspect, 1.0));
    float coreGlow = exp(-cd * cd * 3.4) * uGlow;

    /* Lime ⇄ cyan/azure mix, modulated so threads vary along the flow. */
    float m = clamp(uHue + 0.25 * fbm(uv * 2.0 + uTime * 0.03), 0.0, 1.0);
    vec3 accent = mix(uColorCyan, uColorAzure, 0.5);
    vec3 col = mix(uColorLime, accent, m);

    float bright = uIntensity;
    vec3 rgb = col * (silk * 1.4 + silk * silk * 1.9) * bright;
    rgb += uColorLime * coreGlow * 0.9 + col * coreGlow * 0.4;
    /* Faint haze so the dark never goes fully dead. */
    rgb += col * 0.02 * bright;

    gl_FragColor = vec4(rgb, 1.0);
  }
`;

const LIME = [200 / 255, 255 / 255, 61 / 255];
const CYAN = [87 / 255, 227 / 255, 245 / 255];
const AZURE = [90 / 255, 162 / 255, 255 / 255];

/* Device tiering — the CSS gradient twin covers the low end. */
function detectTier() {
  if (matchMedia("(prefers-reduced-motion: reduce)").matches) return "low";
  let gl = null;
  try {
    const c = document.createElement("canvas");
    gl = c.getContext("webgl2") || c.getContext("webgl");
  } catch (e) {
    return "low";
  }
  if (!gl) return "low";
  const dbg = gl.getExtension("WEBGL_debug_renderer_info");
  const renderer = dbg ? String(gl.getParameter(dbg.UNMASKED_RENDERER_WEBGL)) : "";
  if (/swiftshader|llvmpipe|software|microsoft basic/i.test(renderer)) return "low";
  const cores = navigator.hardwareConcurrency || 8;
  if (cores <= 4 || /Android|iPhone|iPad/i.test(navigator.userAgent)) return "medium";
  return "high";
}

const TIER_CONFIG = {
  low: { layers: 0, scale: 1 },
  medium: { layers: 6, scale: 0.65 },
  high: { layers: 9, scale: 1 },
};

class PixoriaBackground {
  constructor() {
    this.tier = "low";
    this.renderer = null;
    this.scene = null;
    this.mesh = null;
    this.uniforms = null;
    this.shell = null;
    this.canvas = null;
    this.fallback = null;
    this.clock = null;
    this.raf = 0;
    this.running = false;
    this.preloading = false;
    this.preset = PRESETS.home;
    this.presetName = "home";
    this.state = { ...this.preset.default };
    this.target = { ...this.preset.default };
    this.keyframes = [];
    this.masterST = null;
    this.resizeBound = null;
    this.visibilityBound = null;
    this.frameTimes = [];
    this.downgraded = false;
  }

  init(opts = {}) {
    const name = opts.preset && PRESETS[opts.preset] ? opts.preset : "home";
    if (this.presetName !== name) {
      this.presetName = name;
      this.preset = PRESETS[name];
      this.state = { ...this.preset.default };
      this.target = { ...this.preset.default };
    }
    if (this.tier === "low") this.tier = detectTier();
    if (this.tier === "low") return this; /* gradient fallback only */

    if (!this.renderer) this.create();
    if (this.renderer) {
      this.start();
      this.refresh();
    }
    return this;
  }

  create() {
    const shell = document.getElementById("bg-shell");
    if (!shell) return;
    this.shell = shell;
    this.fallback = shell.querySelector(".bg-fallback");

    let renderer;
    try {
      renderer = new THREE.WebGLRenderer({
        antialias: false,
        alpha: false,
        powerPreference: "high-performance",
      });
    } catch (e) {
      this.tier = "low";
      return;
    }
    if (!renderer.capabilities || !renderer.capabilities.isWebGL2) {
      /* WebGL1 would need extra GLSL care for the loop bound; fall back. */
      renderer.dispose();
      this.tier = "low";
      return;
    }

    const cfg = TIER_CONFIG[this.tier] || TIER_CONFIG.medium;
    this.layers = cfg.layers;
    this.resScale = cfg.scale;

    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.5));
    this.renderer = renderer;
    this.canvas = renderer.domElement;
    this.canvas.setAttribute("aria-hidden", "true");
    this.shell.appendChild(this.canvas);

    this.uniforms = {
      uTime: { value: 0 },
      uResolution: { value: [1, 1] },
      uIntensity: { value: this.state.intensity },
      uSwirl: { value: this.state.swirl },
      uScale: { value: this.state.scale },
      uOffset: { value: [this.state.x, this.state.y] },
      uHue: { value: this.state.hue },
      uSpeed: { value: this.state.speed },
      uGlow: { value: this.state.glow },
      uCoreY: { value: 0.5 },
      uAspect: { value: 1 },
      uColorLime: { value: LIME },
      uColorCyan: { value: CYAN },
      uColorAzure: { value: AZURE },
      uLayers: { value: this.layers },
    };

    const geo = new THREE.PlaneGeometry(2, 2);
    const mat = new THREE.ShaderMaterial({
      vertexShader: VERT,
      fragmentShader: FRAG,
      uniforms: this.uniforms,
      depthTest: false,
      depthWrite: false,
    });
    this.mesh = new THREE.Mesh(geo, mat);
    this.scene = new THREE.Scene();
    this.scene.add(this.mesh);

    this.clock = new THREE.Clock();
    this.resizeBound = () => this.resize();
    this.visibilityBound = () => this.onVisibility();
    window.addEventListener("resize", this.resizeBound, { passive: true });
    document.addEventListener("visibilitychange", this.visibilityBound);
    this.resize();

    if (this.fallback) this.fallback.hidden = true;
  }

  start() {
    if (this.running || !this.renderer) return;
    this.running = true;
    this.clock.start();
    this.tick();
  }

  stop() {
    this.running = false;
    if (this.raf) cancelAnimationFrame(this.raf);
    this.raf = 0;
  }

  onVisibility() {
    if (document.hidden) this.stop();
    else this.start();
  }

  resize() {
    if (!this.renderer) return;
    const w = Math.max(1, Math.round(window.innerWidth * this.resScale));
    const h = Math.max(1, Math.round(window.innerHeight * this.resScale));
    this.renderer.setSize(w, h, false);
    this.canvas.style.width = "100%";
    this.canvas.style.height = "100%";
    this.uniforms.uResolution.value = [w, h];
    this.uniforms.uAspect.value = w / h;
  }

  /* ── Scroll keyframes ──
     Sections tagged with data-bg-* become keyframes ordered by their position
     on the page; the pre-footer CTA and footer always resolve to FOOTER_REST.
     A single scrubbed ScrollTrigger interpolates the current state between
     the bracketing keyframes. */
  refresh() {
    if (!this.renderer || !window.ScrollTrigger) return;
    if (this.masterST) {
      this.masterST.kill();
      this.masterST = null;
    }
    this.keyframes = [];

    const doc = document.documentElement;
    const add = (el, forced) => {
      const kf = forced
        ? { ...FOOTER_REST }
        : { ...this.preset.default, ...this.readAttrs(el) };
      this.keyframes.push({ el, state: kf });
    };

    document.querySelectorAll(Object.keys(BG_ATTRS).join(",")).forEach((el) => add(el, false));
    /* The rest-state tail is shared by every page. */
    document
      .querySelectorAll("[data-bg-rest], .cta-banner, footer")
      .forEach((el) => add(el, true));

    this.masterST = window.ScrollTrigger.create({
      trigger: document.body,
      start: 0,
      end: "max",
      scrub: 0.4,
      onUpdate: (self) => this.applyScroll(self.progress),
    });
    this.applyScroll(window.ScrollTrigger.maxScroll(window) ? this.scrollFraction() : 0);
  }

  scrollFraction() {
    const max = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
    return Math.min(1, Math.max(0, window.scrollY / max));
  }

  readAttrs(el) {
    const out = {};
    for (const [attr, key] of Object.entries(BG_ATTRS)) {
      const v = el.getAttribute(attr);
      if (v != null && v !== "") {
        const n = parseFloat(v);
        if (Number.isFinite(n)) out[key] = n;
      }
    }
    return out;
  }

  applyScroll(progress) {
    if (!this.keyframes.length) {
      this.target = { ...this.preset.default };
      return;
    }
    const ranked = this.keyframes
      .map((kf) => {
        const r = kf.el.getBoundingClientRect();
        /* Fraction of the document at which the section's centre sits in the
           viewport centre; recomputed per update so layout shifts are free. */
        const docH = Math.max(1, document.documentElement.scrollHeight);
        const top = (window.scrollY + r.top + r.height / 2 - window.innerHeight / 2) / docH;
        return { kf, top: Math.max(0, top) };
      })
      .sort((a, b) => a.top - b.top);

    /* Rest state always anchors the end of the track. */
    ranked.push({
      kf: { state: { ...FOOTER_REST } },
      top: 1.001,
    });

    let a = ranked[0];
    let b = ranked[ranked.length - 1];
    for (let i = 0; i < ranked.length - 1; i++) {
      if (progress >= ranked[i].top && progress <= ranked[i + 1].top) {
        a = ranked[i];
        b = ranked[i + 1];
        break;
      }
    }
    if (progress < ranked[0].top) b = a;
    const span = Math.max(0.0001, b.top - a.top);
    const t = this.smooth((progress - a.top) / span);
    this.target = this.lerpState(a.kf.state, b.kf.state, t);
  }

  smooth(t) {
    t = Math.min(1, Math.max(0, t));
    return t * t * (3 - 2 * t);
  }

  lerpState(s1, s2, t) {
    const out = {};
    for (const k of Object.keys(s2)) {
      const v1 = s1[k] != null ? s1[k] : this.preset.default[k];
      const v2 = s2[k];
      out[k] = v1 + (v2 - v1) * t;
    }
    return out;
  }

  /* ── Preloader coupling ── */
  enterPreload() {
    if (!this.renderer) return;
    this.preloading = true;
    this.shell.classList.add("is-pre");
    this.state = { ...this.preset.hero };
    this.target = { ...this.preset.hero };
    this.push();
  }

  exitPreload() {
    if (!this.preloading) return;
    this.preloading = false;
    /* Camera pull-back + dim: tween the hero state into the page state. */
    const from = { ...this.state };
    const to = this.currentScrollState();
    const obj = { t: 0 };
    const tween = (gsap) => {
      gsap.to(obj, {
        t: 1,
        duration: 1.15,
        ease: "power2.inOut",
        onUpdate: () => {
          this.state = this.lerpState(from, to, obj.t);
          this.push();
        },
        onComplete: () => {
          this.state = { ...to };
          this.target = { ...to };
          this.shell.classList.remove("is-pre");
        },
      });
    };
    if (window.gsap) tween(window.gsap);
    else {
      this.state = { ...to };
      this.target = { ...to };
      this.push();
      this.shell.classList.remove("is-pre");
    }
  }

  currentScrollState() {
    if (window.ScrollTrigger) this.applyScroll(this.scrollFraction());
    return { ...this.preset.default, ...this.target };
  }

  /* Push the current state into the shader (called per frame by tick and
     directly during preloader transitions). */
  push() {
    if (!this.uniforms) return;
    const s = this.state;
    this.uniforms.uIntensity.value = s.intensity;
    this.uniforms.uSwirl.value = s.swirl;
    this.uniforms.uScale.value = s.scale;
    this.uniforms.uHue.value = s.hue;
    this.uniforms.uSpeed.value = s.speed;
    this.uniforms.uGlow.value = s.glow;
    this.uniforms.uOffset.value = [s.x || 0, s.y || 0];
  }

  /* ── Render loop with an adaptive resolution scale ── */
  tick = () => {
    if (!this.running) return;
    this.raf = requestAnimationFrame(this.tick);
    const dt = this.clock.getDelta();
    this.uniforms.uTime.value += dt;

    /* Ease toward the scroll target so section changes are silky, not stepped. */
    let dirty = false;
    for (const k of Object.keys(this.target)) {
      const cur = this.state[k] || 0;
      const tgt = this.target[k] || 0;
      if (Math.abs(tgt - cur) > 0.0005) {
        this.state[k] = cur + (tgt - cur) * Math.min(1, dt * 3.2);
        dirty = true;
      }
    }
    if (dirty || this.preloading) this.push();

    /* Continuous drift so the background is alive even when idle. */
    const p = this.scrollFraction();
    this.uniforms.uCoreY.value = 0.42 + 0.1 * Math.sin(this.uniforms.uTime.value * 0.12);
    this.uniforms.uOffset.value = [
      (this.state.x || 0) + 0.04 * Math.sin(this.uniforms.uTime.value * 0.08) + p * 0.05,
      (this.state.y || 0) + 0.03 * Math.cos(this.uniforms.uTime.value * 0.1) - p * 0.08,
    ];

    this.renderer.render(this.scene, null);
    this.measure(dt);
  };

  measure(dt) {
    if (this.downgraded || this.tier !== "high") return;
    this.frameTimes.push(dt);
    if (this.frameTimes.length < 90) return;
    const avg = this.frameTimes.reduce((a, b) => a + b, 0) / this.frameTimes.length;
    this.frameTimes = [];
    if (avg > 0.033) {
      /* Missed the 30fps budget repeatedly — drop to the medium profile. */
      this.downgraded = true;
      this.tier = "medium";
      this.resScale = 0.65;
      this.layers = 6;
      this.uniforms.uLayers.value = 6;
      this.resize();
    }
  }

  dispose() {
    this.stop();
    if (this.masterST) this.masterST.kill();
    window.removeEventListener("resize", this.resizeBound);
    document.removeEventListener("visibilitychange", this.visibilityBound);
    if (this.mesh) {
      this.mesh.geometry.dispose();
      this.mesh.material.dispose();
    }
    if (this.renderer) this.renderer.dispose();
    if (this.canvas) this.canvas.remove();
    if (this.fallback) this.fallback.hidden = false;
    this.renderer = null;
    this.mesh = null;
    this.scene = null;
    this.uniforms = null;
    this.tier = "low";
  }
}

export { PixoriaBackground };
