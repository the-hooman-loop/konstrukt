# Changelog

Semver applies to the token contract: token names, token values, and the
meaning of a rendered state. Repository activity on its own is not a release.

## Unreleased

### Proposal — text layer

Not part of the contract yet. See `proposals/text-layer/scope.md`.

- 14 rules for character-cell output: charts, annotations, CLI motion.
- 9 primitives: spark, hbar, grid, range, multi, annotate, kv, frame, ruler.
- Two encodings behind one ladder set: unicode and ascii.
- `scripts/text_lint.py`: an 11-check conformance gate with a self-test.

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
