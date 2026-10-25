/**
 * Konstrukt theme matrix.
 *
 * One palette (atelier), two modes. The cascade is:
 *   :root (light: global + semantic + deprecated aliases)  ->  [data-mode="dark"]
 *
 * Status tokens and deprecated aliases are var() references, so the dark
 * block only overrides the roles whose values differ.
 *
 * `themes` lists the resolved combinations the Swift package and JSON
 * manifest expose, composed by layering the same files in cascade order.
 */

const G = 'tokens/global.json';
const S = 'tokens/semantic.json';
const DEP = 'tokens/deprecated.json';
const DARK = 'tokens/themes/dark.json';

/** Ordered list of CSS selector blocks emitted into konstrukt.css. */
export const cssBlocks = [
  {
    key: 'root',
    selector: ':root',
    prelude: 'color-scheme: light dark;',
    sources: [G, S, DEP],
  },
  {
    key: 'mode-dark',
    selector: '[data-mode="dark"],\n[data-theme="dark"]',
    sources: [DARK],
  },
];

/** Resolved (palette, mode) combinations for Swift + JSON manifest. */
export const themes = [
  { palette: 'atelier', mode: 'light', sources: [G, S, DEP] },
  { palette: 'atelier', mode: 'dark', sources: [G, S, DEP, DARK] },
];

export const semanticSources = [S, DEP];
export const palettes = ['atelier'];
/** Palette names removed in 2.0.0. They still parse and render as atelier. */
export const legacyPalettes = ['hl', 'sqdl', 'courage', 'minimal', 'blueprint'];
export const fontImport =
  "@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap');";
