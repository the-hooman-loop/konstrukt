/**
 * Contrast gate — every foreground/background pair the components actually
 * render must meet WCAG 2.2 AA in every theme: 4.5:1 for text, 3:1 for
 * non-text UI (control outlines, focus rings, structural rules).
 * Reads the resolved manifest, so run `npm run build` first. Exits non-zero
 * on any failure.
 */
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { projectRoot } from './lib.mjs';

const TEXT = 4.5;
const UI = 3;

const feedback = ['success', 'warning', 'danger', 'info'];
const statuses = ['draft', 'review', 'complete', 'in-progress', 'launched'];
const categories = [1, 2, 3, 4, 5];

/** [foreground, background, minimum ratio, where it appears] */
const PAIRS = [
  ...['bg', 'bg-alt', 'surface'].flatMap((bg) => [
    ['text', bg, TEXT, 'body copy'],
    ['text-muted', bg, TEXT, 'meta, labels, table headers'],
    ['accent', bg, TEXT, 'links'],
    ['border', bg, UI, 'control outlines'],
    ['focus', bg, UI, 'focus ring'],
    ['ink', bg, UI, 'structural rules'],
  ]),
  ['accent', 'accent-soft', TEXT, 'selected button, review badge'],
  ['accent', 'accent-light', TEXT, 'accent-light panels'],
  ['on-accent', 'accent', TEXT, 'primary button'],
  ...feedback.flatMap((f) => [
    [f, `${f}-bg`, TEXT, 'alert'],
    [f, 'surface', TEXT, 'inline feedback text'],
  ]),
  ...statuses.map((s) => [`status-${s}`, `status-${s}-bg`, TEXT, 'status badge']),
  ...categories.map((c) => [`category-${c}`, `category-${c}-bg`, TEXT, 'category tag']),
  ['selection-fg', 'selection-bg', TEXT, 'text selection'],
];

function luminance(hex) {
  const h = hex.replace('#', '');
  const [r, g, b] = [0, 2, 4].map((i) => {
    const c = parseInt(h.slice(i, i + 2), 16) / 255;
    return c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
  });
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

export function contrast(a, b) {
  const [hi, lo] = [luminance(a), luminance(b)].sort((x, y) => y - x);
  return (hi + 0.05) / (lo + 0.05);
}

const manifest = JSON.parse(readFileSync(resolve(projectRoot, 'dist/tokens.json'), 'utf8'));
const failures = [];
let checked = 0;

for (const [theme, tokens] of Object.entries(manifest.themes)) {
  for (const [fg, bg, min, where] of PAIRS) {
    const f = tokens[fg]?.value;
    const b = tokens[bg]?.value;
    if (!/^#[0-9a-f]{6}$/i.test(f ?? '') || !/^#[0-9a-f]{6}$/i.test(b ?? '')) {
      failures.push(`${theme}: --${fg} on --${bg} is not a resolvable hex pair (${f} / ${b})`);
      continue;
    }
    checked++;
    const ratio = contrast(f, b);
    if (ratio < min) {
      failures.push(
        `${theme}: --${fg} ${f} on --${bg} ${b} = ${ratio.toFixed(2)}:1, needs ${min}:1 (${where})`
      );
    }
  }
}

if (failures.length) {
  console.error(`Contrast check FAILED (${failures.length} of ${checked} pairs):`);
  for (const f of failures) console.error(`  - ${f}`);
  process.exit(1);
}
console.log(`Contrast check passed — ${checked} pairs across ${Object.keys(manifest.themes).length} themes meet WCAG AA.`);
