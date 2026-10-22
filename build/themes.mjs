/**
 * Konstrukt theme matrix.
 *
 * Each CSS block is generated from an explicit set of token files and a
 * selector. The matrix mirrors the canonical cascade:
 *   :root (atelier light)  ->  [data-palette="x"]  ->  [data-mode="dark"]
 *   ->  [data-palette="x"][data-mode="dark"]
 *
 * `swiftThemes` lists the resolved (palette, mode) combinations the Swift
 * package exposes, composed by layering the same files in cascade order.
 */

const G = 'tokens/global.json';
const S = 'tokens/semantic.json';
const t = (name) => `tokens/themes/${name}`;

/** Ordered list of CSS selector blocks emitted into konstrukt.css. */
export const cssBlocks = [
  {
    key: 'root',
    selector: ':root',
    prelude: 'color-scheme: light dark;',
    sources: [G, S],
  },
  {
    key: 'palette-blueprint',
    selector: '[data-palette="blueprint"]',
    sources: [t('blueprint.light.json')],
  },
  {
    key: 'palette-courage',
    selector: '[data-palette="courage"]',
    sources: [t('courage.light.json')],
  },
  {
    key: 'palette-minimal',
    selector: '[data-palette="minimal"]',
    sources: [t('minimal.light.json')],
  },
  {
    key: 'palette-hl',
    selector: '[data-palette="hl"],\n[data-palette="sqdl"]',
    sources: [t('hl.light.json')],
  },
  {
    key: 'mode-dark',
    selector: '[data-mode="dark"],\n[data-theme="dark"]',
    sources: [t('dark.json')],
  },
  {
    key: 'blueprint-dark',
    selector:
      '[data-palette="blueprint"][data-mode="dark"],\n[data-palette="blueprint"][data-theme="dark"]',
    sources: [t('blueprint.dark.json')],
  },
  {
    key: 'courage-dark',
    selector:
      '[data-palette="courage"][data-mode="dark"],\n[data-palette="courage"][data-theme="dark"]',
    sources: [t('courage.dark.json')],
  },
  {
    key: 'minimal-dark',
    selector:
      '[data-palette="minimal"][data-mode="dark"],\n[data-palette="minimal"][data-theme="dark"]',
    sources: [t('minimal.dark.json')],
  },
  {
    key: 'hl-dark',
    selector:
      '[data-palette="hl"][data-mode="dark"],\n[data-palette="hl"][data-theme="dark"],\n[data-palette="sqdl"][data-mode="dark"],\n[data-palette="sqdl"][data-theme="dark"]',
    sources: [t('hl.dark.json')],
  },
];

/** Resolved (palette, mode) combinations for Swift + JSON manifest. */
export const swiftThemes = [
  { palette: 'atelier', mode: 'light', sources: [G, S] },
  { palette: 'atelier', mode: 'dark', sources: [G, S, t('dark.json')] },
  { palette: 'blueprint', mode: 'light', sources: [G, S, t('blueprint.light.json')] },
  {
    palette: 'blueprint',
    mode: 'dark',
    sources: [G, S, t('blueprint.light.json'), t('dark.json'), t('blueprint.dark.json')],
  },
  { palette: 'courage', mode: 'light', sources: [G, S, t('courage.light.json')] },
  {
    palette: 'courage',
    mode: 'dark',
    sources: [G, S, t('courage.light.json'), t('dark.json'), t('courage.dark.json')],
  },
  { palette: 'minimal', mode: 'light', sources: [G, S, t('minimal.light.json')] },
  {
    palette: 'minimal',
    mode: 'dark',
    sources: [G, S, t('minimal.light.json'), t('dark.json'), t('minimal.dark.json')],
  },
  { palette: 'hl', mode: 'light', sources: [G, S, t('hl.light.json')] },
  {
    palette: 'hl',
    mode: 'dark',
    sources: [G, S, t('hl.light.json'), t('dark.json'), t('hl.dark.json')],
  },
];

export const palettes = ['atelier', 'courage', 'minimal', 'hl', 'blueprint'];
export const fontImport =
  "@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500&display=swap');";
