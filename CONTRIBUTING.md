# Contributing to Konstrukt

Konstrukt is a design system with consumers in three languages and at least
four repos. The point of this document is that **adding something is a fixed
sequence, not an act of taste**. Follow it and the system stays honest; skip a
step and a consumer drifts.

## The one rule that decides everything

There are two tiers, and the difference is not maturity, it is **evidence**.

| Tier | Lives in | Promises | Requires |
|---|---|---|---|
| Proposal | `proposals/<name>/` | nothing | a scope doc and a working prototype |
| Canon | `tokens/` + `src/` | a versioned contract | every gate below green |

A proposal exists so an unstable idea can be examined without the package
claiming to ship it. The text layer sat in `proposals/text-layer/` and moved
three rules in a single day of drawing posters. That is a proposal. Canon has
stopped moving.

**Promotion is the commit.** "Adding something to Konstrukt" means moving it
from the left column to the right one, in one pull request, with this checklist
complete.

## Promotion checklist

Nothing enters canon until all seven are true. The order matters: the gate
before the docs, the docs before the release.

1. **Token.** The new values live in `tokens/*.json` as W3C DTCG, not as
   literals in a consumer, not as a constant in a script. Glyphs, ladders,
   column budgets and scale ranges are design decisions and therefore tokens.
2. **Build output.** `npm run build` emits it, so every language gets it from
   source. Consumers never read `tokens/` directly.
3. **Gate.** A check that fails the build when the contract breaks:
   `npm run check` for token parity, `npm run check:text` for byte-identical
   golden renders across language outputs. **A new output without a gate is a
   new source of drift.**
4. **Lint.** Rules that can be mechanised are mechanised. A documented rule with
   no check is a preference, and preferences rot.
5. **Docs.** A page under `docs/` in the `components.html` anatomy: one section
   per primitive, a live demo rendered from the built output, a copy-ready
   snippet, and the rule stated as a rule. Register it in the nav.
6. **Consumer.** One real surface uses it in the same PR, and the PR body shows
   the before and after. **A primitive is not real until a surface consumes it.**
   This is the step people skip, and it is the only one that proves the contract
   is usable rather than merely describable.
7. **Release.** `CHANGELOG.md` entry, semver bump, tag. Consumers pin the tag.

## Version policy

Semver applies to the **token contract**, not to the repo's activity.

- **minor**: new tokens, new primitives, new output target. Adding the text
  layer is a minor.
- **patch**: generated-output fixes that do not change a token name or value.
- **major**: renaming or removing a token, changing a ladder's meaning, changing
  what a status word means. Anything that makes a consumer's render wrong
  without an error.

## Propagation

Consumers fall into three kinds, and each has one correct mechanism.

1. **Built from source** (site, pages): import the generated CSS at the pinned
   version. No copying.
2. **Vendored by copy** (standalone scripts, cron collectors, anything that
   cannot take an npm dependency): copy the generated file, and stamp the copy:
   ```python
   # konstrukt-text v1.2.0  sha256:3f9c…  do not edit
   ```
   A copy without a version stamp is indistinguishable from a fork.
3. **Hand-declared** (a token block pasted into a page's own stylesheet):
   tolerated only for throwaway artifacts, and registered in `consumers.json` so
   `npm run verify` can diff it against `dist` and report the first differing
   line. If it matters, it is kind 1.

## What never goes in canon

- A primitive with no consumer.
- A glyph ladder that exists only inside one script.
- A rule whose only enforcement is a sentence in a prompt.
- Anything whose spec lives in a slide, a Paper document or a chat message. The
  repo is the version of the truth; everything else is a derivative that must be
  regenerated from it.
