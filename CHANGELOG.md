# Changelog

Semver applies to the token contract: token names, token values, and the
meaning of a rendered state. Repository activity on its own is not a release.

## Unreleased

**Added**

- `llms.txt` and generated `llms-full.txt` so agents can discover the contract,
  token sources, and how to build the outputs. `npm run build:llms` regenerates
  the full file; `npm run check:llms` (run in CI) fails if it drifts or if an
  `llms.txt` link points at a missing file.
- `AGENTS.md` with working rules for coding agents in or consuming this repo.
- The docs build copies `llms.txt` and `llms-full.txt` to the `docs/` root
  (harmless for `npm run docs` and an optional Pages deploy).

## 2.0.0

One palette, a layered token model, typography as tokens, and a contrast gate.
This is a major release because palettes are removed and token values change.
Every 1.x token name still resolves through a deprecated alias.

**Breaking**

- Palettes cut from five to one. `atelier` remains; `hl`, `sqdl`, `courage`,
  `minimal` and `blueprint` are gone. `theme.js` normalizes those names to
  `atelier` and Swift keeps `.hl`, `.courage`, `.minimal` and `.blueprint` as
  deprecated aliases, so nothing fails to compile or parse, but surfaces on
  those palettes now render as atelier.
- The `swatch-*` tokens and `KonstruktSwatch` are removed along with the
  palette switcher.
- Values changed to pass WCAG AA:
  - `accent` light `#067F8A` → `#057079`. The old teal was 4.35:1 on `bg` and
    3.73:1 on `accent-soft`.
  - `status-draft` `#7A7A7A` → `#5C5C58` on `#ECEAE4`. It was 3.69:1.
  - Dark `border` `#4D4D49` → `#74746E`. It was 1.96:1 on `surface`.
- Status and category colors moved off stock Tailwind values onto a Bauhaus
  ramp (green, ochre, yellow, blue, red, violet) in `tokens/primitives.json`.

**Added**

- `tokens/primitives.json`: raw ramps referenced as `{color.teal.700}`,
  resolved at build time and never emitted.
- Feedback roles: `success`, `warning`, `danger`, `info`, each with `-bg`.
  Plus `on-accent` and `focus`.
- `category-1` to `category-5`: generic categorical slots.
- Type tokens: `--type-size-*`, `--type-weight-*`, `--type-tracking-*`,
  `--type-leading-*`, and eight roles emitted as `--type-<role>` font shorthands
  with `-tracking` and `-transform`. Swift gets `KonstruktTextStyle` and
  `.konstruktTextStyle(_:)`.
- Stroke tokens: `--stroke-hairline`, `--stroke-rule`, `--stroke-rail`, and
  `KonstruktStroke` in Swift.
- Components: `.btn-primary`, `.field` / `.input`, `.alert-*`, `.tag-1`
  to `.tag-5`. Focus rings use `--focus`.
- `npm run check:contrast`: 80 foreground/background pairs across both modes
  checked against WCAG 2.2 AA. It is part of `npm run check` and CI.
- `npm run snapshot` to accept an intended token change.

**Changed**

- `base.css` uses type roles and stroke tokens instead of literals.
- Status tokens link to feedback roles (`status-complete: var(--success)`), so
  dark mode no longer repeats them.
- The parity snapshot is now the generated 2.0.0 output, not the
  hand-authored 1.x portal stylesheet.
- Inter 600 is added to the font import; it was used but not loaded.

**Deprecated** (aliases in `tokens/deprecated.json`, removed in 3.0.0)

- Duplicates: `card` → `surface`, `muted` → `text-muted`, `done` →
  `success`, `badge-*` → `status-*`, `tag-*-text` → `category-*`.
- Product vocabulary: `tag-builders/operators/learners` → `category-1/2/3`,
  `beachhead` → `category-4`. `revenue-*`, `invoice-*` and `timeline-*` map to
  feedback roles and should move into the consuming product.

## 1.2.0

The text layer is now part of the versioned contract.

- `tokens/text.json`: glyph ladders, column budgets, cell counts, reserved
  marks. Two encodings (`unicode`, `ascii`) behind one ladder set.
- `npm run build` emits `dist/text.json`, `dist/text.py`, `dist/css/text.css`,
  and a `text` block on `dist/tokens.json`. Existing CSS, Swift and colour
  token outputs are unchanged.
- Nine primitives in the Python renderer: spark, hbar, grid, range, multi,
  annotate, kv, frame, ruler.
- `src/text/lint.py`: an 11-check conformance gate with a self-test.
- `npm run check:text`: linter, golden board, generated-renderer identity.
- Spec at `docs/text.md`. Review sheet at `docs/text-review.html`.

## 1.1.0

The version this repository starts at. It is the state of the design system as
extracted from the monorepo it grew up in, published as its own repository.

- JSON-first tokens in `tokens/` (W3C DTCG) as the single source of truth.
- Five palettes (`atelier`, `courage`, `minimal`, `hl`, `blueprint`) × two modes,
  resolved into 10 themes and 78 tokens per theme.
- Generated outputs: themed CSS, portable component CSS, the `HLTheme` runtime,
  a SwiftUI package, and a JSON manifest.
- Parity gate (`npm run check`) that fails the build when generated CSS drifts
  from the canonical snapshot.
- Self-contained docs site with a live token explorer and a component reference.
