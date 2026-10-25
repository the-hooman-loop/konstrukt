# AGENTS.md

Instructions for coding agents working in or consuming Konstrukt. The full
contract is [DESIGN.md](DESIGN.md) — read it before changing tokens, gates, or
outputs. This file is the short path in, not a second spec.

## What this is

Konstrukt is The Hooman Loop's public, MIT-licensed design system. Tokens are
authored once as W3C DTCG JSON and generated into CSS, Swift/SwiftUI, a
resolved JSON manifest, and a text/ASCII layer. Version 2.0.0 ships one
palette, `atelier`, in light and dark.

## Hard rules

- Square corners. `--radius: 0px`. Do not introduce border-radius.
- No shadows. `--shadow: none`. Elevation is borders and weight, never blur.
- Use tokens. Never hard-code hex values, radii, or shadows in consumer CSS,
  Swift, or docs. A token path is the CSS custom property:
  `status.draft-bg` → `--status-draft-bg`.
- One palette: `atelier`. Light and dark are selected with
  `data-mode="light"` or `data-mode="dark"` on `<html>`.
- `data-palette` is accepted and ignored. 1.x names (`hl`, `sqdl`, `courage`,
  `minimal`, `blueprint`) are aliases that render as atelier; they go away in
  3.0. `[data-theme="dark"]` still aliases `data-mode="dark"`.
- Contrast is gated. 80 foreground/background pairs must meet WCAG 2.2 AA
  (4.5:1 text, 3:1 controls) in both modes.

## Where things live

| Path | Role |
|------|------|
| `tokens/` | Author here — primitives, global, semantic, dark, deprecated, text |
| `src/` | `base.css`, `theme.js`, `text.css`, text renderer and linter |
| `build/` | Generator plus parity, contrast, and llms-full gates |
| `dist/` | Generated. Never hand-edit. Gitignored. |
| `docs/` | Static docs site, published to design.thehoomanloop.com |
| `proposals/` | Unstable. No version, no gate, no compatibility promise. |

Consumers never read `tokens/` directly. They consume `dist/`.

## Build and check

```bash
npm install
npm run build       # tokens/ → dist/{css,swift,tokens.json,text.json,text.py} + docs/assets
npm run check       # parity vs build/canonical-tokens.css + WCAG AA contrast
npm run check:text  # text-layer linter + golden board
npm run check:llms  # llms-full.txt matches sources; llms.txt links resolve
npm run snapshot    # accept an intended token change (commit the snapshot with it)
npm run docs        # http://localhost:4340
```

If you edit `DESIGN.md`, `README.md`, `docs/text.md`, `CONTRIBUTING.md`, or
this file, run `npm run build:llms` and commit the regenerated `llms-full.txt`.

A new output needs a gate. A new primitive needs a real consumer in the same
pull request. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Consuming tokens

| Surface | How |
|---------|-----|
| Vanilla HTML | `dist/css/konstrukt.css` + `base.css` + `theme.js` |
| Astro / Vite / React | `@import '@hooman-loop/konstrukt/css'` |
| iOS / SwiftUI | Add `dist/swift/Konstrukt`; read `@Environment(\.konstruktTheme)` |
| Tooling / AI | `dist/tokens.json` — `themes["atelier.light"]`, `themes["atelier.dark"]`, plus `text` |
| Text / CLI | Vendor `dist/text.py`, or read `dist/text.json` for raw ladders |

After a docs deploy, the resolved manifest is also at
`https://design.thehoomanloop.com/assets/tokens.json`.

## When to use the text layer

Use it for chat, CLI, SMS, logs, and other character-cell channels — not for
pixel UI. Nine primitives (`spark`, `hbar`, `grid`, `range`, `multi`,
`annotate`, `kv`, `frame`, `ruler`) live in `src/text/renderer.py` and ship as
`dist/text.py`. Glyph ladders and column budgets are tokens
(`tokens/text.json`). The spec is [docs/text.md](docs/text.md). Run
`npm run check:text` after changing any of that.

## Agent entry points

- [llms.txt](llms.txt) — curated index (also served at `/llms.txt` on the docs site)
- [llms-full.txt](llms-full.txt) — generated full docs
- [DESIGN.md](DESIGN.md) — the contract
