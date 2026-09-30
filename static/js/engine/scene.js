/* صحنه‌ی سه‌بعدی هیرو — Three.js، پارالاکس ماوس + اسکرول
   canvas تزئینی است (aria-hidden)؛ reduced-motion یا خطا = بدون صحنه */
import { RM } from "../core/utils.js";

export function initHeroScene(host) {
  if (!host || RM || !window.THREE) return null;

  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true, powerPreference: "low-power" });
  } catch (e) {
    return null;
  }

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(50, 1, 0.1, 100);
  camera.position.z = 9;

  const canvas = renderer.domElement;
  canvas.setAttribute("aria-hidden", "true");
  canvas.style.cssText = "position:absolute;inset:0;width:100%;height:100%;pointer-events:none;z-index:-1;";
  host.style.position = host.style.position || "relative";
  host.prepend(canvas);

  /* پالت برند — اینک برای کنتراست روی پس‌زمینه‌ی روشن paper،
     لایم برای تاکید. صحنه تنک و ظریف است تا متن هیرو تمرکز اصلی بماند. */
  const lime = new THREE.Color(0xc8ff3d);
  const ink = new THREE.Color(0x0e0e0e);
  const group = new THREE.Group();
  scene.add(group);

  /* شبکه‌ی نقاط تنک — لایم‌دیپ روی paper کنتراست می‌دهد */
  const COUNT = 170;
  const geo = new THREE.BufferGeometry();
  const pos = new Float32Array(COUNT * 3);
  const seed = new Float32Array(COUNT);
  for (let i = 0; i < COUNT; i++) {
    pos[i * 3] = (Math.random() - 0.5) * 18;
    pos[i * 3 + 1] = (Math.random() - 0.5) * 10;
    pos[i * 3 + 2] = (Math.random() - 0.5) * 8;
    seed[i] = Math.random() * Math.PI * 2;
  }
  geo.setAttribute("position", new THREE.BufferAttribute(pos, 3));
  const pointsMat = new THREE.PointsMaterial({
    color: 0xa3d130, size: 0.06, transparent: true, opacity: 0, sizeAttenuation: true,
  });
  const points = new THREE.Points(geo, pointsMat);
  group.add(points);

  /* حلقه‌های وایرفریم اینک — دو حلقه‌ی ظریف و نازک */
  const RING_OP = [0.28, 0.18];
  const rings = [];
  for (let i = 0; i < 2; i++) {
    const r = 3.2 + i * 1.9;
    const ring = new THREE.Mesh(
      new THREE.TorusGeometry(r, 0.008, 8, 120),
      new THREE.MeshBasicMaterial({ color: ink, transparent: true, opacity: 0 })
    );
    ring.rotation.x = Math.PI / 2.4 + i * 0.35;
    ring.rotation.y = i * 0.5;
    rings.push(ring);
    group.add(ring);
  }

  /* پارالاکس ماوس */
  const mouse = { x: 0, y: 0, tx: 0, ty: 0 };
  const fine = matchMedia("(hover: hover) and (pointer: fine)").matches;
  if (fine) {
    window.addEventListener("mousemove", (e) => {
      mouse.tx = (e.clientX / window.innerWidth - 0.5) * 2;
      mouse.ty = (e.clientY / window.innerHeight - 0.5) * 2;
    }, { passive: true });
  }

  /* پیشرفت اسکرول هیرو */
  let scrollP = 0;
  if (window.ScrollTrigger) {
    ScrollTrigger.create({
      trigger: host,
      start: "top top",
      end: "bottom top",
      scrub: true,
      onUpdate: (self) => { scrollP = self.progress; },
    });
  }

  function resize() {
    const w = host.offsetWidth || window.innerWidth;
    const h = host.offsetHeight || window.innerHeight;
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
  }
  resize();
  window.addEventListener("resize", resize);

  const clock = new THREE.Clock();
  let raf = 0;
  const io = new IntersectionObserver(([entry]) => {
    if (entry.isIntersecting && !raf) tick();
    else if (!entry.isIntersecting && raf) {
      cancelAnimationFrame(raf);
      raf = 0;
    }
  }, { threshold: 0 });
  io.observe(host);

  function tick() {
    raf = requestAnimationFrame(tick);
    const t = clock.getElapsedTime();

    /* ورود نرم: صحنه در ~۱.۲ ثانیه از شفاف به حالت نهایی می‌رسد */
    const intro = 1 - Math.pow(1 - Math.min(1, t / 1.2), 3);
    pointsMat.opacity = 0.75 * intro;
    rings.forEach((r, i) => { r.material.opacity = RING_OP[i] * intro; });

    mouse.x += (mouse.tx - mouse.x) * 0.05;
    mouse.y += (mouse.ty - mouse.y) * 0.05;

    group.rotation.y = t * 0.05 + mouse.x * 0.16;
    group.rotation.x = mouse.y * 0.1;
    group.position.y = scrollP * 2.2;
    camera.position.z = 9 + scrollP * 2;

    const arr = geo.attributes.position.array;
    for (let i = 0; i < COUNT; i++) {
      arr[i * 3 + 1] += Math.sin(t * 0.6 + seed[i]) * 0.0016;
    }
    geo.attributes.position.needsUpdate = true;

    rings.forEach((r, i) => {
      r.rotation.z = t * (0.06 + i * 0.035) * (i % 2 ? -1 : 1);
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
