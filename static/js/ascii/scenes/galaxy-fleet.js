/**
 * Galaxy Fleet Scene — Multiple ships in formation flying through starfield
 */
class GalaxyFleetScene extends AsciiScene {
  constructor(options = {}) {
    super(options);
    this.ships = this.createFleet(8);
    this.stars = this.createStars(80);
    this.formationAngle = 0;
  }

  createStars(count) {
    const stars = [];
    for (let i = 0; i < count; i++) {
      stars.push({
        x: Math.random() * 80,
        y: Math.random() * 40,
        speed: 0.2 + Math.random() * 0.8,
        size: Math.random() > 0.8 ? 2 : 1
      });
    }
    return stars;
  }

  createFleet(count) {
    const ships = [];
    const baseX = -40;
    const baseY = 20;
    for (let i = 0; i < count; i++) {
      const row = Math.floor(i / 4);
      const col = i % 4;
      ships.push({
        x: baseX + col * 18,
        y: baseY + row * 12,
        offsetX: 0,
        offsetY: 0,
        phase: Math.random() * Math.PI * 2,
        type: i % 3 // 0: fighter, 1: cruiser, 2: carrier
      });
    }
    return ships;
  }

  update(grid, width, height) {
    super.update(grid, width, height);
    this.clearGrid(grid);

    // Starfield
    this.stars.forEach(star => {
      star.x -= star.speed;
      if (star.x < 0) {
        star.x = width - 1;
        star.y = Math.random() * height;
      }
      this.setPixel(grid, Math.floor(star.x), Math.floor(star.y), star.size > 1 ? '*' : '·');
    });

    this.formationAngle += 0.005;

    // Update and draw ships
    this.ships.forEach((ship, i) => {
      // Formation movement
      ship.x += 0.4;
      ship.offsetY = Math.sin(this.time * 2 + ship.phase) * 1.5;
      ship.offsetX = Math.sin(this.time * 1.5 + ship.phase) * 0.8;

      if (ship.x > width + 20) {
        ship.x = -40;
        ship.y = Math.random() * (height - 10) + 5;
      }

      const sx = Math.floor(ship.x + ship.offsetX);
      const sy = Math.floor(ship.y + ship.offsetY);

      // Draw different ship types
      if (ship.type === 0) {
        // Fighter
        this.drawFighter(grid, sx, sy);
      } else if (ship.type === 1) {
        // Cruiser
        this.drawCruiser(grid, sx, sy);
      } else {
        // Carrier
        this.drawCarrier(grid, sx, sy);
      }
    });

    // Formation indicator lines
    this.ships.forEach((ship, i) => {
      if (i < this.ships.length - 1) {
        const next = this.ships[i + 1];
        if (Math.floor(ship.y / 12) === Math.floor(next.y / 12)) {
          // Same row - draw connection
          const x1 = Math.floor(ship.x + 10);
          const x2 = Math.floor(next.x);
          const y = Math.floor(ship.y + ship.offsetY);
          for (let x = x1; x < x2; x += 2) {
            this.setPixel(grid, x, y, '·');
          }
        }
      }
    });
  }

  drawFighter(grid, x, y) {
    const shape = [
      '  ▄▄',
      ' ████▄',
      '██████▄',
      ' ████▀',
      '  ▀▀'
    ];
    shape.forEach((line, i) => {
      for (let j = 0; j < line.length; j++) {
        if (line[j] !== ' ') this.setPixel(grid, x + j, y + i - 2, line[j]);
      }
    });
    // Engine trail
    this.setPixel(grid, x - 2, y, '░');
    this.setPixel(grid, x - 3, y + 1, '▒');
  }

  drawCruiser(grid, x, y) {
    const shape = [
      '    ▄▄▄▄',
      '  ▄██████▄',
      ' ██████████▄',
      '█████████████',
      ' ▀█████████▀',
      '  ▀██████▀',
      '    ▀▀▀▀'
    ];
    shape.forEach((line, i) => {
      for (let j = 0; j < line.length; j++) {
        if (line[j] !== ' ') this.setPixel(grid, x + j - 2, y + i - 3, line[j]);
      }
    });
    // Engines
    this.setPixel(grid, x - 2, y + 1, '▓');
    this.setPixel(grid, x - 2, y + 2, '▓');
  }

  drawCarrier(grid, x, y) {
    const shape = [
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
    shape.forEach((line, i) => {
      for (let j = 0; j < line.length; j++) {
        if (line[j] !== ' ') this.setPixel(grid, x + j - 6, y + i - 4, line[j]);
      }
    });
    // Multiple engines
    for (let i = 0; i < 3; i++) {
      this.setPixel(grid, x - 3 - i, y + 1 + i, '▓');
    }
  }
}

// Register scene
window.AsciiScenes = window.AsciiScenes || {};
window.AsciiScenes['galaxy-fleet'] = GalaxyFleetScene;