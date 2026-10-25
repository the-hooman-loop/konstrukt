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

/** Primitive ramps: referenced as {color.*}, never emitted themselves. */
export const PRIMITIVES = 'tokens/primitives.json';

/**
 * Deep-merge token objects in cascade order (later wins), then resolve
 * build-time references. `{a.b.c}` is replaced with the literal value of that
 * token path, looked up in the primitives plus the merged sources. `var(--x)`
 * references are left alone: they are runtime links between emitted tokens.
 */
export function mergeSources(sources) {
  const out = {};
  for (const src of sources) deepMerge(out, readJson(src));
  const pool = {};
  deepMerge(pool, readJson(PRIMITIVES));
  deepMerge(pool, out);
  return resolveRefs(out, pool);
}

function lookupPath(pool, path, seen = new Set()) {
  if (seen.has(path)) throw new Error(`Circular token reference: {${path}}`);
  seen.add(path);
  let node = pool;
  for (const key of path.split('.')) node = node?.[key];
  if (!isToken(node)) throw new Error(`Unresolved token reference: {${path}}`);
  const value = node.$value;
  const whole = typeof value === 'string' && value.match(/^\{([^}]+)\}$/);
  return whole ? lookupPath(pool, whole[1], seen) : value;
}

function resolveRefs(node, pool) {
  if (typeof node === 'string') {
    const whole = node.match(/^\{([^}]+)\}$/);
    if (whole) return lookupPath(pool, whole[1]);
    return node.replace(/\{([a-z0-9.-]+)\}/gi, (_, path) => String(lookupPath(pool, path)));
  }
  if (Array.isArray(node)) return node.map((n) => resolveRefs(n, pool));
  if (node && typeof node === 'object') {
    const out = {};
    for (const [key, value] of Object.entries(node)) out[key] = resolveRefs(value, pool);
    return out;
  }
  return node;
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
 * { name, value, type, deprecated? } where `name` is the CSS custom-property name
 * (path joined with "-", without the leading "--").
 */
export function flatten(tokenObj) {
  const out = [];
  walk(tokenObj, [], out);
  return out;
}

function walk(node, path, out) {
  if (isToken(node)) {
    const token = { name: path.join('-'), value: node.$value, type: node.$type || 'other' };
    if (node.$deprecated) token.deprecated = node.$deprecated;
    out.push(token);
    return;
  }
  for (const [key, value] of Object.entries(node)) {
    if (value && typeof value === 'object') walk(value, [...path, key], out);
  }
}

/** Resolve var(--x) references against a flat name->value map (for Swift/JSON). */
export function resolveValue(value, lookup, seen = new Set()) {
  if (value && typeof value === 'object') {
    const out = {};
    for (const [k, v] of Object.entries(value)) out[k] = resolveValue(v, lookup, new Set(seen));
    return out;
  }
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
