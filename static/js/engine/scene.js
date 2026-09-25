/* صحنه‌ی سه‌بعدی هیرو — Three.js، پارالاکس ماوس + اسکرول
   canvas تزئینی است (aria-hidden)؛ reduced-motion یا خطا = بدون صحنه */
import { RM } from "../utils.js";

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
  canvas.style.cssText = "position:absolute;inset:0;width:100%;height:100%;pointer-events:none;z-index:0;";
  host.style.position = host.style.position || "relative";
  host.prepend(canvas);

  /* شبکه‌ی نقاط + وایرفریم‌های شناور با رنگ لایم برند */
  const lime = new THREE.Color(0xc8ff3d);
  const group = new THREE.Group();
  scene.add(group);

  const COUNT = 220;
  const geo = new THREE.BufferGeometry();
  const pos = new Float32Array(COUNT * 3);
  const seed = new Float32Array(COUNT);
  for (let i = 0; i < COUNT; i++) {
    pos[i * 3] = (Math.random() - 0.5) * 16;
    pos[i * 3 + 1] = (Math.random() - 0.5) * 9;
    pos[i * 3 + 2] = (Math.random() - 0.5) * 8;
    seed[i] = Math.random() * Math.PI * 2;
  }
  geo.setAttribute("position", new THREE.BufferAttribute(pos, 3));
  const points = new THREE.Points(
    geo,
    new THREE.PointsMaterial({ color: lime, size: 0.055, transparent: true, opacity: 0.75, sizeAttenuation: true })
  );
  group.add(points);

  const rings = [];
  for (let i = 0; i < 3; i++) {
    const r = 2.6 + i * 1.7;
    const ring = new THREE.Mesh(
      new THREE.TorusGeometry(r, 0.012, 8, 90),
      new THREE.MeshBasicMaterial({ color: lime, transparent: true, opacity: 0.14 - i * 0.03 })
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
