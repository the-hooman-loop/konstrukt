# Changelog

Semver applies to the token contract: token names, token values, and the
meaning of a rendered state. Repository activity on its own is not a release.

## Unreleased

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
