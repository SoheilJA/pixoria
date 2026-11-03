/**
 * Ringed Planet Scene — Planet with rotating rings and moons
 * Responsive: scales to fit grid dimensions
 */
class RingedPlanetScene extends AsciiScene {
  constructor(options = {}) {
    super(options);
    this.basePlanetRadius = options.planetRadius || 14;
    this.ringRotation = 0;
    this.planetRotation = 0;
    this.moons = [
      { angle: 0, distanceRatio: 1.6, speed: 0.008, size: 2, char: '○' },
      { angle: 2.1, distanceRatio: 2.0, speed: 0.005, size: 1, char: '●' },
      { angle: 4.2, distanceRatio: 1.25, speed: 0.012, size: 1, char: '◦' }
    ];
  }

  update(grid, width, height) {
    super.update(grid, width, height);
    this.clearGrid(grid);

    // Scale planet and rings to fit grid (leave 2-char margin)
    const maxRadius = Math.min(width, height) / 2 - 2;
    this.planetRadius = Math.max(6, Math.min(this.basePlanetRadius, maxRadius * 0.6));
    this.ringInner = this.planetRadius + 2;
    this.ringOuter = Math.min(this.planetRadius + 8, maxRadius);

    const cx = Math.floor(width / 2);
    const cy = Math.floor(height / 2);

    this.ringRotation += 0.003;
    this.planetRotation += 0.005;

    // Draw rings (ellipse with perspective)
    for (let r = this.ringInner; r <= this.ringOuter; r++) {
      const opacity = 1 - (r - this.ringInner) / Math.max(1, this.ringOuter - this.ringInner);
      const chars = ['·', ':', '+', '*', '#'];
      const char = chars[Math.floor(opacity * (chars.length - 1))];

      for (let angle = 0; angle < Math.PI * 2; angle += 0.02) {
        const rotAngle = angle + this.ringRotation;
        const x = cx + Math.round(r * Math.cos(rotAngle));
        const y = cy + Math.round(r * Math.sin(rotAngle) * 0.35);

        const z = Math.sin(rotAngle) * 0.35;
        if (z > -0.2) {
          this.setPixel(grid, x, y, char);
        }
      }
    }

    // Draw planet (circle with surface detail)
    for (let y = -this.planetRadius; y <= this.planetRadius; y++) {
      const halfWidth = Math.round(Math.sqrt(Math.max(0, this.planetRadius * this.planetRadius - y * y)) * 1.2);
      for (let x = -halfWidth; x <= halfWidth; x++) {
        const dist = Math.sqrt(x * x + (y / 1.2) * (y / 1.2));
        if (dist <= this.planetRadius) {
          const angle = Math.atan2(y, x / 1.2) + this.planetRotation;
          const chars = ['█', '▓', '▒', '░', '·'];
          const charIndex = Math.floor((Math.sin(angle * 3) + 1) / 2 * (chars.length - 1));
          this.setPixel(grid, cx + x, cy + y, chars[Math.max(0, Math.min(charIndex, chars.length - 1))]);
        }
      }
    }

    // Draw moons with responsive distance
    this.moons.forEach(moon => {
      moon.angle += moon.speed;
      const moonDistance = Math.min(moon.distanceRatio * this.planetRadius, width * 0.4);
      const mx = cx + Math.round(moonDistance * Math.cos(moon.angle));
      const my = cy + Math.round(moonDistance * Math.sin(moon.angle) * 0.4);
      this.setPixel(grid, mx, my, moon.char);

      // Moon trail
      for (let i = 1; i <= 3; i++) {
        const trailAngle = moon.angle - i * 0.1;
        const trailDist = Math.min((moon.distanceRatio * this.planetRadius - i * 0.5), width * 0.4);
        const tx = cx + Math.round(trailDist * Math.cos(trailAngle));
        const ty = cy + Math.round(trailDist * Math.sin(trailAngle) * 0.4);
        this.setPixel(grid, tx, ty, '·');
      }
    });

    // Ambient stars
    for (let i = 0; i < 15; i++) {
      const sx = (i * 17 + this.time * 5) % width;
      const sy = (i * 23 + this.time * 3) % height;
      this.setPixel(grid, sx, sy, i % 3 === 0 ? '*' : '·');
    }
  }
}

// Register scene
window.AsciiScenes = window.AsciiScenes || {};
window.AsciiScenes['ringed-planet'] = RingedPlanetScene;