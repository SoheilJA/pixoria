/**
 * Pixoria hero — Three.js starfield + crystal planet.
 *
 * Ported from the inline module of new/index.html, wrapped in the performance
 * rules recorded as D8 in AGENT_PROGRESS.md:
 *   - the renderer/scene are only built when #hero-3d is near the viewport and
 *     the page has loaded / is idle (never blocks first paint or the LCP);
 *   - devicePixelRatio is capped at 2;
 *   - the render loop is paused (not merely skipped) while the hero is
 *     off-screen or the tab is hidden, and everything is disposed on teardown;
 *   - prefers-reduced-motion renders nothing animated and shows the CSS
 *     fallback poster instead;
 *   - any failure (no WebGL, no GPU, exception) falls back to #hero-fallback.
 *
 * Loaded as an ES module from base.html; three is imported locally.
 */

import * as THREE from "./vendor/three.module.js";

const REDUCED = matchMedia("(prefers-reduced-motion: reduce)").matches;

const mount = document.getElementById("hero-3d");
const canvas = document.getElementById("hero-canvas");
const heroSection = document.getElementById("home");
const fallback = document.getElementById("hero-fallback");

let booted = false;

function showFallback() {
  fallback?.classList.add("show");
}

/* ------------------------------------------------------------- scene build */

