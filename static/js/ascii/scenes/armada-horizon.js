/**
 * Armada Horizon Scene — Large fleet on horizon with perspective
 */
class ArmadaHorizonScene extends AsciiScene {
  constructor(options = {}) {
    super(options);
    this.ships = this.createArmada(12);
    this.stars = this.createStars(50);
    this.horizonY = 28;
  }

  createStars(count) {
    const stars = [];
    for (let i = 0; i < count; i++) {
      stars.push({
        x: Math.random() * 80,
        y: Math.random() * this.horizonY,
        brightness: Math.random()
      });
    }
    return stars;
  }

  createArmada(count) {
    const ships = [];
    for (let i = 0; i < count; i++) {
      ships.push({
        x: Math.random() * 80,
        z: 0.3 + Math.random() * 0.7, // Depth (0.3 = far, 1.0 = near)
        type: Math.floor(Math.random() * 4),
        speed: 0.15 + Math.random() * 0.25,
        phase: Math.random() * Math.PI * 2,
        scale: 1
      });
    }
    return ships;
  }

  update(grid, width, height) {
    super.update(grid, width, height);
    this.clearGrid(grid);

    // Draw starfield above horizon
    this.stars.forEach(star => {
      const char = star.brightness > 0.7 ? '*' : (star.brightness > 0.4 ? '·' : '‧');
      this.setPixel(grid, Math.floor(star.x), Math.floor(star.y), char);
    });

    // Draw horizon line
    for (let x = 0; x < width; x++) {
      this.setPixel(grid, x, this.horizonY, '─');
    }

    // Update and draw armada ships (sorted by depth - far to near)
    const sortedShips = [...this.ships].sort((a, b) => a.z - b.z);

    sortedShips.forEach(ship => {
      ship.x += ship.speed * ship.z;
      if (ship.x > width + 20) {
        ship.x = -30;
        ship.z = 0.3 + Math.random() * 0.7;
        ship.type = Math.floor(Math.random() * 4);
      }

      // Perspective scaling
      const scale = 0.4 + ship.z * 0.6;
      const sy = this.horizonY - Math.floor(3 * ship.z);
      const sx = Math.floor(ship.x);

      this.drawArmadaShip(grid, sx, sy, ship.type, scale, ship.z);
    });

    // Water/reflection below horizon
    for (let y = this.horizonY + 1; y < height; y += 2) {
      for (let x = 0; x < width; x += 4) {
        this.setPixel(grid, x, y, y % 4 === 0 ? '∼' : '≈');
      }
    }
  }

  drawArmadaShip(grid, x, y, type, scale, depth) {
    const chars = depth > 0.7 ? ['█', '▓', '▒'] : ['▓', '▒', '░'];
    const mainChar = chars[0];
    const detailChar = chars[1];
    const lightChar = chars[2];

    switch (type) {
      case 0: // Battleship
        this.drawBattleship(grid, x, y, mainChar, detailChar, scale);
        break;
      case 1: // Carrier
        this.drawCarrier(grid, x, y, mainChar, detailChar, scale);
        break;
      case 2: // Cruiser
        this.drawCruiser(grid, x, y, mainChar, detailChar, scale);
        break;
      case 3: // Destroyer
        this.drawDestroyer(grid, x, y, mainChar, detailChar, scale);
        break;
    }

    // Wake trail
    for (let i = 1; i <= 5; i++) {
      const wx = x - i * 2;
      const wy = y + Math.floor(i * 0.3);
      if (wx >= 0) this.setPixel(grid, wx, wy, i % 2 === 0 ? '∼' : '≈');
    }
  }

  drawBattleship(grid, x, y, main, detail, scale) {
    const w = Math.max(8, Math.floor(14 * scale));
    // Hull
    for (let i = 0; i < w; i++) {
      this.setPixel(grid, x + i, y, main);
    }
    // Superstructure
    for (let i = 2; i < w - 2; i++) {
      this.setPixel(grid, x + i, y - 1, detail);
      if (i > 3 && i < w - 5) this.setPixel(grid, x + i, y - 2, main);
    }
    // Turrets
    this.setPixel(grid, x + 2, y - 3, '▲');
    this.setPixel(grid, x + w - 3, y - 3, '▲');
  }

  drawCarrier(grid, x, y, main, detail, scale) {
    const w = Math.max(10, Math.floor(18 * scale));
    // Flight deck
    for (let i = 0; i < w; i++) {
      this.setPixel(grid, x + i, y, main);
    }
    // Island
    this.setPixel(grid, x + w - 4, y - 1, detail);
    this.setPixel(grid, x + w - 4, y - 2, main);
    this.setPixel(grid, x + w - 3, y - 2, main);
  }

  drawCruiser(grid, x, y, main, detail, scale) {
    const w = Math.max(6, Math.floor(10 * scale));
    // Hull
    for (let i = 0; i < w; i++) {
      this.setPixel(grid, x + i, y, main);
    }
    // Bridge
    for (let i = 1; i < w - 1; i++) {
      this.setPixel(grid, x + i, y - 1, detail);
    }
    // Turret
    this.setPixel(grid, x + Math.floor(w/2), y - 2, '▲');
  }

  drawDestroyer(grid, x, y, main, detail, scale) {
    const w = Math.max(5, Math.floor(8 * scale));
    // Sleek hull
    for (let i = 0; i < w; i++) {
      this.setPixel(grid, x + i, y, main);
    }
    // Pointed bow
    this.setPixel(grid, x - 1, y, '▶');
    // Small bridge
    this.setPixel(grid, x + 2, y - 1, detail);
  }
}

// Register scene
window.AsciiScenes = window.AsciiScenes || {};
window.AsciiScenes['armada-horizon'] = ArmadaHorizonScene;