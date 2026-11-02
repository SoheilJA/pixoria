/**
 * Deep Space Drift Scene — Slow parallax starfield with nebulae and cosmic dust
 */
class DeepSpaceDriftScene extends AsciiScene {
  constructor(options = {}) {
    super(options);
    this.layers = this.createLayers();
    this.nebulae = this.createNebulae(4);
    this.dustParticles = this.createDust(100);
  }

  createLayers() {
    // Multiple parallax layers for depth
    return [
      { stars: this.createStars(30, 0.05), speed: 0.02, chars: ['‧', '·'], color: 'dim' },
      { stars: this.createStars(25, 0.1), speed: 0.05, chars: ['·', ':'], color: 'normal' },
      { stars: this.createStars(20, 0.2), speed: 0.1, chars: [':', '+'], color: 'bright' },
      { stars: this.createStars(15, 0.3), speed: 0.15, chars: ['+', '*'], color: 'bright' }
    ];
  }

  createStars(count, depth) {
    const stars = [];
    for (let i = 0; i < count; i++) {
      stars.push({
        x: Math.random() * 80,
        y: Math.random() * 40,
        phase: Math.random() * Math.PI * 2,
        twinkleSpeed: 0.01 + Math.random() * 0.03,
        baseBrightness: Math.random(),
        depth
      });
    }
    return stars;
  }

  createNebulae(count) {
    const nebulae = [];
    for (let i = 0; i < count; i++) {
      nebulae.push({
        x: Math.random() * 80,
        y: Math.random() * 40,
        radiusX: 8 + Math.random() * 12,
        radiusY: 4 + Math.random() * 8,
        rotation: Math.random() * Math.PI * 2,
        rotSpeed: (Math.random() - 0.5) * 0.0005,
        phase: Math.random() * Math.PI * 2,
        pulseSpeed: 0.002 + Math.random() * 0.003,
        color: ['░', '▒', '▓', '█', '▒', '░']
      });
    }
    return nebulae;
  }

  createDust(count) {
    const dust = [];
    for (let i = 0; i < count; i++) {
      dust.push({
        x: Math.random() * 80,
        y: Math.random() * 40,
        vx: (Math.random() - 0.5) * 0.02,
        vy: (Math.random() - 0.5) * 0.01,
        size: Math.random() > 0.9 ? 2 : 1,
        life: Math.random(),
        decay: 0.0005 + Math.random() * 0.001
      });
    }
    return dust;
  }

  update(grid, width, height) {
    super.update(grid, width, height);
    this.clearGrid(grid);

    // Update and draw parallax star layers (back to front)
    this.layers.forEach(layer => {
      layer.stars.forEach(star => {
        star.x -= layer.speed;
        if (star.x < 0) {
          star.x = width - 1;
          star.y = Math.random() * height;
        }

        // Twinkling
        star.phase += star.twinkleSpeed;
        const brightness = star.baseBrightness + Math.sin(star.phase) * 0.3;
        const charIndex = Math.floor(Math.max(0, Math.min(brightness, 0.99)) * (layer.chars.length - 1));
        const char = layer.chars[charIndex];

        this.setPixel(grid, Math.floor(star.x), Math.floor(star.y), char);
      });
    });

    // Update and draw nebulae
    this.nebulae.forEach(nebula => {
      nebula.rotation += nebula.rotSpeed;
      nebula.phase += nebula.pulseSpeed;
      const pulse = (Math.sin(nebula.phase) + 1) / 2;

      for (let angle = 0; angle < Math.PI * 2; angle += 0.05) {
        for (let r = 0; r < nebula.radiusX; r += 0.5) {
          const x = nebula.x + Math.round(r * Math.cos(angle + nebula.rotation) * Math.cos(nebula.rotation) - r * Math.sin(angle + nebula.rotation) * Math.sin(nebula.rotation) * 0.5);
          const y = nebula.y + Math.round(r * Math.sin(angle + nebula.rotation) * 0.4);

          const dist = r / nebula.radiusX;
          const intensity = (1 - dist) * pulse;
          const charIndex = Math.floor(intensity * (nebula.color.length - 1));
          const char = nebula.color[Math.max(0, Math.min(charIndex, nebula.color.length - 1))];

          if (char !== ' ' && intensity > 0.15) {
            this.setPixel(grid, x, y, char);
          }
        }
      }
    });

    // Update and draw cosmic dust
    this.dustParticles = this.dustParticles.filter(p => {
      p.x += p.vx;
      p.y += p.vy;
      p.life -= p.decay;

      if (p.life <= 0 || p.x < 0 || p.x >= width || p.y < 0 || p.y >= height) {
        // Respawn
        p.x = Math.random() * width;
        p.y = Math.random() * height;
        p.vx = (Math.random() - 0.5) * 0.02;
        p.vy = (Math.random() - 0.5) * 0.01;
        p.life = 1;
        return true;
      }

      const char = p.size > 1 ? '·' : '‧';
      this.setPixel(grid, Math.floor(p.x), Math.floor(p.y), char);
      return true;
    });

    // Occasional shooting star
    if (Math.random() < 0.003) {
      this.spawnShootingStar(width, height);
    }

    // Draw shooting stars
    this.shootingStars = this.shootingStars || [];
    this.shootingStars = this.shootingStars.filter(s => {
      s.x += s.vx;
      s.y += s.vy;
      s.life -= 0.02;

      if (s.life <= 0 || s.x < 0 || s.x >= width || s.y < 0 || s.y >= height) {
        return false;
      }

      // Draw trail
      for (let i = 0; i < 8; i++) {
        const tx = Math.floor(s.x - i * s.vx);
        const ty = Math.floor(s.y - i * s.vy);
        const chars = ['█', '▓', '▒', '░', '·', '‧'];
        const char = chars[Math.min(i, chars.length - 1)];
        this.setPixel(grid, tx, ty, char);
      }
      return true;
    });
  }

  spawnShootingStar(width, height) {
    const side = Math.floor(Math.random() * 4);
    let x, y, vx, vy;

    switch (side) {
      case 0: // Top
        x = Math.random() * width;
        y = -5;
        vx = (Math.random() - 0.5) * 2;
        vy = 2 + Math.random() * 2;
        break;
      case 1: // Right
        x = width + 5;
        y = Math.random() * height;
        vx = -2 - Math.random() * 2;
        vy = (Math.random() - 0.5) * 2;
        break;
      case 2: // Bottom
        x = Math.random() * width;
        y = height + 5;
        vx = (Math.random() - 0.5) * 2;
        vy = -2 - Math.random() * 2;
        break;
      case 3: // Left
        x = -5;
        y = Math.random() * height;
        vx = 2 + Math.random() * 2;
        vy = (Math.random() - 0.5) * 2;
        break;
    }

    this.shootingStars = this.shootingStars || [];
    this.shootingStars.push({ x, y, vx, vy, life: 1 });
  }
}

// Register scene
window.AsciiScenes = window.AsciiScenes || {};
window.AsciiScenes['deep-space-drift'] = DeepSpaceDriftScene;