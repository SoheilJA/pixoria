import { $, $$, isDark } from './utils.js';

function pixSVG(rows, pal) {
  const w = Math.max(...rows.map((r) => r.length));
  let rects = "";
  rows.forEach((r, y) => {
    for (let x = 0; x < r.length; x++) {
const c = pal[r[x]];
if (c)
  rects += `<rect x="${x}" y="${y}" width="1" height="1" fill="${c}"/>`;
    }
  });
  return `<svg class="pixart" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${w} ${rows.length}" shape-rendering="crispEdges" aria-hidden="true" focusable="false">${rects}</svg>`;
}
function drawMat(ctx, rows, pal, x, y, s = 1) {
  for (let r = 0; r < rows.length; r++) {
    const row = rows[r];
    for (let c = 0; c < row.length; c++) {
const col = pal[row[c]];
if (col) {
  ctx.fillStyle = col;
  ctx.fillRect(x + c * s, y + r * s, s, s);
}
    }
  }
}
const SPAL = {
  K: "#241f1c",
  W: "#f6f2e7",
  A: "#9c3f66",
  B: "#2e6e6a",
  Y: "#c99a2e",
  R: "#b8503d",
  G: "#4a8a5f",
};
const SPRITES = {
  browser: [
    [
"KKKKKKKKKKKK",
"KAAAAAAAAAAK",
"KKKKKKKKKKKK",
"KWWWWWWWWWWK",
"KWWWKKKWWWWK",
"KWWWWWWWWWWK",
"KWWWWWKKKWWK",
"KWWWWWKKKWWK",
"KWWWWWWWWWWK",
"KKKKKKKKKKKK",
"............",
"............",
    ],
  ],
  chip: [
    [
"..K..K..K...",
".KKKKKKKKK..",
".KWWWWWWWK..",
"KKWKAAAKWKK.",
"KWKAKKKKAKWK",
"KWKAKKKKAKWK",
"KKWKAAAKWKK.",
".KWWWWWWWK..",
".KKKKKKKKK..",
"..K..K..K...",
"............",
"............",
    ],
  ],
  brush: [
    [
".......KK...",
"......KWK...",
".....KWK....",
"....KWK.....",
"...KWK......",
"..KWK.......",
".KWK........",
".KAAK.......",
".KAAK.......",
".KAAK.......",
"..KK........",
"............",
    ],
  ],
  palette: [
    [
"..KKKKK.....",
".KWWWWWK....",
"KWRWKWYWK...",
"KWWWWWWWK...",
"KWKWWWKBK...",
".KWWWWWWK...",
"..KKKWWK....",
".....KK.....",
"............",
"............",
"............",
"............",
    ],
  ],
  signal: [
    [
"........KK..",
".......KWK..",
"......KWK...",
".....KWK....",
"....KWK.....",
"..KKWK......",
".KWWKKKK....",
"KWWWWWWK....",
"KWWWWWWK....",
"KKKKKKKK....",
"............",
"............",
    ],
  ],
};
const IPAL = {
  K: "#241f1c",
  Y: "#c99a2e",
  W: "#f6f2e7",
  R: "#b8503d",
  S: "#8a8a92",
  T: "#4a8a5f",
};
const ICONS = {
  coin: [
    "..KKKK..",
    ".KYYYYK.",
    ".KYKKYK.",
    ".KYKKYK.",
    ".KYYYYK.",
    "..KKKK..",
  ],
  map: [
    "KKKKKKKK",
    "KWWKWWWK",
    "KWWKWKWK",
    "KWWKWWWK",
    "KWRRWWWK",
    "KKKKKKKK",
  ],
  hammer: [
    "..KKKK..",
    ".KSSSSK.",
    ".KSSSSK.",
    "..KKKK..",
    "...KWK..",
    "...KWK..",
    "...KWK..",
    "...KKK..",
  ],
  bug: [
    "K......K",
    ".KTTTTK.",
    "KKTWTTKK",
    ".KTTTTK.",
    "K.KTTK.K",
    ".K.KK.K.",
  ],
  flag: [
    ".KKKKKK.",
    ".KRRRRK.",
    ".KRRRK..",
    ".KRRK...",
    ".KRK....",
    ".KK.....",
    ".KWK....",
    ".KKK....",
  ],
};
/* Ã™â€¦Ã™Ë†Ã˜Â´ÃšÂ© (Ã›Â±Ã›Â²Ãƒâ€”Ã›Â²Ã›Â´) */
const ROCKET = [
  ".....RR.....",
  "....RRRR....",
  "....WWWW....",
  "...WWWWWW...",
  "...WWWWWW...",
  "..WWWWWWWW..",
  "..WWWWWWWW..",
  ".WWWWWWWWWW.",
  ".WWGGGGGGWW.",
  ".WWGGGGGGWW.",
  ".WWWWWWWWWW.",
  ".WWWWWWWWWW.",
  ".WWRWWWWRWW.",
  ".WWWWWWWWWW.",
  ".WWWWWWWWWW.",
  "WW.WWWWWW.WW",
  "WWW.WWWW.WWW",
  "RWW.WWWW.WWR",
  "RR.WW..WW.RR",
  "RR.DDDDDD.RR",
  "....DDDD....",
  "....DDDD....",
  ".....DD.....",
  "............",
];
const ROCKET_P = {
  R: "#e2543e",
  W: "#f4f6fb",
  G: "#9adfff",
  D: "#6a7390",
};
/* Ã™â€¡Ã™â€¦Ã˜Â±Ã˜Â§Ã™â€¡: Ã˜Â¨Ã›Å’Ã™Â¾ (Ã›Â±Ã›Â²Ãƒâ€”Ã›Â±Ã›Â²) */
const BEEP_A = [
  ".....KK.....",
  "....KRRK....",
  ".....KK.....",
  "..KKKKKKKK..",
  ".KYYYYYYYYK.",
  "KYYYYYYYYYYK",
  "KYYWWYYWWYYK",
  "KYYWKYYWKYYK",
  "KYYYYYYYYYYK",
  "KYYYKKKKYYYK",
  ".KYYYYYYYYK.",
  "..KKKKKKKK..",
];
const BEEP_B = [
  ".....KK.....",
  "....KYYK....",
  ".....KK.....",
  "..KKKKKKKK..",
  ".KYYYYYYYYK.",
  "KYYYYYYYYYYK",
  "KYYKKYYKKYYK",
  "KYYYYYYYYYYK",
  "KYYYYYYYYYYK",
  "KYYKKKKKKYYK",
  ".KYYYYYYYYK.",
  "..KKKKKKKK..",
];
const BEEP_P = { K: "#141a3a", Y: "#ffd23f", R: "#ff5252", W: "#141a3a" };
/* Ã™ÂÃ˜Â¶Ã˜Â§Ã™â€ Ã™Ë†Ã˜Â±Ã˜Â¯ (Ã›Â±Ã›Â°Ãƒâ€”Ã›Â±Ã›Â´) */
const AST_A = [
  "...KKKK...",
  "..KWWWWK..",
  "..KWGGWK..",
  "..KWGGWK..",
  "...KWWK...",
  "..KWWWWK..",
  ".WKWWWWKW.",
  ".WKWWWWKW.",
  "..KWWWWK..",
  "..KAWWAK..",
  "..KWWWWK..",
  "..KW..WK..",
  "..KW..WK..",
  "..KK..KK..",
];
const AST_B = [
  "...KKKK...",
  "..KWWWWK..",
  "..KWGGWK..",
  "..KWGGWK..",
  "...KWWK...",
  "..KWWWWK..",
  ".WKWWWWKW.",
  ".WKWWWWKW.",
  "..KWWWWK..",
  "..KAWWAK..",
  "..KWWWWK..",
  ".KW....WK.",
  ".KW....WK.",
  ".KK....KK.",
];
const AST_STAND = [
  "...KKKK...",
  "..KWWWWK..",
  "..KWGGWK..",
  "..KWGGWK..",
  "...KWWK...",
  "..KWWWWK..",
  ".WKWWWWKW.",
  ".WKWWWWKW.",
  "..KWWWWK..",
  "..KAWWAK..",
  "..KWWWWK..",
  "..KW..WK..",
  "..KW..WK..",
  "..KK..KK..",
];
const AST_P = { K: "#141a3a", W: "#f2f5fb", G: "#8fd8ff", A: "#e2543e" };
/* Ã™â€ Ã™Ë†Ã˜Â´Ã¢â‚¬Å’ÃšÂ©Ã˜Â±Ã™Ë†Ã™â€¦ (Ã›Â±Ã›Â²Ãƒâ€”Ã›Â±Ã›Â²) */
const CHOM_C = [
  "....KKKK....",
  "..KKYYYYKK..",
  ".KYYYYYYYYK.",
  "KYYKYYYYKYYK",
  "KYYKYYYYKYYK",
  "KYYYYYYYYYYK",
  "KYYYYYYYYKKK",
  "KYYYYYYYKKKK",
  "KYYYYYYYKKKK",
  "KYYYYYYYYKKK",
  ".KYYYYYYYYK.",
  "..KKYYYYKK..",
];
const CHOM_O = [
  "....KKKK....",
  "..KKYYYYKK..",
  ".KYYYYYYYYK.",
  "KYYKYYYYKYYK",
  "KYYKYYYYKYYK",
  "KYYYYYYYYYYK",
  "KYYYYYYYKKKK",
  "KYYYYYYK....",
  "KYYYYYYK....",
  "KYYYYYYYKKKK",
  ".KYYYYYYYYK.",
  "..KKYYYYKK..",
];
const CHOM_P = { K: "#141a3a", Y: "#e8b64c" };
/* Ã˜Â±Ã™Ë†Ã˜Â­Ã¢â‚¬Å’Ã™â€¡Ã˜Â§ (Ã›Â±Ã›Â°Ãƒâ€”Ã›Â±Ã›Â²) */
const GHOST_A = [
  "...KKKK...",
  "..KVVVVK..",
  ".KVVVVVVK.",
  "KVVVVVVVVK",
  "KWWVVVVWWK",
  "KWWVVVVWWK",
  "KVVVVVVVVK",
  "KVVVVVVVVK",
  "KVVVVVVVVK",
  "KVKVVVVKVK",
  ".K.KVVK.K.",
  "..........",
];
const GHOST_B = [
  "...KKKK...",
  "..KVVVVK..",
  ".KVVVVVVK.",
  "KVVVVVVVVK",
  "KWWVVVVWWK",
  "KWWVVVVWWK",
  "KVVVVVVVVK",
  "KVVVVVVVVK",
  "KVVVVVVVVK",
  "KKKVVVVKKK",
  "..KK..KK..",
  "..........",
];
const HEART = [
  ".KK...KK.",
  "KRRK.KRRK",
  "KRRRKKRRK",
  "KRRRRRRRK",
  ".KRRRRRK.",
  "..KRRRK..",
  "...KRK...",
  "....K....",
];
const HEART_P = { K: "#141a3a", R: "#e05b4a" };
/* Ã˜Â®Ã™Ë†Ã˜Â±Ã˜Â´Ã›Å’Ã˜Â¯ Ã™Ë† Ã™â€¦Ã˜Â§Ã™â€¡ */
const SUN_M = [
  "....YY....",
  "..Y.YY.Y..",
  "...YYYY...",
  "..YYYYYY..",
  ".YYYYYYYY.",
  ".YYYYYYYY.",
  ".YYYYYYYY.",
  "..YYYYYY..",
  "...YYYY...",
  "..Y.YY.Y..",
  "....YY....",
];
const SUN_P = { Y: "#ffb347" };
const MOON_M = [
  "....MMM....",
  "..MMMMM....",
  ".MMMM......",
  ".MMC.......",
  ".MMM.......",
  ".MMC.......",
  ".MMMM......",
  "..MMMMM....",
  "....MMM....",
];
const MOON_P = { M: "#eaeef5", C: "#c3cbda" };
function injectSprites() {
  $$("[data-sprite]").forEach((el) => {
    el.innerHTML = pixSVG(SPRITES[el.dataset.sprite][0], SPAL);
  });
  $$("[data-ico]").forEach((el) => {
    el.innerHTML = pixSVG(ICONS[el.dataset.ico], IPAL);
  });
  const pre = $("#preSprite");
  if (pre) pre.innerHTML = pixSVG(ROCKET, ROCKET_P);
  const th = $("#themeIco");
  if (th) th.innerHTML = isDark() ? pixSVG(MOON_M, MOON_P) : pixSVG(SUN_M, SUN_P);
  const b = $("#railBuddy .b-in");
  if (b)
    b.innerHTML = `<span class="f f1">${pixSVG(BEEP_A, BEEP_P)}</span><span class="f f2">${pixSVG(BEEP_B, BEEP_P)}</span>`;
}

/* تیک عمومی تعویض فریم (۲فریمی‌ها) */
setInterval(() => {
  if (document.hidden || RM) return;
  $$('.sprite[data-frames="2"]').forEach((el) => el.classList.toggle("fr"));
}, 420);
export { pixSVG, drawMat, SPAL, SPRITES, IPAL, ICONS, ROCKET, ROCKET_P, BEEP_A, BEEP_B, BEEP_P, AST_A, AST_B, AST_STAND, AST_P, CHOM_C, CHOM_O, CHOM_P, GHOST_A, GHOST_B, HEART, HEART_P, SUN_M, SUN_P, MOON_M, MOON_P, injectSprites };