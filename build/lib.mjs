import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
export const projectRoot = resolve(here, '..');

export function readJson(relPath) {
  return JSON.parse(readFileSync(resolve(projectRoot, relPath), 'utf8'));
}

function isToken(node) {
  return node && typeof node === 'object' && '$value' in node;
}

/** Deep-merge token objects in cascade order (later wins). */
export function mergeSources(sources) {
  const out = {};
  for (const src of sources) deepMerge(out, readJson(src));
  return out;
}

function deepMerge(target, source) {
  for (const [key, value] of Object.entries(source)) {
    if (isToken(value)) {
      target[key] = value;
    } else if (value && typeof value === 'object') {
      target[key] = isToken(target[key]) ? {} : target[key] || {};
      deepMerge(target[key], value);
    } else {
      target[key] = value;
    }
  }
}

/**
 * Flatten a nested token object to an ordered list of
 * { name, value, type } where `name` is the CSS custom-property name
 * (path joined with "-", without the leading "--").
 */
export function flatten(tokenObj) {
  const out = [];
  walk(tokenObj, [], out);
  return out;
}

function walk(node, path, out) {
  if (isToken(node)) {
    out.push({ name: path.join('-'), value: node.$value, type: node.$type || 'other' });
    return;
  }
  for (const [key, value] of Object.entries(node)) {
    if (value && typeof value === 'object') walk(value, [...path, key], out);
  }
}

/** Resolve var(--x) references against a flat name->value map (for Swift/JSON). */
export function resolveValue(value, lookup, seen = new Set()) {
  if (typeof value !== 'string') return value;
  const match = value.match(/^var\(--([a-z0-9-]+)\)$/i);
  if (!match) return value;
  const ref = match[1];
  if (seen.has(ref) || !(ref in lookup)) return value;
  seen.add(ref);
  return resolveValue(lookup[ref], lookup, seen);
}

/** Strip W3C DTCG `{$type, $value}` wrappers, recursively. */
export function unwrapDtcg(node) {
  if (Array.isArray(node)) return node.map(unwrapDtcg);
  if (node && typeof node === 'object') {
    if ('$value' in node) return unwrapDtcg(node.$value);
    const out = {};
    for (const [key, value] of Object.entries(node)) out[key] = unwrapDtcg(value);
    return out;
  }
  return node;
}
