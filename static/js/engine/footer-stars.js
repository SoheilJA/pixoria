/* صحنه‌ی فوتر — میدان ستاره‌ای سبک با حس سفر مستقیم در فضا:
   دو لایه ستاره با سرعت‌های متفاوت رو به دوربین شتاب می‌گیرند و پس از
   رد شدن، در اعماق دوباره ظاهر می‌شوند. canvas تزئینی است (aria-hidden)؛
   reduced-motion یا خطا = بدون صحنه */
import { RM } from "../core/utils.js";

export function initFooterStars(host) {
  if (!host || RM || !window.THREE) return null;

  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({
      alpha: true,
      antialias: true,
      powerPreference: "low-power",
    });
  } catch (e) {
    return null;
  }

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(62, 1, 0.1, 140);
  camera.position.z = 6;

  const canvas = renderer.domElement;
  canvas.setAttribute("aria-hidden", "true");
  canvas.style.cssText =
    "position:absolute;inset:0;width:100%;height:100%;pointer-events:none;z-index:0;";
  host.style.position = host.style.position || "relative";
  host.prepend(canvas);

  /* پالت برند — سفید کاغذی با گلوله‌هایی از لایم */
  const paper = new THREE.Color(0xf5f4f0);
  const lime = new THREE.Color(0xc8ff3d);

  /* دو لایه: دور (ریز و کند) + نزدیک (درشت و تند) — عمق میدان فضایی */
  const LAYERS = [
    { n: 130, spread: 20, depth: 34, speed: 3.4, size: 0.05, opacity: 0.3, limeChance: 0 },
    { n: 46, spread: 12, depth: 30, speed: 7.8, size: 0.11, opacity: 0.85, limeChance: 0.3 },
  ];

  const layers = LAYERS.map((L) => {
    const pos = new Float32Array(L.n * 3);
    const col = new Float32Array(L.n * 3);
    for (let i = 0; i < L.n; i++) {
      pos[i * 3] = (Math.random() - 0.5) * L.spread * 2;
      pos[i * 3 + 1] = (Math.random() - 0.5) * L.spread * 2;
      pos[i * 3 + 2] = Math.random() * L.depth + 0.6;
      const c = Math.random() < L.limeChance ? lime : paper;
      col[i * 3] = c.r;
      col[i * 3 + 1] = c.g;
      col[i * 3 + 2] = c.b;
    }
    const geo = new THREE.BufferGeometry();
    geo.setAttribute("position", new THREE.BufferAttribute(pos, 3));
    geo.setAttribute("color", new THREE.BufferAttribute(col, 3));
    const mat = new THREE.PointsMaterial({
      size: L.size,
      sizeAttenuation: true,
      transparent: true,
      opacity: 0,
      vertexColors: true,
      depthWrite: false,
    });
    const pts = new THREE.Points(geo, mat);
    scene.add(pts);
    return { L, pos, geo, mat };
  });

  /* پارالاکس ملایم ماوس — حس کج‌شدن سفینه */
  const mouse = { x: 0, y: 0, tx: 0, ty: 0 };
  const fine = matchMedia("(hover: hover) and (pointer: fine)").matches;
  if (fine) {
    window.addEventListener(
      "mousemove",
      (e) => {
        mouse.tx = (e.clientX / window.innerWidth - 0.5) * 2;
        mouse.ty = (e.clientY / window.innerHeight - 0.5) * 2;
      },
      { passive: true },
    );
  }

  function resize() {
    const w = host.offsetWidth || window.innerWidth;
    const h = host.offsetHeight || 240;
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
  }
  resize();
  window.addEventListener("resize", resize);

  const clock = new THREE.Clock();
  let raf = 0;
  const io = new IntersectionObserver(
    ([entry]) => {
      if (entry.isIntersecting && !raf) tick();
      else if (!entry.isIntersecting && raf) {
        cancelAnimationFrame(raf);
        raf = 0;
      }
    },
    { threshold: 0 },
  );
  io.observe(host);

  function tick() {
    raf = requestAnimationFrame(tick);
    const dt = Math.min(clock.getDelta(), 0.05);
    const t = clock.elapsedTime;

    /* ورود نرم: ستاره‌ها در ~۱.۴ ثانیه ظاهر می‌شوند */
    const intro = 1 - Math.pow(1 - Math.min(1, t / 1.4), 3);

    mouse.x += (mouse.tx - mouse.x) * 0.04;
    mouse.y += (mouse.ty - mouse.y) * 0.04;
    camera.position.x = mouse.x * 1.1;
    camera.position.y = mouse.y * 0.7;
    camera.lookAt(0, 0, 0);

    layers.forEach(({ L, pos, geo, mat }) => {
      mat.opacity = L.opacity * intro;
      for (let i = 0; i < L.n; i++) {
        let z = pos[i * 3 + 2] - L.speed * dt;
        if (z < 0.35) {
          /* از دوربین رد شد — در اعماق دوباره متولد می‌شود */
          z = L.depth;
          pos[i * 3] = (Math.random() - 0.5) * L.spread * 2;
          pos[i * 3 + 1] = (Math.random() - 0.5) * L.spread * 2;
        }
        pos[i * 3 + 2] = z;
      }
      geo.attributes.position.needsUpdate = true;
    });

    renderer.render(scene, camera);
  }

  return {
    destroy() {
      cancelAnimationFrame(raf);
      io.disconnect();
      window.removeEventListener("resize", resize);
      renderer.dispose();
      canvas.remove();
    },
  };
}
