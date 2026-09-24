/* پس‌زمینه‌ی سه‌بعدی ووکسی — بازاستفاده‌ی دقیق از landing-5 (سیارات/ستاره‌ها)
   Three.js لوکال از static/js/vendor/three.module.js */
import { $, clamp, RM, isDark, onThemeChange } from "../core/utils.js";

let scrollP = 0;
let api = null;

export async function initThreeBackground() {
  const cv = $("#bg3d");
  if (!cv) return;
  let T;
  try {
    T = await import("../vendor/three.module.js");
  } catch (e) {
    cv.style.display = "none";
    return;
  }
  let renderer;
  try {
    renderer = new T.WebGLRenderer({
      canvas: cv,
      antialias: false,
      powerPreference: "low-power",
    });
  } catch (e) {
    cv.style.display = "none";
    return;
  }
  renderer.setPixelRatio(1);
  const scene = new T.Scene();
  const cam = new T.PerspectiveCamera(62, 1, 0.1, 500);
  cam.position.set(0, 4, 34);
  scene.add(new T.AmbientLight(0xffffff, 0.55));
  const dl = new T.DirectionalLight(0xffffff, 0.95);
  dl.position.set(10, 20, 12);
  scene.add(dl);

  /* ستاره‌های ووکسی */
  const N = 220;
  const stars = new T.InstancedMesh(
    new T.BoxGeometry(0.7, 0.7, 0.7),
    new T.MeshBasicMaterial({ color: "#8fa0d8" }),
    N,
  );
  const m4 = new T.Matrix4();
  for (let i = 0; i < N; i++) {
    m4.identity();
    m4.setPosition(
      (Math.random() * 2 - 1) * 70,
      (Math.random() * 2 - 1) * 38,
      40 - Math.random() * 190,
    );
    stars.setMatrixAt(i, m4);
  }
  scene.add(stars);

  /* سیاره‌ها */
  const planetMats = [];
  const rings = [];
  const planets = [];
  for (let i = 0; i < 5; i++) {
    const g = new T.Group();
    const mat = new T.MeshLambertMaterial({
      flatShading: true,
      color: "#888888",
    });
    const body = new T.Mesh(
      new T.IcosahedronGeometry(2.4 + (i % 2) * 1.2, 1),
      mat,
    );
    g.add(body);
    const ring = new T.InstancedMesh(
      new T.BoxGeometry(0.5, 0.5, 0.5),
      new T.MeshBasicMaterial({ color: "#888888" }),
      14,
    );
    for (let j = 0; j < 14; j++) {
      const a = (j / 14) * Math.PI * 2,
        rr = 4.4;
      m4.identity();
      m4.setPosition(Math.cos(a) * rr, 0, Math.sin(a) * rr);
      ring.setMatrixAt(j, m4);
    }
    g.add(ring);
    g.position.set(
      (i % 2 ? -1 : 1) * (7 + i * 1.4),
      ((i % 3) - 1) * 5,
      16 - i * 26,
    );
    scene.add(g);
    planetMats.push(mat);
    rings.push(ring);
    planets.push(g);
  }

  const PAL = {
    dark: {
      bg: "#070a18",
      stars: "#8fa0d8",
      cols: ["#ff6b35", "#3ee6c0", "#ff4f9a", "#ffb347", "#8f7bff"],
    },
    light: {
      bg: "#dfe5f2",
      stars: "#8b96b8",
      cols: ["#e2543e", "#2a9d8f", "#d6336c", "#d9822b", "#7a6bd6"],
    },
  };
  function theme() {
    const p = isDark() ? PAL.dark : PAL.light;
    scene.background = new T.Color(p.bg);
    scene.fog = new T.Fog(new T.Color(p.bg), 34, 165);
    stars.material.color.set(p.stars);
    planetMats.forEach((m, i) => m.color.set(p.cols[i]));
    rings.forEach((r, i) => r.material.color.set(p.cols[i]));
    draw(performance.now());
  }
  function draw(t) {
    cam.position.z += (34 - scrollP * 132 - cam.position.z) * 0.05;
    cam.position.x = RM ? 0 : Math.sin(t * 0.00018) * 1.6;
    cam.lookAt(0, cam.position.y, cam.position.z - 20);
    planets.forEach((g, i) => {
      g.children[0].rotation.y += RM ? 0 : 0.004 + i * 0.0012;
      g.children[1].rotation.y += RM ? 0 : 0.006;
    });
    renderer.render(scene, cam);
  }
  function resize() {
    const w = window.innerWidth,
      h = window.innerHeight,
      S = 4;
    renderer.setSize(
      Math.max(2, Math.ceil(w / S)),
      Math.max(2, Math.ceil(h / S)),
      false,
    );
    cam.aspect = w / h;
    cam.updateProjectionMatrix();
    draw(performance.now());
  }
  window.addEventListener("resize", resize);
  onThemeChange(theme);
  theme();
  resize();
  if (!RM) {
    (function loop(t) {
      requestAnimationFrame(loop);
      if (!document.hidden) draw(t);
    })(0);
  } else {
    window.addEventListener(
      "scroll",
      () => draw(performance.now()),
      { passive: true },
    );
  }
  api = { theme };
}

export function initScrollProgress() {
  let tick = false;
  window.addEventListener(
    "scroll",
    () => {
      if (tick) return;
      tick = true;
      requestAnimationFrame(() => {
        const doc = document.documentElement;
        scrollP = clamp(
          window.scrollY / Math.max(1, doc.scrollHeight - window.innerHeight),
          0,
          1,
        );
        const alt = $("#altMeter");
        if (alt)
          alt.textContent =
            "ALT " + String(Math.round(scrollP * 999)).padStart(3, "0");
        tick = false;
      });
    },
    { passive: true },
  );
}

export default { initThreeBackground, initScrollProgress };
