/**
 * Parity gate — confirm the generated CSS matches the canonical portal
 * tokens.css value-for-value (selector by selector, declaration by
 * declaration). Whitespace and declaration order are ignored; values are
 * compared exactly. Exits non-zero on any drift.
 */
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { projectRoot } from './lib.mjs';

const generated = resolve(projectRoot, 'dist/css/konstrukt.css');
// Default oracle is the committed snapshot of the original hand-authored
// portal tokens.css (captured before the portal began consuming generated
// output). Pass an explicit path to diff against any other stylesheet.
const canonical = process.argv[2] || resolve(projectRoot, 'build/canonical-tokens.css');

function parse(css) {
  const cleaned = css
    .replace(/\/\*[\s\S]*?\*\//g, '')
    .replace(/@import\s+url\([^)]*\)\s*;/g, '');
  const rules = new Map();
  const re = /([^{}]+)\{([^}]*)\}/g;
  let m;
  while ((m = re.exec(cleaned))) {
    const selectorKey = m[1]
      .split(',')
      .map((s) => s.trim())
      .filter(Boolean)
      .sort()
      .join(',');
    const decls = {};
    for (const decl of m[2].split(';')) {
      const idx = decl.indexOf(':');
      if (idx === -1) continue;
      const prop = decl.slice(0, idx).trim();
      const value = decl.slice(idx + 1).trim();
      if (prop) decls[prop] = value;
    }
    const existing = rules.get(selectorKey) || {};
    rules.set(selectorKey, { ...existing, ...decls });
  }
  return rules;
}

const gen = parse(readFileSync(generated, 'utf8'));
const can = parse(readFileSync(canonical, 'utf8'));

const problems = [];
for (const [selector, decls] of can) {
  if (!gen.has(selector)) {
    problems.push(`Missing selector: ${selector}`);
    continue;
  }
  const g = gen.get(selector);
  for (const [prop, value] of Object.entries(decls)) {
    if (!(prop in g)) problems.push(`${selector} -> missing ${prop}`);
    else if (g[prop] !== value)
      problems.push(`${selector} -> ${prop}: expected "${value}", got "${g[prop]}"`);
  }
  for (const prop of Object.keys(g)) {
    if (!(prop in decls)) problems.push(`${selector} -> extra ${prop}: "${g[prop]}"`);
  }
}
for (const selector of gen.keys()) {
  if (!can.has(selector)) problems.push(`Extra selector: ${selector}`);
}

if (problems.length) {
  console.error(`Parity check FAILED (${problems.length} differences):`);
  for (const p of problems) console.error(`  - ${p}`);
  process.exit(1);
}
console.log(`Parity check passed — generated CSS matches ${canonical} value-for-value.`);
