/* Background presets for PixoriaBackground (static/js/pixoria-bg/).

Every uniform the ribbon shader exposes can be keyed per section through
`data-bg-*` attributes; a preset supplies the page-level defaults and the
"hero" state used by the first-visit preloader.

`FOOTER_REST` is special: the pre-footer CTA and the footer always settle into
it, on every page and every preset, so the site ends on the same calm lime
glow. Service pages will add their own presets later (`service-web`, …) and
simply reference FOOTER_REST for their tail.
*/

export const FOOTER_REST = {
  intensity: 0.34,
  glow: 0.42,
  swirl: 0.55,
  scale: 1.15,
  hue: 0.12,
  speed: 0.4,
  x: 0,
  y: 0.1,
};

export const PRESETS = {
  /* Homepage: bright twisting vortex in the hero, breathing through the
     middle sections, calm at the bottom. */
  home: {
    default: {
      intensity: 0.85,
      glow: 0.95,
      swirl: 1.0,
      scale: 1.0,
      hue: 0.0,
      speed: 1.0,
      x: 0,
      y: 0,
    },
    /* Preloader: swirl centred and bright, slow and hypnotic. */
    hero: {
      intensity: 1.25,
      glow: 1.5,
      swirl: 1.15,
      scale: 0.92,
      hue: 0.04,
      speed: 0.7,
      x: 0,
      y: 0,
    },
    /* Per-section moods the homepage sections ask for via data-bg-*. */
    moods: {
      hero: { intensity: 1.05, glow: 1.25, swirl: 1.05, hue: 0.0 },
      work: { intensity: 0.7, glow: 0.7, swirl: 0.8, hue: 0.1 },
      services: { intensity: 0.9, glow: 0.9, swirl: 1.0, hue: 0.18 },
      process: { intensity: 1.0, glow: 1.0, swirl: 1.1, hue: 0.08 },
      contact: { intensity: 0.95, glow: 1.1, swirl: 0.9, hue: 0.0 },
    },
  },
};

/* data-bg-* attribute → uniform key map (kept here so the attribute set is
   defined in one place, shared by the scanner and the docs). */
export const BG_ATTRS = {
  "data-bg-intensity": "intensity",
  "data-bg-glow": "glow",
  "data-bg-swirl": "swirl",
  "data-bg-scale": "scale",
  "data-bg-hue": "hue",
  "data-bg-speed": "speed",
  "data-bg-x": "x",
  "data-bg-y": "y",
};
