/**
 * Konstrukt build — JSON tokens -> CSS, Swift, and a JSON manifest.
 *
 * CSS is produced with Style Dictionary: one build per selector block via a
 * custom `konstrukt/css` format, concatenated into a single stylesheet that
 * reproduces the canonical palette x mode cascade. Swift and JSON outputs are
 * derived from the same token files so every surface stays in lock-step.
 */
import { mkdtempSync, mkdirSync, readFileSync, writeFileSync, rmSync, cpSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { resolve, join } from 'node:path';
import StyleDictionary from 'style-dictionary';
import { cssBlocks, themes, semanticSources, palettes, legacyPalettes, fontImport } from './themes.mjs';
import { projectRoot, mergeSources, flatten, resolveValue, unwrapDtcg, readJson } from './lib.mjs';

const dist = resolve(projectRoot, 'dist');
const distCss = join(dist, 'css');
const distSwift = join(dist, 'swift', 'Konstrukt');

/**
 * A typography role becomes three properties: a `font` shorthand plus its
 * tracking and case, which the shorthand cannot carry.
 *   h1 { font: var(--type-display); letter-spacing: var(--type-display-tracking); }
 */
function typographyDecls(name, v) {
  return [
    [name, `${v.fontWeight} ${v.fontSize}/${v.lineHeight} ${v.fontFamily}`],
    [`${name}-tracking`, v.letterSpacing],
    [`${name}-transform`, v.textTransform],
  ];
}

StyleDictionary.registerFormat({
  name: 'konstrukt/css',
  format: ({ dictionary, options }) => {
    const { selector, prelude } = options;
    const lines = dictionary.allTokens.flatMap((token) => {
      const name = token.path.join('-');
      const value = token.$value ?? token.value;
      const decls = token.$type === 'typography' ? typographyDecls(name, value) : [[name, value]];
      const note = token.$deprecated ? ` /* deprecated: ${token.$deprecated} */` : '';
      return decls.map(([n, v]) => `  --${n}: ${v};${note}`);
    });
    if (prelude) lines.unshift(`  ${prelude}`);
    return `${selector} {\n${lines.join('\n')}\n}\n`;
  },
});

async function buildCss() {
  const tmp = mkdtempSync(join(tmpdir(), 'konstrukt-'));
  const blocks = [];
  for (const block of cssBlocks) {
    const sd = new StyleDictionary(
      {
        usesDtcg: true,
        tokens: mergeSources(block.sources),
        platforms: {
          css: {
            transforms: [],
            buildPath: `${tmp}/`,
            files: [
              {
                destination: `${block.key}.css`,
                format: 'konstrukt/css',
                options: { selector: block.selector, prelude: block.prelude },
              },
            ],
          },
        },
      },
      { verbosity: 'silent' }
    );
    await sd.buildAllPlatforms();
    blocks.push(readFileSync(join(tmp, `${block.key}.css`), 'utf8').trimEnd());
  }
  rmSync(tmp, { recursive: true, force: true });

  const header = [
    fontImport,
    '',
    '/**',
    ' * Konstrukt Design System — generated tokens. DO NOT EDIT BY HAND.',
    ' * Source: tokens/*.json — run `npm run build`.',
    ' *',
    ' * Aesthetic: Bauhaus / Swiss International Typographic Style.',
    ' * One palette (atelier), two modes, set on <html>:',
    ' *   data-mode : light | dark   (legacy alias [data-theme="dark"])',
    ` *   data-palette is accepted but ignored; ${legacyPalettes.join(', ')} render as atelier.`,
    ' */',
    '',
  ].join('\n');

  mkdirSync(distCss, { recursive: true });
  writeFileSync(join(distCss, 'konstrukt.css'), `${header}\n${blocks.join('\n\n')}\n`);
  return cssBlocks.length;
}

function kebabToCamel(name) {
  return name.replace(/-([a-z0-9])/g, (_, c) => c.toUpperCase());
}

function resolvedMap(sources) {
  const tokens = flatten(mergeSources(sources));
  const lookup = Object.fromEntries(tokens.map((t) => [t.name, t.value]));
  const out = {};
  for (const t of tokens) {
    out[t.name] = { value: resolveValue(t.value, lookup), type: t.type };
    if (t.deprecated) out[t.name].deprecated = t.deprecated;
  }
  return out;
}

function loadTextSpec() {
  return unwrapDtcg(readJson('tokens/text.json'));
}

function buildJsonManifest(textSpec) {
  const globals = resolvedMap(['tokens/global.json']);
  const resolved = {};
  for (const { palette, mode, sources } of themes) {
    resolved[`${palette}.${mode}`] = resolvedMap(sources);
  }
  const manifest = {
    name: 'konstrukt',
    version: readJson('package.json').version,
    description: 'The Hooman Loop design system — resolved design tokens.',
    generated: new Date().toISOString().slice(0, 10),
    palettes,
    legacyPalettes,
    modes: ['light', 'dark'],
    primitives: resolvedMap(['tokens/primitives.json']),
    global: globals,
    themes: resolved,
    text: textSpec,
  };
  mkdirSync(dist, { recursive: true });
  writeFileSync(join(dist, 'tokens.json'), `${JSON.stringify(manifest, null, 2)}\n`);
}

/**
 * Emit the text-layer spec and a self-contained Python renderer.
 * CSS and Swift outputs do not consume these tokens — they stay on the
 * pixel contract so the parity gate is unchanged.
 */
function buildTextLayer(textSpec) {
  const pkg = readJson('package.json');
  mkdirSync(dist, { recursive: true });
  mkdirSync(distCss, { recursive: true });

  writeFileSync(join(dist, 'text.json'), `${JSON.stringify(textSpec, null, 2)}\n`);

  const source = readFileSync(resolve(projectRoot, 'src/text/renderer.py'), 'utf8');
  if (!source.includes('BAKED_SPEC = None')) {
    throw new Error('src/text/renderer.py is missing `BAKED_SPEC = None`; cannot bake tokens.');
  }
  const baked = source.replace(
    'BAKED_SPEC = None',
    `BAKED_SPEC = json.loads(r'''${JSON.stringify(textSpec)}''')`
  );
  const header = [
    '#!/usr/bin/env python3',
    `# konstrukt-text v${pkg.version}  do not edit`,
    '# Generated by `npm run build` from tokens/text.json + src/text/renderer.py.',
    '',
  ].join('\n');
  // Drop the source shebang so the stamp is the first line.
  const body = baked.replace(/^#![^\n]*\n/, '');
  writeFileSync(join(dist, 'text.py'), `${header}${body}`);

  cpSync(resolve(projectRoot, 'src/text.css'), join(distCss, 'text.css'));
}

function firstFontFamily(value) {
  const first = String(value).split(',')[0].trim();
  return first.replace(/^["']|["']$/g, '');
}

function remToPoints(value) {
  const n = parseFloat(value);
  return String(value).endsWith('rem') ? n * 16 : n;
}

const SWIFT_WEIGHTS = { 400: 'regular', 500: 'medium', 600: 'semibold', 700: 'bold' };

function buildSwift() {
  // Color fields = semantic color tokens (shared across every theme).
  // Deprecated aliases become computed properties that forward to their target.
  const semantic = flatten(mergeSources(semanticSources)).filter((t) => t.type === 'color');
  const live = semantic.filter((t) => !t.deprecated);
  const colorNames = live.map((t) => t.name);
  const aliases = semantic
    .filter((t) => t.deprecated)
    .map((t) => {
      const target = String(t.value).match(/^var\(--([a-z0-9-]+)\)$/)?.[1];
      if (!target) return null;
      // Follow alias chains (badge-review -> status-review) to a stored field.
      const field = colorNames.includes(target)
        ? target
        : String(semantic.find((s) => s.name === target)?.value).match(/^var\(--([a-z0-9-]+)\)$/)?.[1];
      if (!colorNames.includes(field)) return null;
      return `    @available(*, deprecated, message: "${t.deprecated.replace(/"/g, '\\"')}")\n    var ${kebabToCamel(t.name)}: Color { ${kebabToCamel(field)} }`;
    })
    .filter(Boolean);

  const themeConsts = themes.map(({ palette, mode, sources }) => {
    const map = resolvedMap(sources);
    const args = colorNames
      .map((name) => `        ${kebabToCamel(name)}: Color(hex: "${map[name].value}")`)
      .join(',\n');
    return `    static let ${palette}${mode === 'dark' ? 'Dark' : 'Light'} = KonstruktTheme(\n${args}\n    )`;
  });

  const switchCases = themes
    .map(
      ({ palette, mode }) =>
        `        case (.${palette}, .${mode}): return ${palette}${mode === 'dark' ? 'Dark' : 'Light'}`
    )
    .join('\n');

  const fields = colorNames.map((name) => `    public let ${kebabToCamel(name)}: Color`).join('\n');
  const initArgs = colorNames.map((name) => `${kebabToCamel(name)}: Color`).join(', ');
  const initBody = colorNames
    .map((name) => `        self.${kebabToCamel(name)} = ${kebabToCamel(name)}`)
    .join('\n');

  // Global constants (palette/mode independent).
  const globals = resolvedMap(['tokens/global.json']);
  const spacing = Object.entries(globals)
    .filter(([n]) => n.startsWith('sp-'))
    .map(([n, v]) => `    public static let sp${n.slice(3)}: CGFloat = ${parseFloat(v.value)}`)
    .join('\n');
  const strokes = Object.entries(globals)
    .filter(([n]) => n.startsWith('stroke-'))
    .map(([n, v]) => `    public static let ${n.slice(7)}: CGFloat = ${parseFloat(v.value)}`)
    .join('\n');
  const fonts = [
    `    public static let display = "${firstFontFamily(globals['font-display'].value)}"`,
    `    public static let sans = "${firstFontFamily(globals['font-sans'].value)}"`,
    `    public static let mono = "${firstFontFamily(globals['font-mono'].value)}"`,
  ].join('\n');
  const typeStyles = Object.entries(globals)
    .filter(([, v]) => v.type === 'typography')
    .map(([n, { value: v }]) => {
      const name = kebabToCamel(n.slice(5));
      return [
        `    static let ${name} = KonstruktTextStyle(`,
        `        family: "${firstFontFamily(v.fontFamily)}",`,
        `        size: ${remToPoints(v.fontSize)},`,
        `        weight: .${SWIFT_WEIGHTS[v.fontWeight]},`,
        `        lineHeight: ${v.lineHeight},`,
        `        tracking: ${parseFloat(v.letterSpacing)},`,
        `        uppercase: ${v.textTransform === 'uppercase'}`,
        `    )`,
      ].join('\n');
    })
    .join('\n\n');
  const legacyCases = legacyPalettes
    .filter((p) => p !== 'sqdl')
    .map(
      (p) =>
        `    @available(*, deprecated, message: "Removed in 2.0.0; renders as .atelier.")\n    static var ${p}: KonstruktPalette { .atelier }`
    )
    .join('\n');

  const swift = `// Konstrukt Design System — generated Swift tokens. DO NOT EDIT BY HAND.
// Source: tokens/*.json — run \`npm run build\`.
//
// Bauhaus / Swiss International style. One palette, two modes.

import SwiftUI

public enum KonstruktPalette: String, CaseIterable, Sendable {
    case ${palettes.join(', ')}
}

public extension KonstruktPalette {
${legacyCases}
}

public enum KonstruktMode: String, CaseIterable, Sendable {
    case light, dark
}

public struct KonstruktTheme: Sendable, Equatable {
${fields}

    public init(${initArgs}) {
${initBody}
    }
}

public extension KonstruktTheme {
${aliases.join('\n\n')}
}

public extension KonstruktTheme {
    /// Resolve a theme for the given palette and mode.
    static func theme(palette: KonstruktPalette = .atelier, mode: KonstruktMode = .light) -> KonstruktTheme {
        switch (palette, mode) {
${switchCases}
        }
    }

${themeConsts.join('\n\n')}
}

/// 4px spacing grid.
public enum KonstruktSpacing {
${spacing}
}

/// Border widths: hairline, the 2px ink rule, and the 4px accent rail.
public enum KonstruktStroke {
${strokes}
}

public enum KonstruktRadius {
    public static let base: CGFloat = ${parseFloat(globals['radius'].value)}
}

/// Font family names. Register the fonts in your app bundle to use them.
public enum KonstruktFont {
${fonts}
}

/// A typography role: family, size in points, weight, line height as a
/// multiple of size, tracking in em, and case.
public struct KonstruktTextStyle: Sendable, Equatable {
    public let family: String
    public let size: CGFloat
    public let weight: Font.Weight
    public let lineHeight: CGFloat
    public let tracking: CGFloat
    public let uppercase: Bool

    public var font: Font { .custom(family, size: size).weight(weight) }
    /// Tracking in points, for \`.tracking(_:)\`.
    public var trackingPoints: CGFloat { tracking * size }
    /// Extra leading in points, for \`.lineSpacing(_:)\`.
    public var lineSpacing: CGFloat { max(0, (lineHeight - 1) * size) }
}

public extension KonstruktTextStyle {
${typeStyles}
}

public extension View {
    /// Apply a Konstrukt typography role: font, tracking, line spacing and case.
    @available(iOS 16.0, macOS 13.0, *)
    func konstruktTextStyle(_ style: KonstruktTextStyle) -> some View {
        font(style.font)
            .tracking(style.trackingPoints)
            .lineSpacing(style.lineSpacing)
            .textCase(style.uppercase ? .uppercase : nil)
    }
}

// MARK: - SwiftUI environment

public struct KonstruktThemeKey: EnvironmentKey {
    public static let defaultValue = KonstruktTheme.atelierLight
}

public extension EnvironmentValues {
    var konstruktTheme: KonstruktTheme {
        get { self[KonstruktThemeKey.self] }
        set { self[KonstruktThemeKey.self] = newValue }
    }
}

public extension View {
    /// Inject a Konstrukt theme into the environment for this subtree.
    func konstruktTheme(palette: KonstruktPalette = .atelier, mode: KonstruktMode = .light) -> some View {
        environment(\\.konstruktTheme, KonstruktTheme.theme(palette: palette, mode: mode))
    }
}

// MARK: - Color(hex:)

public extension Color {
    init(hex: String) {
        let cleaned = hex.trimmingCharacters(in: CharacterSet(charactersIn: "#"))
        var value: UInt64 = 0
        Scanner(string: cleaned).scanHexInt64(&value)
        let r, g, b, a: Double
        switch cleaned.count {
        case 8:
            r = Double((value & 0xFF00_0000) >> 24) / 255
            g = Double((value & 0x00FF_0000) >> 16) / 255
            b = Double((value & 0x0000_FF00) >> 8) / 255
            a = Double(value & 0x0000_00FF) / 255
        default:
            r = Double((value & 0xFF0000) >> 16) / 255
            g = Double((value & 0x00FF00) >> 8) / 255
            b = Double(value & 0x0000FF) / 255
            a = 1
        }
        self.init(.sRGB, red: r, green: g, blue: b, opacity: a)
    }
}
`;

  const pkg = `// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "Konstrukt",
    platforms: [.iOS(.v15), .macOS(.v12)],
    products: [
        .library(name: "Konstrukt", targets: ["Konstrukt"]),
    ],
    targets: [
        .target(name: "Konstrukt"),
    ]
)
`;

  const sourcesDir = join(distSwift, 'Sources', 'Konstrukt');
  mkdirSync(sourcesDir, { recursive: true });
  writeFileSync(join(distSwift, 'Package.swift'), pkg);
  writeFileSync(join(sourcesDir, 'Konstrukt.swift'), swift);
}

function copyStaticAssets() {
  mkdirSync(distCss, { recursive: true });
  cpSync(resolve(projectRoot, 'src', 'base.css'), join(distCss, 'base.css'));
  cpSync(resolve(projectRoot, 'src', 'theme.js'), join(distCss, 'theme.js'));
}

/** Mirror generated assets into docs/assets so the docs site is self-contained. */
function copyDocsAssets() {
  const docsAssets = resolve(projectRoot, 'docs', 'assets');
  mkdirSync(docsAssets, { recursive: true });
  cpSync(join(distCss, 'konstrukt.css'), join(docsAssets, 'konstrukt.css'));
  cpSync(join(distCss, 'base.css'), join(docsAssets, 'base.css'));
  cpSync(join(distCss, 'theme.js'), join(docsAssets, 'theme.js'));
  cpSync(join(distCss, 'text.css'), join(docsAssets, 'text.css'));
  cpSync(join(dist, 'tokens.json'), join(docsAssets, 'tokens.json'));
  cpSync(join(dist, 'text.json'), join(docsAssets, 'text.json'));
}

async function main() {
  rmSync(dist, { recursive: true, force: true });
  const textSpec = loadTextSpec();
  const blockCount = await buildCss();
  buildJsonManifest(textSpec);
  buildSwift();
  buildTextLayer(textSpec);
  copyStaticAssets();
  copyDocsAssets();
  console.log(`Konstrukt build complete:`);
  console.log(`  dist/css/konstrukt.css   (${blockCount} selector blocks)`);
  console.log(`  dist/css/base.css        (portable components)`);
  console.log(`  dist/css/theme.js        (HLTheme runtime)`);
  console.log(`  dist/css/text.css        (text-layer embed)`);
  console.log(`  dist/tokens.json         (${themes.length} resolved themes + text)`);
  console.log(`  dist/text.json           (text-layer spec)`);
  console.log(`  dist/text.py             (text-layer renderer)`);
  console.log(`  dist/swift/Konstrukt/    (Swift package)`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
