/**
 * ASCII Engine — Core rendering engine for ASCII art scenes
 * Features: grid-based rendering, IntersectionObserver for offscreen pause,
 * reduced motion support, HTMX hook integration, <=30fps throttling
 */
class AsciiEngine {
  constructor(options = {}) {
    this.canvas = options.canvas;
    this.scene = options.scene;
    this.fps = options.fps || 30;
    this.frameInterval = 1000 / this.fps;
    this.lastFrameTime = 0;
    this.rafId = null;
    this.isRunning = false;
    this.isVisible = false;
    this.reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    this.gridWidth = options.gridWidth || 80;
    this.gridHeight = options.gridHeight || 40;
    this.grid = this.createGrid();
    this.observer = null;

    this.initObserver();
    this.handleVisibilityChange = this.handleVisibilityChange.bind(this);
    document.addEventListener('visibilitychange', this.handleVisibilityChange);

    // HTMX integration - re-init after swaps
    document.body.addEventListener('htmx:afterSwap', (e) => {
      if (e.detail.target.querySelector?.('[data-ascii-scene]')) {
        this.initFromDOM(e.detail.target);
      }
    });

    if (this.canvas && this.scene) {
      this.init(this.canvas, this.scene);
    }
  }

  createGrid() {
    return Array(this.gridHeight).fill(null).map(() =>
      Array(this.gridWidth).fill(' ')
    );
  }

  clearGrid() {
    for (let y = 0; y < this.gridHeight; y++) {
      for (let x = 0; x < this.gridWidth; x++) {
        this.grid[y][x] = ' ';
      }
    }
  }

  initObserver() {
    if (!this.canvas) return;

    this.observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          this.isVisible = entry.isIntersecting;
          if (this.isVisible) {
            this.start();
          } else {
            this.pause();
          }
        });
      },
      { rootMargin: '50px', threshold: 0.01 }
    );

    this.observer.observe(this.canvas);

    // ResizeObserver to handle layout changes (not just window resize)
    // Observe the parent wrapper since canvas is 100% width/height
    if (window.ResizeObserver) {
      const wrapper = this.canvas.parentElement;
      if (wrapper) {
        this.resizeObserver = new ResizeObserver(() => this.resize());
        this.resizeObserver.observe(wrapper);
      }
    }
  }

  handleVisibilityChange() {
    if (document.hidden) {
      this.pause();
    } else if (this.isVisible) {
      this.start();
    }
  }

  init(canvas, scene) {
    this.canvas = canvas;
    this.scene = scene;
    this.ctx = canvas.getContext('2d');
    this.resize();
    window.addEventListener('resize', () => this.resize());
    this.start();
  }

  resize() {
    if (!this.canvas) return;
    const rect = this.canvas.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    this.canvas.width = rect.width * dpr;
    this.canvas.height = rect.height * dpr;
    this.ctx.scale(dpr, dpr);
    this.canvas.style.width = rect.width + 'px';
    this.canvas.style.height = rect.height + 'px';

    // Recalculate grid based on font size
    const fontSize = parseFloat(getComputedStyle(this.canvas).fontSize) || 10;
    const charWidth = fontSize * 0.6;
    const charHeight = fontSize * 1.2;
    this.gridWidth = Math.max(40, Math.floor(rect.width / charWidth));
    this.gridHeight = Math.max(20, Math.floor(rect.height / charHeight));
    this.grid = this.createGrid();
  }

  start() {
    if (this.isRunning || this.reducedMotion) return;
    this.isRunning = true;
    this.lastFrameTime = performance.now();
    this.tick();
  }

  pause() {
    this.isRunning = false;
    if (this.rafId) {
      cancelAnimationFrame(this.rafId);
      this.rafId = null;
    }
  }

  tick(timestamp) {
    if (!this.isRunning) return;

    const elapsed = timestamp - this.lastFrameTime;
    if (elapsed >= this.frameInterval) {
      this.lastFrameTime = timestamp - (elapsed % this.frameInterval);
      this.update();
      this.render();
    }

    this.rafId = requestAnimationFrame((t) => this.tick(t));
  }

  update() {
    if (this.scene && typeof this.scene.update === 'function') {
      this.scene.update(this.grid, this.gridWidth, this.gridHeight);
    }
  }

  render() {
    if (!this.ctx || !this.canvas) return;

    const rect = this.canvas.getBoundingClientRect();
    const fontSize = parseFloat(getComputedStyle(this.canvas).fontSize) || 10;
    const lineHeight = fontSize * 1.2;

    this.ctx.clearRect(0, 0, rect.width, rect.height);
    this.ctx.fillStyle = getComputedStyle(this.canvas).color || '#d8cfc0';
    this.ctx.font = `${fontSize}px "JetBrains Mono", "Fira Code", monospace`;
    this.ctx.textBaseline = 'top';

    for (let y = 0; y < this.gridHeight; y++) {
      const line = this.grid[y].join('');
      if (line.trim()) {
        this.ctx.fillText(line, 0, y * lineHeight);
      }
    }
  }

  setScene(scene) {
    this.scene = scene;
    this.clearGrid();
  }

  destroy() {
    this.pause();
    if (this.observer) {
      this.observer.disconnect();
      this.observer = null;
    }
    if (this.resizeObserver) {
      this.resizeObserver.disconnect();
      this.resizeObserver = null;
    }
    document.removeEventListener('visibilitychange', this.handleVisibilityChange);
  }
}

