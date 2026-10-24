# Konstrukt — design system contract

Konstrukt is the single source of truth for design tokens across the Hooman
Loop ecosystem. Tokens are authored once as JSON and generated into CSS,
Swift/SwiftUI, a machine-readable JSON manifest, and a text/ASCII output
layer. Every surface — the portal, the marketing site, internal tools, native
iOS, and character-cell channels — consumes the same generated values.

## Aesthetic

Bauhaus / Swiss International Typographic Style: flat surfaces (`--shadow: none`),
square corners (`--radius: 0px`), Space Grotesk for display, Inter for body,
SF Mono for code. Authority through typography and a restrained palette, not
chrome.

## Two orthogonal axes

Every theme is the intersection of a **palette** and a **mode**, set as
attributes on `<html>`:

| Axis | Attribute | Values |
|------|-----------|--------|
| Palette | `data-palette` | `atelier` · `courage` · `minimal` · `hl` · `blueprint` |
| Mode | `data-mode` | `light` · `dark` |

`atelier` light is the `:root` default. Legacy aliases are preserved: the
palette name `sqdl` renders the same as `hl`, and `[data-theme="dark"]` aliases
`data-mode="dark"`.

## Source of truth

```
├── tokens/                      # AUTHOR HERE — W3C DTCG JSON
│   ├── global.json              # fonts, spacing, radius, transition, swatches
│   ├── semantic.json            # :root defaults (surfaces, text, accent, status…)
│   ├── text.json                # glyph ladders, column budgets, reserved marks
│   └── themes/                  # per-palette + per-mode overrides
├── build/                       # generator + parity / text gates
├── src/                         # base.css, theme.js, text.css, text renderer + linter
└── dist/                        # GENERATED — never hand-edit
    ├── css/konstrukt.css        # all palette × mode selector blocks
    ├── css/base.css             # portable components (.module, .badge, …)
    ├── css/theme.js             # HLTheme runtime
    ├── css/text.css             # pre.kt embed styles
    ├── swift/Konstrukt/         # Swift package
    ├── tokens.json              # resolved manifest, one entry per theme, plus text
    ├── text.json                # resolved text-layer spec
    └── text.py                  # self-contained Python renderer
```

Token naming maps directly to CSS custom properties: a token at path
`status.draft-bg` becomes `--status-draft-bg`. Edit JSON, then run the build.

## Build & verify

```bash
npm install        # first time
npm run build      # tokens/ -> dist/{css,swift,tokens.json,text.json,text.py} + docs/assets
npm run check      # parity gate vs build/canonical-tokens.css
npm run check:text # text-layer linter + golden board
npm run docs       # serve docs on http://localhost:4340
```

From the monorepo root:

```bash
make konstrukt-build   # build + parity check
make konstrukt-docs    # build + serve docs
make sync-tokens       # build + distribute CSS to every consumer
```

### Parity gate

`build/canonical-tokens.css` is a frozen snapshot of the original hand-authored
portal `tokens.css`, captured before the portal began consuming generated
output. `npm run check` confirms the generated CSS still matches it
value-for-value (selector by selector, declaration by declaration). Treat a
parity failure as either an intended token change (update the snapshot
deliberately) or a generator regression.

## Consuming Konstrukt

| Surface type | How to consume |
|--------------|----------------|
| Vanilla HTML | `<link rel="stylesheet" href=".../konstrukt.css">` + `base.css` + `<script src=".../theme.js">` |
| Astro / Vite / React | `@import '@hooman-loop/konstrukt/css';` or the synced `konstrukt.css` |
| iOS / SwiftUI | Add the `dist/swift/Konstrukt` package; read `@Environment(\.konstruktTheme)` (see `docs/ios.html`) |
| Tooling / AI | Read `dist/tokens.json` (resolved per theme, plus `text`) |
| Text / CLI | Vendor `dist/text.py`, or read `dist/text.json` for raw ladders |

`make sync-tokens` copies `dist/css/konstrukt.css` into each web consumer and,
for the portal, also `base.css` and `theme.js`. The portal's
`portal/css/tokens.css` is now a generated artifact — edit tokens here, not
there.

## Adoption status

Konstrukt is consumed at three levels of trust. The distinction matters because
only the first kind is verifiable from this repo.

| Surface kind | Tokens | Notes |
|---------|--------|-------|
| Marketing site (Astro) | generated | `src/styles/konstrukt.css` refreshed from `dist/` by a sync step. |
| Product portal | generated | `tokens.css`, `base.css`, `theme.js` synced from `dist/`. |
| Client sites | imported | their stylesheet imports the synced `konstrukt.css`. |
| Internal dashboards | synced | token file synced, but a runtime stylesheet may still inline a token subset. |
| Internal agent lanes | bridged | imports the synced `konstrukt.css` while keeping a legacy `--color-*` vocabulary. |
| Native iOS | generated | SwiftUI package built from `dist/swift/`. |

Legacy `--color-*` token names are deprecated in favor of the canonical names
above. Surfaces still on the old vocabulary keep working via their own `:root`
blocks until migrated.
