/* صحنه‌ی هیرو — سیاره‌ی دیجیتال: کره‌ی وایرفریم لایم با هاله‌ی نرم،
   حلقه‌های مداری ظریف و میدان ستاره‌ای روی پس‌زمینه‌ی اینک.
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
  canvas.style.cssText = "position:absolute;inset:0;width:100%;height:100%;pointer-events:none;z-index:0;";
  host.style.position = host.style.position || "relative";
  host.prepend(canvas);

  /* پالت برند — لایم روی اینک: کنتراست بالا و حس لوکس */
  const lime = new THREE.Color(0xc8ff3d);
  const limeDeep = new THREE.Color(0xa3d130);

  const planet = new THREE.Group();
  scene.add(planet);

  /* هاله‌ی نرم دور سیاره — BackSide برای درخشش لبه‌ها */
  const haloMat = new THREE.MeshBasicMaterial({
    color: lime, transparent: true, opacity: 0, side: THREE.BackSide,
  });
  const halo = new THREE.Mesh(new THREE.IcosahedronGeometry(2.6, 2), haloMat);
  planet.add(halo);

  /* کره‌ی اصلی — وایرفریم لایم، ساختار هندسی سیاره */
  const wireMat = new THREE.MeshBasicMaterial({
    color: lime, wireframe: true, transparent: true, opacity: 0,
  });
  const wire = new THREE.Mesh(new THREE.IcosahedronGeometry(2.1, 3), wireMat);
  planet.add(wire);

  /* نقاط رأس‌ها — دُرات دیجیتال روی سطح کره */
  const dotMat = new THREE.PointsMaterial({
    color: lime, size: 0.06, transparent: true, opacity: 0, sizeAttenuation: true,
  });
  const dots = new THREE.Points(wire.geometry, dotMat);
  planet.add(dots);

  /* حلقه‌های مداری ظریف — لایم به‌جای اینک خاکستری */
  const RING_OP = [0.42, 0.26];
  const rings = [];
  for (let i = 0; i < 2; i++) {
    const ring = new THREE.Mesh(
      new THREE.TorusGeometry(3.1 + i * 0.9, 0.008, 8, 140),
      new THREE.MeshBasicMaterial({ color: i ? limeDeep : lime, transparent: true, opacity: 0 })
    );
    ring.rotation.x = Math.PI / 2.2 + i * 0.5;
    ring.rotation.y = i * 0.7;
    rings.push(ring);
    planet.add(ring);
  }

  /* میدان ستاره‌ای تنک در پس‌زمینه */
  const STAR_N = 90;
  const starPos = new Float32Array(STAR_N * 3);
  for (let i = 0; i < STAR_N; i++) {
    starPos[i * 3] = (Math.random() - 0.5) * 20;
    starPos[i * 3 + 1] = (Math.random() - 0.5) * 12;
    starPos[i * 3 + 2] = (Math.random() - 0.5) * 10 - 2;
  }
  const starGeo = new THREE.BufferGeometry();
  starGeo.setAttribute("position", new THREE.BufferAttribute(starPos, 3));
  const starMat = new THREE.PointsMaterial({
    color: 0xf5f4f0, size: 0.03, transparent: true, opacity: 0, sizeAttenuation: true,
  });
  const stars = new THREE.Points(starGeo, starMat);
  scene.add(stars);

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

    /* ورود نرم: عناصر در ~۱.۲ ثانیه ظاهر می‌شوند */
    const intro = 1 - Math.pow(1 - Math.min(1, t / 1.2), 3);
    haloMat.opacity = 0.07 * intro;
    wireMat.opacity = 0.45 * intro;
    dotMat.opacity = 0.9 * intro;
    starMat.opacity = 0.5 * intro;
    rings.forEach((r, i) => { r.material.opacity = RING_OP[i] * intro; });

    mouse.x += (mouse.tx - mouse.x) * 0.05;
    mouse.y += (mouse.ty - mouse.y) * 0.05;

    planet.rotation.y = t * 0.08 + mouse.x * 0.2;
    planet.rotation.x = mouse.y * 0.12;
    stars.rotation.y = t * 0.012;
    planet.position.y = scrollP * 2.2;
    camera.position.z = 9 + scrollP * 2;

    rings.forEach((r, i) => {
      r.rotation.z = t * (0.05 + i * 0.03) * (i % 2 ? -1 : 1);
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
