/**
 * Globe Scene — Rotating wireframe sphere with latitude/longitude lines
 */
class GlobeScene extends AsciiScene {
  constructor(options = {}) {
    super(options);
    this.radius = options.radius || 12;
    this.rotationY = 0;
    this.rotationX = 0.3;
    this.latLines = parseInt(options.latLines) || 6;
    this.lonLines = parseInt(options.lonLines) || 10;
  }

  update(grid, width, height) {
    super.update(grid, width, height);
    this.rotationY += 0.008;
    this.rotationX += 0.002;

    this.clearGrid(grid);
    const cx = Math.floor(width / 2);
    const cy = Math.floor(height / 2);

    // Draw latitude lines (horizontal circles)
    for (let i = 1; i < this.latLines; i++) {
      const phi = (i / this.latLines) * Math.PI;
      const r = this.radius * Math.sin(phi);
      const y = cy + Math.round(this.radius * Math.cos(phi) * 0.5);

      for (let angle = 0; angle < Math.PI * 2; angle += 0.05) {
        const x3d = r * Math.cos(angle);
        const z3d = r * Math.sin(angle);

        // Rotate around Y
        const xRot = x3d * Math.cos(this.rotationY) - z3d * Math.sin(this.rotationY);
        const zRot = x3d * Math.sin(this.rotationY) + z3d * Math.cos(this.rotationY);

        // Rotate around X
        const yRot = y * Math.cos(this.rotationX) - zRot * Math.sin(this.rotationX);
        const zFinal = y * Math.sin(this.rotationX) + zRot * Math.cos(this.rotationX);

        const x2d = cx + Math.round(xRot);
        const y2d = cy + Math.round(yRot - cy);

        if (zFinal > -0.5) {
          this.setPixel(grid, x2d, y2d, '.');
        }
      }
    }

    // Draw longitude lines (vertical circles)
    for (let i = 0; i < this.lonLines; i++) {
      const theta = (i / this.lonLines) * Math.PI * 2;
      for (let phi = 0; phi <= Math.PI; phi += 0.05) {
        const x3d = this.radius * Math.sin(phi) * Math.cos(theta);
        const y3d = this.radius * Math.cos(phi);
        const z3d = this.radius * Math.sin(phi) * Math.sin(theta);

        // Rotate around Y
        const xRot = x3d * Math.cos(this.rotationY) - z3d * Math.sin(this.rotationY);
        const zRot = x3d * Math.sin(this.rotationY) + z3d * Math.cos(this.rotationY);

        // Rotate around X
        const yRot = y3d * Math.cos(this.rotationX) - zRot * Math.sin(this.rotationX);
        const zFinal = y3d * Math.sin(this.rotationX) + zRot * Math.cos(this.rotationX);

        const x2d = cx + Math.round(xRot);
        const y2d = cy + Math.round(yRot * 0.5);

        const char = zFinal > 0 ? '•' : '·';
        this.setPixel(grid, x2d, y2d, char);
      }
    }

    // Draw equator highlight
    for (let angle = 0; angle < Math.PI * 2; angle += 0.04) {
      const x3d = this.radius * Math.cos(angle);
      const z3d = this.radius * Math.sin(angle);

      const xRot = x3d * Math.cos(this.rotationY) - z3d * Math.sin(this.rotationY);
      const zRot = x3d * Math.sin(this.rotationY) + z3d * Math.cos(this.rotationY);
      const yRot = 0 * Math.cos(this.rotationX) - zRot * Math.sin(this.rotationX);
      const zFinal = 0 * Math.sin(this.rotationX) + zRot * Math.cos(this.rotationX);

      const x2d = cx + Math.round(xRot);
      const y2d = cy + Math.round(yRot);

      if (zFinal > -0.5) {
        this.setPixel(grid, x2d, y2d, 'o');
      }
    }
  }
}

// Register scene
window.AsciiScenes = window.AsciiScenes || {};
window.AsciiScenes.globe = GlobeScene;