/**
 * Scene base class - extend for custom scenes
 */
class AsciiScene {
  constructor(options = {}) {
    this.time = 0;
    this.options = options;
  }

  clearGrid(grid) {
    for (let y = 0; y < grid.length; y++) {
      for (let x = 0; x < grid[y].length; x++) {
        grid[y][x] = ' ';
      }
    }
  }

  update(grid, width, height) {
    this.time += 1/30;
    // Override in subclasses
  }

  setPixel(grid, x, y, char) {
    if (!grid || grid.length === 0 || !grid[0] || grid[0].length === 0) return;
    const xi = Math.round(x);
    const yi = Math.round(y);
    if (xi >= 0 && xi < grid[0].length && yi >= 0 && yi < grid.length) {
      grid[yi][xi] = char;
    }
  }

  drawLine(grid, x0, y0, x1, y1, char) {
    const dx = Math.abs(x1 - x0);
    const dy = Math.abs(y1 - y0);
    const sx = x0 < x1 ? 1 : -1;
    const sy = y0 < y1 ? 1 : -1;
    let err = dx - dy;

    while (true) {
      this.setPixel(grid, x0, y0, char);
      if (x0 === x1 && y0 === y1) break;
      const e2 = 2 * err;
      if (e2 > -dy) { err -= dy; x0 += sx; }
      if (e2 < dx) { err += dx; y0 += sy; }
    }
  }

  drawCircle(grid, cx, cy, radius, char, filled = false) {
    if (filled) {
      for (let y = -radius; y <= radius; y++) {
        for (let x = -radius; x <= radius; x++) {
          if (x*x + y*y <= radius*radius) {
            this.setPixel(grid, cx + x, cy + y, char);
          }
        }
      }
    } else {
      for (let angle = 0; angle < Math.PI * 2; angle += 0.1) {
        const x = Math.round(cx + Math.cos(angle) * radius);
        const y = Math.round(cy + Math.sin(angle) * radius * 0.5);
        this.setPixel(grid, x, y, char);
      }
    }
  }
}

// Auto-initialize from DOM
function initAsciiFromDOM(root = document) {
  root.querySelectorAll('[data-ascii-scene]').forEach(el => {
    if (el._asciiEngine) return;

    const sceneName = el.dataset.asciiScene;
    const SceneClass = window.AsciiScenes?.[sceneName];
    if (!SceneClass) {
      console.warn(`ASCII Scene "${sceneName}" not found`);
      return;
    }

    const canvas = el.querySelector('canvas') || el;
    const scene = new SceneClass({
      ...el.dataset,
      ...JSON.parse(el.dataset.asciiOptions || '{}')
    });

    const engine = new AsciiEngine({
      canvas,
      scene,
      fps: parseInt(el.dataset.asciiFps) || 30,
      gridWidth: parseInt(el.dataset.asciiWidth) || 80,
      gridHeight: parseInt(el.dataset.asciiHeight) || 40
    });

    el._asciiEngine = engine;
  });
}

// Expose globally
window.AsciiEngine = AsciiEngine;
window.AsciiScene = AsciiScene;
window.initAsciiFromDOM = initAsciiFromDOM;
window.AsciiScenes = window.AsciiScenes || {};

// Auto-init on DOM ready - DISABLED by default to allow manual scene loading
// Pages should call window.initAsciiFromDOM() after loading their scenes
// if (document.readyState === 'loading') {
//   document.addEventListener('DOMContentLoaded', () => initAsciiFromDOM());
// } else {
//   initAsciiFromDOM();
// }