# Konstrukt

The Hooman Loop design system. JSON-first design tokens, generated into CSS,
Swift/SwiftUI, and a JSON manifest, with a self-contained documentation site.

Konstrukt is the single source of truth: edit tokens in `tokens/`, run the
build, and every surface — web apps, the marketing site, internal tools, and
native iOS — follows.

Public, version **1.1.0**. One open proposal: a
[text layer](proposals/text-layer/scope.md) for charts, annotations and CLI
motion, which is not part of the versioned contract yet.

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
