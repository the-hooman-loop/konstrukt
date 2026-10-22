# Konstrukt

[![verify](https://github.com/the-hooman-loop/konstrukt/actions/workflows/verify.yml/badge.svg)](https://github.com/the-hooman-loop/konstrukt/actions/workflows/verify.yml)
[![license](https://img.shields.io/badge/license-MIT-067F8A?style=flat-square)](LICENSE)

The Hooman Loop design system. JSON-first design tokens, generated into CSS,
Swift/SwiftUI, and a JSON manifest, with a self-contained documentation site.

Konstrukt is the single source of truth: edit tokens in `tokens/`, run the
build, and every surface — web apps, marketing sites, internal tools, and
native iOS — follows.

![Konstrukt landing page](assets/readme/hero.png)

Ten themes · 78 resolved tokens per theme · 3 output targets · 0px radius ·
0 shadows. Bauhaus / Swiss International: flat surfaces, square corners,
authority through typography rather than chrome.

## Ten themes, one token set

![Palette cycling through all ten themes](assets/readme/palettes.gif)

Every theme is the intersection of two orthogonal axes, set as attributes on
`<html>`: a **palette** (`atelier` · `courage` · `minimal` · `hl` · `blueprint`)
and a **mode** (`light` · `dark`). Five palettes × two modes, resolved at build
time into ten flat token sets. No runtime interpolation, no theme math in the
browser.

## Quick start

```bash
npm install
npm run build      # tokens/ -> dist/ (CSS, Swift, tokens.json) + docs/assets
npm run check      # parity gate vs the canonical snapshot
npm run docs       # serve the docs site on http://localhost:4340
```

## What it produces

| Output | Path | For |
|--------|------|-----|
| Themed CSS | `dist/css/konstrukt.css` | all web surfaces (palette × mode) |
| Components | `dist/css/base.css` | portable Konstrukt components |
| Theme runtime | `dist/css/theme.js` | `HLTheme` — sets mode/palette on `<html>` |
| Swift package | `dist/swift/Konstrukt/` | iOS / SwiftUI |
| Manifest | `dist/tokens.json` | tooling, design apps, AI agents |
| Docs site | `docs/` | reference + integration guides |

## Tokens

Every token is authored once, in W3C DTCG JSON, and its path becomes its CSS
custom property: `status.draft-bg` → `--status-draft-bg`. The reference page
reads the generated manifest, so what you see is what ships.

<img src="assets/readme/tokens.png" width="820" alt="Token reference: surfaces and text, accent and borders, status">

## Components

The portable component vocabulary: modules with 2px ink borders, status pills,
segmented filters, data tables, question lists. Square by default, no shadows,
teal reserved for the one primary action on a surface.

<img src="assets/readme/components.png" width="820" alt="Component reference">

## Text layer — proposal

Charts, annotations and CLI motion for channels that render characters instead
of pixels. Nine primitives, two encodings, and a linter that fails a build when
a chart lies about a number.

<img src="assets/readme/text-layer.png" width="900" alt="Konstrukt text layer one-pager">

This is a proposal, not part of the versioned contract. Read
[`proposals/text-layer/scope.md`](proposals/text-layer/scope.md) for the rules,
or run the reference renderer: `python3 scripts/text_layer_prototype.py`.

## Documentation

- Design system reference and live token explorer: `npm run docs`, or the
  published copy at [thehoomanloop.com/konstrukt](https://thehoomanloop.com/konstrukt).
- The full contract — token model, build, parity gate, consumption, and
  adoption status — is in [`DESIGN.md`](DESIGN.md).
- iOS integration: `docs/ios.html`.
- Deploying the docs: [`scripts/README-deploy.md`](scripts/README-deploy.md).

## Editing tokens

Author tokens in `tokens/` as W3C DTCG JSON. A token's path becomes its CSS
custom property (`status.draft-bg` → `--status-draft-bg`). Never edit anything
in `dist/` — it is generated. After editing, run `npm run build && npm run check`.

## Proposals

`proposals/` holds work that is under review and promises nothing. It has no
version, no gate, and no compatibility guarantee. When a proposal is stable it
is promoted into `tokens/` through the checklist in
[`CONTRIBUTING.md`](CONTRIBUTING.md), and only then does it ship.

## Contributing

Read [`CONTRIBUTING.md`](CONTRIBUTING.md) first. The short version: a new
output needs a gate, a new primitive needs a real consumer in the same pull
request, and a vendored copy carries a version stamp.

## License

MIT for the code and tokens. The Konstrukt name and marks are not covered by
the license. See [`LICENSE`](LICENSE).

---

Konstrukt is a project of The Hooman Loop.