function boot() {
  if (booted) return;
  booted = true;

  try {
    const renderer = new THREE.WebGLRenderer({
      canvas,
      antialias: true,
      alpha: true,
      powerPreference: "high-performance",
    });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.15;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, 1, 0.1, 120);
    camera.position.set(0, 0, 9);

    // Procedural lit environment (no external file)
    const pmrem = new THREE.PMREMGenerator(renderer);
    const envScene = new THREE.Scene();
    envScene.add(
      new THREE.Mesh(
        new THREE.BoxGeometry(16, 16, 16),
        new THREE.MeshBasicMaterial({ color: 0x07070b, side: THREE.BackSide }),
      ),
    );
    const panel = (hex, k, w, h, pos, rot) => {
      const mat = new THREE.MeshBasicMaterial({ side: THREE.DoubleSide });
      mat.color.setHex(hex).multiplyScalar(k);
      const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), mat);
      m.position.set(...pos);
      m.rotation.set(...rot);
      envScene.add(m);
    };
    panel(0xfff1d6, 3.2, 7, 4, [0, 6.4, 0], [-Math.PI / 2, 0, 0]); // warm key light above
    panel(0xe8c47a, 2.2, 3.5, 7, [6.4, 1, -2], [0, -Math.PI / 3, 0]); // gold bar
    panel(0x2e63ff, 0.9, 2.5, 7, [-6.2, 0, 1], [0, Math.PI / 2.6, 0]); // faint blue edge
    panel(0xd8d2c4, 0.6, 9, 5, [0, 0, -6.4], [0, 0, 0]); // cream backdrop
    scene.environment = pmrem.fromScene(envScene, 0.06).texture;

    const key = new THREE.DirectionalLight(0xffe9c4, 1.3);
    key.position.set(3, 4, 5);
    scene.add(key);
    const warm = new THREE.PointLight(0xc9a15a, 30, 22);
    warm.position.set(2.5, -2, 2.5);
    scene.add(warm);
    const royal = new THREE.PointLight(0x2e63ff, 16, 24);
    royal.position.set(-4, -1, 3);
    scene.add(royal);

    // Soft circular star texture (so the points are not square)
    const starTex = (() => {
      const c = document.createElement("canvas");
      c.width = c.height = 64;
      const g = c.getContext("2d");
      const grad = g.createRadialGradient(32, 32, 0, 32, 32, 32);
      grad.addColorStop(0, "rgba(255,255,255,1)");
      grad.addColorStop(0.25, "rgba(255,255,255,.85)");
      grad.addColorStop(0.55, "rgba(255,255,255,.22)");
      grad.addColorStop(1, "rgba(255,255,255,0)");
      g.fillStyle = grad;
      g.fillRect(0, 0, 64, 64);
      const t = new THREE.CanvasTexture(c);
      t.colorSpace = THREE.SRGBColorSpace;
      return t;
    })();

    // Multi-layer star field (space-depth effect)
    const DEPTH = 90; // travel-tunnel length
    const starLayers = [];
    const makeStarLayer = (count, size, zMin, zMax, colors) => {
      const pos = new Float32Array(count * 3);
      const col = new Float32Array(count * 3);
      const c = new THREE.Color();
      for (let i = 0; i < count; i++) {
        // Scatter over a wide cylinder around the view axis
        const a = Math.random() * Math.PI * 2;
        const r = 3 + Math.random() * 17;
        pos[i * 3] = Math.cos(a) * r;
        pos[i * 3 + 1] = Math.sin(a) * r;
        pos[i * 3 + 2] = zMin + Math.random() * (zMax - zMin);
        c.set(colors[Math.floor(Math.random() * colors.length)]);
        col[i * 3] = c.r;
        col[i * 3 + 1] = c.g;
        col[i * 3 + 2] = c.b;
      }
      const geo = new THREE.BufferGeometry();
      geo.setAttribute("position", new THREE.BufferAttribute(pos, 3));
      geo.setAttribute("color", new THREE.BufferAttribute(col, 3));
      const mat = new THREE.PointsMaterial({
        size,
        map: starTex,
        sizeAttenuation: true,
        transparent: true,
        depthWrite: false,
        blending: THREE.AdditiveBlending,
        vertexColors: true,
      });
      const pts = new THREE.Points(geo, mat);
      scene.add(pts);
      starLayers.push({ pts, zMin, zMax });
      return pts;
    };

    const WARM = [0xfff4e0, 0xe8c47a, 0xfff4e0, 0xfff4e0, 0xc9a15a];
    const COOL = [0x2e63ff, 0x6b8bff, 0x8fa8ff];
    makeStarLayer(900, 0.16, -DEPTH * 0.35, DEPTH * 0.65, WARM); // far layer — small, slow
    makeStarLayer(520, 0.27, -DEPTH * 0.2, DEPTH * 0.8, [...WARM, ...COOL]); // middle
    makeStarLayer(240, 0.42, -DEPTH * 0.1, DEPTH * 0.9, COOL.concat([0xfff4e0])); // near — big, fast

    // Central crystal planet
    const planet = new THREE.Group();
    scene.add(planet);

    const core = new THREE.Mesh(
      new THREE.SphereGeometry(1.5, 64, 48),
      new THREE.MeshPhysicalMaterial({
        color: 0xf4ecd9,
        metalness: 0.1,
        roughness: 0.12,
        transmission: 0.92,
        thickness: 2.4,
        ior: 1.42,
        attenuationColor: new THREE.Color(0xd9b26a),
        attenuationDistance: 3.2,
        clearcoat: 1,
        clearcoatRoughness: 0.1,
        envMapIntensity: 1.5,
      }),
    );
    planet.add(core);

    const goldMat = new THREE.MeshStandardMaterial({
      color: 0xc9a15a,
      metalness: 1,
      roughness: 0.25,
      envMapIntensity: 1.5,
    });
    const goldMat2 = new THREE.MeshStandardMaterial({
      color: 0xe8c47a,
      metalness: 1,
      roughness: 0.18,
      envMapIntensity: 1.6,
    });

    // Gold orbital rings (Saturn-like)
    const ring1 = new THREE.Mesh(
      new THREE.TorusGeometry(2.35, 0.055, 32, 160),
      goldMat,
    );
    ring1.rotation.set(1.15, 0.2, 0);
    const ring2 = new THREE.Mesh(
      new THREE.TorusGeometry(2.95, 0.026, 32, 180),
      goldMat2,
    );
    ring2.rotation.set(0.55, 0.75, 0.2);
    planet.add(ring1, ring2);

    // Small moons orbiting the planet
    const moons = new THREE.Group();
    planet.add(moons);
    const moonData = [];
    for (let i = 0; i < 5; i++) {
      const m = new THREE.Mesh(
        new THREE.OctahedronGeometry(0.11 + Math.random() * 0.09),
        i % 3 ? goldMat : goldMat2,
      );
      const r = 2.2 + Math.random() * 1.1;
      const tilt = (Math.random() - 0.5) * 0.9;
      moonData.push({
        mesh: m,
        radius: r,
        tilt,
        speed: 0.06 + Math.random() * 0.12,
        phase: Math.random() * Math.PI * 2,
      });
      moons.add(m);
    }

    /* ---------------- animation state ---------------- */
    const state = { mx: 0, my: 0, travel: 0 }; // travel = journey progress (0 → 1 with scroll)
    const cur = { rx: 0, ry: 0, roll: 0 };

    /* ---------------- layout (desktop vs mobile planet position) ---------------- */
    function layout() {
      const w = mount.clientWidth;
      const h = mount.clientHeight;
      renderer.setSize(w, h, false);
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      if (w < 768) {
        planet.position.set(0, 1.1, 0);
        planet.scale.setScalar(0.62);
      } else {
        // Desktop: planet on the left of the canvas (text column on the right)
        planet.position.set(-2.0, 0.1, 0);
        planet.scale.setScalar(0.95);
      }
    }
    new ResizeObserver(layout).observe(mount);
    layout();

    window.addEventListener(
      "pointermove",
      (e) => {
        state.mx = (e.clientX / innerWidth - 0.5) * 2;
        state.my = (e.clientY / innerHeight - 0.5) * 2;
      },
      { passive: true },
    );

    /* ---------------- scroll-driven journey ---------------- */
    const gsap = window.gsap;
    const ScrollTrigger = window.ScrollTrigger;
    if (gsap && ScrollTrigger) {
      gsap.registerPlugin(ScrollTrigger);
      if (!REDUCED) {
        gsap.to(state, {
          travel: 1,
          ease: "none",
          scrollTrigger: {
            trigger: heroSection,
            start: "top top",
            end: "bottom top",
            scrub: 0.7,
          },
        });
        // Fade the scene out by the end of the hero
        gsap.to(mount, {
          yPercent: 16,
          opacity: 0,
          ease: "none",
          scrollTrigger: {
            trigger: heroSection,
            start: "top top",
            end: "bottom 40%",
            scrub: 0.6,
          },
        });
      }
    }

    /* ---------------- render loop (pausable) ---------------- */
    const clock = new THREE.Clock();
    let running = false;
    const startLoop = () => {
      if (running || REDUCED) return;
      running = true;
      clock.start();
      renderer.setAnimationLoop(frame);
    };
    const stopLoop = () => {
      if (!running) return;
      running = false;
      renderer.setAnimationLoop(null);
    };

    function frame() {
      const dt = Math.min(clock.getDelta(), 0.05);
      const t = clock.elapsedTime;

      // Travel speed: very slow at rest, gentle at peak scroll
      const speed = 0.12 + state.travel * 0.5;

      // Move stars toward the camera and wrap them behind it
      for (const layer of starLayers) {
        const arr = layer.pts.geometry.attributes.position.array;
        // Closer (bigger) layers move faster
        const layerSpeed = speed * (0.4 + (layer.zMax - layer.zMin) / DEPTH);
        for (let i = 0; i < arr.length; i += 3) {
          arr[i + 2] += layerSpeed * dt * 14;
          if (arr[i + 2] > camera.position.z + 4) {
            arr[i + 2] = layer.zMin;
            const a = Math.random() * Math.PI * 2;
            const r = 3 + Math.random() * 17;
            arr[i] = Math.cos(a) * r;
            arr[i + 1] = Math.sin(a) * r;
          }
        }
        layer.pts.geometry.attributes.position.needsUpdate = true;
      }

      // Planet rotation (very slow at rest, gentler while travelling)
      const spin = 0.04 + state.travel * 0.11;
      planet.rotation.y = t * spin + cur.ry;
      planet.rotation.x = cur.rx;
      core.rotation.y = -t * 0.08;
      ring1.rotation.x = 1.15 + Math.sin(t * 0.3) * 0.12;
      ring1.rotation.y = t * 0.1;
      ring2.rotation.z = t * 0.15;

      // Moons orbit the planet
      for (const md of moonData) {
        const a = t * md.speed + md.phase;
        md.mesh.position.set(
          Math.cos(a) * md.radius,
          Math.sin(a) * md.radius * 0.35 + md.tilt,
          Math.sin(a) * md.radius * 0.55,
        );
        md.mesh.rotation.x = t * 0.6;
        md.mesh.rotation.y = t * 0.4;
      }

      // Camera: mouse parallax + gentle roll while travelling + approach
      cur.ry += (state.mx * 0.45 - cur.ry) * 0.05;
      cur.rx += (-state.my * 0.3 - cur.rx) * 0.05;
      const targetRoll = state.travel * 0.22; // gentle airplane-style bank
      cur.roll += (targetRoll - cur.roll) * 0.06;

      camera.position.z = 9 - state.travel * 0.9; // gentle dive toward the planet
      camera.position.x = cur.ry * 1.2 + 0.7; // camera slightly right, planet left of frame
      camera.position.y = cur.rx * 1.2;
      camera.lookAt(
        planet.position.x * 0.55 * (1 - state.travel * 0.4),
        planet.position.y * (1 - state.travel * 0.4),
        0,
      );
      // Applied after lookAt so it is not overwritten
      camera.rotateZ(cur.roll);

      renderer.render(scene, camera);
    }

    // Pause the loop while the hero is off-screen or the tab is hidden.
    new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) startLoop();
      else stopLoop();
    }).observe(heroSection);
    document.addEventListener("visibilitychange", () => {
      if (document.hidden) stopLoop();
      else startLoop();
    });

    if (REDUCED) {
      renderer.render(scene, camera);
    } else {
      startLoop();
    }

    // Teardown: free GPU memory when the page is discarded
    const dispose = () => {
      stopLoop();
      for (const root of [scene, envScene]) {
        root.traverse((obj) => {
          obj.geometry?.dispose();
          const mats = obj.material && (Array.isArray(obj.material) ? obj.material : [obj.material]);
          mats?.forEach((m) => {
            for (const k in m) if (m[k] && m[k].isTexture) m[k].dispose();
            m.dispose();
          });
        });
      }
      starTex.dispose();
      pmrem.dispose();
      renderer.dispose();
    };
    window.addEventListener("pagehide", dispose, { once: true });

    window.__hero3d = true;

    // The triggers above were added after load; let ScrollTrigger measure them.
    if (gsap && ScrollTrigger) ScrollTrigger.refresh();
  } catch (e) {
    showFallback();
  }
}

/* ------------------------------------------------------------- scheduling */

if (mount && canvas && heroSection) {
  if (REDUCED) {
    // No 3D at all for reduced motion — the CSS poster is the hero.
    showFallback();
  } else {
    const schedule = () => {
      const idle =
        window.requestIdleCallback ||
        ((fn) => setTimeout(fn, 200));
      idle(boot, { timeout: 1500 });
    };

    if (document.readyState === "complete") {
      schedule();
    } else {
      window.addEventListener("load", schedule, { once: true });
    }

    // Only build the scene when the hero is actually near the viewport…
    if ("IntersectionObserver" in window) {
      const gate = new IntersectionObserver(
        (entries) => {
          if (entries.some((e) => e.isIntersecting)) {
            gate.disconnect();
            schedule();
          }
        },
        { rootMargin: "200px" },
      );
      gate.observe(mount);
    }

    // …and show the CSS fallback if the scene never comes up.
    setTimeout(() => {
      if (!booted) showFallback();
    }, 3500);
  }
}
