/**
 * Starship Scene — Flying ship with engine trail and starfield
 */
class StarshipScene extends AsciiScene {
  constructor(options = {}) {
    super(options);
    this.shipX = -20;
    this.shipY = 0;
    this.speed = options.speed || 0.8;
    this.stars = this.createStars(60);
    this.trail = [];
    this.maxTrail = 30;
  }

  createStars(count) {
    const stars = [];
    for (let i = 0; i < count; i++) {
      stars.push({
        x: Math.random() * 80,
        y: Math.random() * 40,
        speed: 0.5 + Math.random() * 1.5,
        brightness: Math.random()
      });
    }
    return stars;
  }

  update(grid, width, height) {
    super.update(grid, width, height);
    this.clearGrid(grid);

    // Update and draw starfield
    this.stars.forEach(star => {
      star.x -= star.speed * this.speed * 0.5;
      if (star.x < 0) {
        star.x = width - 1;
        star.y = Math.random() * height;
      }
      const char = star.brightness > 0.7 ? '*' : (star.brightness > 0.4 ? '·' : '‧');
      this.setPixel(grid, Math.floor(star.x), Math.floor(star.y), char);
    });

    // Ship position (moves across screen)
    this.shipX += this.speed;
    if (this.shipX > width + 30) {
      this.shipX = -30;
      this.shipY = Math.random() * (height - 10) + 5;
    }

    // Add to trail
    this.trail.unshift({ x: this.shipX, y: this.shipY, life: 1.0 });
    if (this.trail.length > this.maxTrail) this.trail.pop();

    // Draw trail
    this.trail.forEach((point, i) => {
      point.life -= 0.03;
      if (point.life <= 0) return;
      const chars = ['·', '‧', '˙', ' '];
      const charIndex = Math.floor((1 - point.life) * chars.length);
      const char = chars[Math.min(charIndex, chars.length - 1)];
      if (char !== ' ') {
        this.setPixel(grid, Math.floor(point.x), Math.floor(point.y), char);
      }
    });

    // Draw starship
    const sx = Math.floor(this.shipX);
    const sy = Math.floor(this.shipY);
    const ship = [
      '      ▄▄▄▄▄▄',
      '    ▄████████▄',
      '  ▄████████████▄',
      ' ████████████████',
      '██████████████████',
      ' ████████████████',
      '  ▀████████████▀',
      '    ▀████████▀',
      '      ▀▀▀▀▀▀'
    ];

    ship.forEach((line, i) => {
      for (let j = 0; j < line.length; j++) {
        const ch = line[j];
        if (ch !== ' ') {
          this.setPixel(grid, sx + j - 10, sy + i - 4, ch);
        }
      }
    });

    // Engine glow
    const glowChars = ['░', '▒', '▓', '█'];
    for (let i = 0; i < 4; i++) {
      const gx = sx - 12 - i * 2;
      const gy = sy + Math.floor(Math.random() * 3) - 1;
      this.setPixel(grid, gx, gy, glowChars[Math.floor(Math.random() * glowChars.length)]);
    }
  }
}

// Register scene
window.AsciiScenes = window.AsciiScenes || {};
window.AsciiScenes.starship = StarshipScene;