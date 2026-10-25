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

## One palette, two modes

Konstrukt 2.0 ships one palette, `atelier`, in two modes set on `<html>`:

| Attribute | Values |
|-----------|--------|
| `data-mode` | `light` (the `:root` default) · `dark` |
| `data-palette` | accepted and ignored |

The 1.x palettes (`hl`, `sqdl`, `courage`, `minimal`, `blueprint`) were cut in
2.0.0. `theme.js` and the Swift package normalize those names to `atelier`, so
stored preferences and old call sites keep rendering. `[data-theme="dark"]`
still aliases `data-mode="dark"`.

## Token layers

| Layer | File | Emitted? | Referenced as |
|-------|------|----------|---------------|
| Primitives | `tokens/primitives.json` | no | `{color.teal.700}`, resolved at build time |
| Global | `tokens/global.json` | yes | fonts, type scale and roles, spacing, strokes, radius |
| Semantic | `tokens/semantic.json` | yes | light-mode roles; may link to each other with `var(--x)` |
| Dark | `tokens/themes/dark.json` | yes | overrides only the roles that differ |
| Deprecated | `tokens/deprecated.json` | yes | 1.x names as `var()` aliases, removed in 3.0.0 |

Semantic roles: surfaces (`bg`, `bg-alt`, `surface`), type (`text`,
`text-muted`), structure (`ink`, `border`, `border-light`), accent (`accent`,
`accent-soft`, `accent-light`, `on-accent`, `focus`), feedback (`success`,
`warning`, `danger`, `info`, each with `-bg`), `status-*` (which link to the
feedback roles), `category-1` to `category-5`, and selection.

Konstrukt does not know product vocabulary. Segments, invoice states and
timelines are mapped onto `category-*` and feedback roles in the product's own
stylesheet.

## Source of truth

```
├── tokens/                      # AUTHOR HERE — W3C DTCG JSON
│   ├── primitives.json          # raw color ramps, referenced, never emitted
│   ├── global.json              # fonts, type scale + roles, spacing, strokes, radius
│   ├── semantic.json            # :root light roles (surfaces, text, accent, feedback…)
│   ├── deprecated.json          # 1.x aliases, removed in 3.0.0
│   ├── text.json                # glyph ladders, column budgets, reserved marks
│   └── themes/dark.json         # dark-mode overrides
├── build/                       # generator + parity / contrast / text gates
├── src/                         # base.css, theme.js, text.css, text renderer + linter
└── dist/                        # GENERATED — never hand-edit
    ├── css/konstrukt.css        # :root (light) + dark selector blocks
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
npm run check      # parity vs build/canonical-tokens.css + WCAG AA contrast
npm run snapshot   # rebuild and accept the output as the new snapshot
npm run check:text # text-layer linter + golden board
npm run check:llms # llms-full.txt freshness + llms.txt link check
npm run build:llms # regenerate llms-full.txt from the contract docs
npm run docs       # serve docs on http://localhost:4340
```

From the monorepo root:

```bash
make konstrukt-build   # build + parity check
make konstrukt-docs    # build + serve docs
make sync-tokens       # build + distribute CSS to every consumer
```

### Parity gate

`build/canonical-tokens.css` is the committed snapshot of the generated CSS.
`npm run check:parity` confirms the build still matches it value-for-value
(selector by selector, declaration by declaration). A failure is either a
generator regression or an intended token change. For the latter, run
`npm run snapshot` and commit the snapshot diff with the token change, so the
reviewer sees exactly which custom properties moved.

Through 1.x the snapshot was the original hand-authored portal `tokens.css`.
It was regenerated in 2.0.0, when the token model changed.

### Contrast gate

`npm run check:contrast` checks every foreground/background pair the
components render, in both modes, against WCAG 2.2 AA: 4.5:1 for text, 3:1 for
control outlines, focus rings and structural rules. The pairs are listed in
`build/check-contrast.mjs`. A new role that renders text needs a row there.

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
