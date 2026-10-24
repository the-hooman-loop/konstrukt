# Konstrukt · Text — spec

Status: shipped in 1.2.0. Part of the versioned contract.

Artifacts:
- `tokens/text.json` — glyph ladders, column budgets, cell counts, reserved marks
- `src/text/renderer.py` — reference renderer (source)
- `src/text/lint.py` — conformance linter, `--self-test` proves 11 of 11 checks
- `dist/text.json` — resolved spec, emitted by `npm run build`
- `dist/text.py` — self-contained renderer for vendoring, baked from the tokens
- `dist/css/text.css` — `pre.kt` embed styles for a Konstrukt page
- `dist/tokens.json` — includes a top-level `text` block
- `scripts/text_board_page.py` — builds the review sheet as a Konstrukt HTML page

## 1. The gap

Konstrukt is a *rendered surface* system. Its colour tokens are pixels: colour,
spacing, radius, fonts. Every artifact that leaves the pixel world used to
invent its own grammar.

- Briefing scripts held `SPARK_GLYPHS = "▁▂▃▄▅▆▇█"`, a hand-rolled
  `sparkline()`, and a 16-point compass spelled out as a tuple.
- The eight-column contract that makes that chart readable lived in a `wanted`
  set in the collector, not in the primitive. Hand the same primitive fifteen
  hourly points and it renders 54 columns and nothing complains.
- CLI status output, progress and spinners were written inline wherever needed.
- The prompt that consumed it carried a paragraph of prose explaining how to
  read the chart, because the chart had no spec to point at.

That is one working renderer. The drift risk is the second one: a new agent
writes a 7-level ladder, or `#` bars beside `█` bars, or carets under the wrong
column, and nothing catches it because there is no token, no reference, no test.

Text is not a smaller web surface. It has one resolution axis, a fixed cell, and
a channel that may refuse colour. What transfers is not pixels, it is the
authority structure: hard edges, mono metadata, one accent, status words.

## 2. The translation table

This is the design argument. Everything else follows from it.

| Konstrukt (pixels) | Konstrukt · Text (cells) |
|---|---|
| `--radius: 0` | square corners only: `┌ ┐ └ ┘`, never `╭ ╮` |
| `--border` 2px ink | heavy box drawing `┏ ┓ ┗ ┛ ━ ┃` for a block frame |
| `--border-light` | single `┌ ─ │` for rules inside a block |
| `.module-head` (1fr auto) | first line: `LABEL` left, meta right-aligned to budget |
| `.micro-label` mono uppercase | `LABEL` uppercase, two spaces, no colon |
| `.row` (1fr auto) | label padded, value right-aligned, numerics right-justified |
| `.pill` | `[NORMAL]` `[WATCH]` `[VET]` |
| `.progress-fill` | fixed 8-cell ladder `████░░░░` |
| `font-variant-numeric: tabular-nums` | automatic: the cell grid is tabular |
| `--accent` teal | ANSI / HTML colour where the channel has it, never alone |
| `--text-muted` | lowercase, or `·` separators |
| `.status-strip` | `──` rule plus one KPI line |
| `.page-header` | `┏━` frame, kicker uppercase, status pill right |

Two things do **not** transfer and must be replaced, not scaled:

- **Type scale.** There is no 12/14/18/32 in a chat message. Hierarchy is
  carried by case, position and the frame, and by nothing else.
- **Weight.** Bold is unreliable across channels: it survives Markdown, not
  plain text, not a pasted log. Never encode meaning in weight.

## 3. One new axis: encoding

Konstrukt has palette × mode. The text layer adds a third, orthogonal axis:

| Axis | Values | Meaning |
|---|---|---|
| `encoding` | `unicode` (default) · `ascii` | same ladder positions, two renderings |

`unicode` uses block and box glyphs. `ascii` maps every position onto
`. : - = + * # @`, `- = # @` and `+ - | =`, for SMS, some email clients, log
files, and terminals with a broken font. Same shape, degraded resolution, never
a different language.

Corollary: **ASCII illustration is out of scope.** Box drawing and block
elements are data glyphs. Cat faces made of slashes are a different craft with
no data contract. The layer owns data marks, not pictures.

## 4. Tokens

Authored in `tokens/text.json`, emitted by `npm run build` as `dist/text.json`
and as the `text` block on `dist/tokens.json`. Consumers never read `tokens/`
directly.

```json
{
  "column": { "phone": 34, "chat": 44, "terminal": 78 },
  "cells": { "spark": 8, "hbar": 8, "range": 16, "multi": 12 },
  "glyph": {
    "unicode": {
      "spark8": "▁▂▃▄▅▆▇█",
      "bar4": "░▒▓█",
      "hbar": { "on": "█", "off": "░" },
      "box-light": { "tl": "┌", "tr": "┐", "bl": "└", "br": "┘", "h": "─", "v": "│" },
      "box-ink":   { "tl": "┏", "tr": "┓", "bl": "┗", "br": "┛", "h": "━", "v": "┃" },
      "mark": { "caret": "▲", "rule": "─", "dot": "·", "dot-on": "●", "pointer": "›" },
      "spin": "▘▝▗▖"
    },
    "ascii": { "...": "same keys, ascii values" }
  },
  "scale": { "percent": { "min": 0, "max": 100 } }
}
```

Glyph ladders are tokens because they are the thing that drifts. A ladder is
a design decision (how many levels before it reads as noise), not a string
literal inside a cron script.

## 5. Nine primitives

Closed set. Anything else is composition. Implemented in `src/text/renderer.py`
and baked into `dist/text.py`.

1. **spark** — one row, N columns, self-normalised curve, with sampling inside
   the primitive so a caller cannot widen it by accident.
2. **hbar** — fixed-scale horizontal bar, 8 or 16 cells, magnitude right-aligned.
3. **grid** — N by M cell matrix on a 4-step ladder, for patterns over time.
4. **range** — a span with the current value marked inside it, for a sleep
   window or a price band where the range matters as much as the point.
5. **multi** — small multiples sharing one scale, so rows are comparable.
6. **annotate** — caret plus label under a specific column of the row above.
7. **kv** — key, dot leaders, value. The text form of `.row-meta`.
8. **frame** — a Konstrukt module in text: heavy frame, head line with meta
   right-aligned, body rows, status pill.
9. **ruler** — a measuring probe, not a chart. See R2.

CLI adds two atoms, which are motion rather than data:

- **spin** — four-frame ladder `▘ ▝ ▗ ▖`, drawn from the same Unicode block as
  the data ladder, so any terminal that can draw a chart can draw the spinner.
  ASCII fallback `| / - \`. Fixed duration per frame, resolved final state.
- **progress** — determinate, 8 cells, count beside it. Never animate a number.

Braille spinners (`⠋⠙⠹⠸`) were the first choice and were rejected: the braille
block is missing from several client fonts and renders as solid tofu, which is
worse than no spinner. Motion borrows glyphs the reader has already proved the
channel can render.

## 6. Rules

R1. **The cell is the pixel.** Align by column index. Never tabs, never
    proportional-font assumptions, pad with spaces, right-justify numerics.

R2. **Width is a contract, and it ships with a measuring device.** Every
    renderer takes a budget from `text.column.<channel>` and truncates with `…`;
    a chart never wraps. Because the real budget depends on the client's font
    and cannot be asserted from a build machine, the system also ships `ruler`:
    paste it into a channel once, and if it comes back ragged, that channel is
    proportional and charts must live inside a code block there.

R3. **Shape is not magnitude.** A self-normalised sparkline must carry its real
    numbers on the same line (`▂▁▃▅▆█▇▅ temp 56→72°`). A bounded domain must pin
    its scale (percent 0-100), so a 9% bar cannot render as a full bar.

R4. **Widen flat ranges.** If the spread is below the minimum, widen it, or a
    two-degree drift renders as mountains.

R5. **One row, one variable.** Two differently scaled series on one line need a
    label per series. Two series sharing a scale share a line, and `multi`
    exists so several rows can share one.

R6. **Absence is signal.** No row when the data is noise. Never a placeholder,
    never an apology for the missing row. A blank cell in a grid is absence, not
    zero, so rows rstrip.

R7. **Colour is never load-bearing.** Every state must be readable in plain
    text. ANSI is a second channel, applied after the shape already says it.

R8. **Emoji are section labels, never data.** `📅 agenda` is fine. Temperature
    encoded as emoji is not.

R9. **Annotate in place.** Caret directly under the column, label under the
    caret, one line, no legend that requires counting. The caret is anchored to
    its column and never moves; the label slides left at the right edge so an
    annotation cannot push a clean block over budget. Derive the caret column
    from the rendered string, because hand-counting is how carets drift.

R10. **Animation resolves.** Every frame ladder ends in a terminal state. No
     animation on numbers. Reduced motion means printing only the resolved frame.

R11. **No mark carries two meanings.** A glyph already spent on one meaning is
     not available for another, because the reader has learned the first one.

     | Mark | Already means |
     |---|---|
     | `↑` `↓` | high / low temperature, or increase / decrease |
     | `▲` | caret: points at the annotated column |
     | `›` | list lead-in |
     | `·` | separator, or idle state |
     | `●` | present / active |
     | `[NORMAL]` | status pill |
     | `▁▂▃▄▅▆▇█` | data ladder: height means magnitude |
     | `▘▝▗▖` | motion only, never a value |

     The live collision is wind: weather widgets spend the arrows on high/low,
     so `↑` next to a wind reading parses as a temperature trend. Wind is
     spelled cardinal (`SSW`), never drawn.

R12. **The ladder is a silhouette, not countable columns.** Adjacent block
     glyphs touch in a monospace font, so an eight-level spark reads as a filled
     profile. That is correct for a trend and wrong for anything where the
     reader must count individual columns. Countable quantities use `hbar` or
     `grid`.

R13. **Eight levels need vertical room.** The same ladder rendered inside a
     13px line box collapses into a silhouette, because the whole scale is being
     drawn in ten pixels of height. Roughly 16px of line box is the floor for
     eight levels. Below that, drop to five levels or use `hbar`, which encodes
     magnitude in width and survives any size.

R14. **A rule without a check is a preference.** Every rule above that can be
     mechanised is mechanised in `src/text/lint.py` and runs in the gate.

## 7. Enforcement

`python3 src/text/lint.py` (or `scripts/text_lint.py`) judges a rendered block
and exits nonzero. Eleven checks:

| Id | Catches |
|---|---|
| T1 | line wider than the column budget |
| T2 | tab characters |
| T3 | trailing whitespace (invisible, poisons golden diffs) |
| T4 | bar ladder and spark ladder mixed in one line |
| T5 | a curve with no number on the line |
| T6 | bar length contradicts the percentage beside it |
| T7 | caret points past its row, or at whitespace |
| T8 | frame lines that do not close |
| T9 | emoji used as a data mark |
| T10 | `↑` `↓` away from a number |
| T11 | two series on one line with no label for either |

`--self-test` lints a block containing one deliberate defect per rule and
asserts 11 of 11 are caught, so the linter itself cannot rot silently.

The point is not tidiness. T6 is a truth check: a bar that says three cells and
a label that says 80% is a chart lying about a number. T5 is the same failure
in the other direction, a shape with nothing to anchor it.

Applied to a live weather chart, honestly:

```
wet day, live path        38 cols   clean
same chart, 15 raw hours  54 cols   T1 over budget
```

The shipped primitive pre-samples to eight points. A caller that bypasses it
and hands raw hourly data still renders 54 columns; the linter catches that as
T1. That is the class of bug the token plus the gate exist to prevent.

`npm run check:text` runs the self-test, lints the reference board in both
encodings, and diffs the board against `build/canonical-text-board.txt`. After
`npm run build` it also requires `dist/text.py` to render byte-identical to the
source renderer.

## 8. Outputs

Consumers are standalone Python scripts and shell tools that cannot take an npm
dependency, so the build emits a vendored runtime plus the raw spec:

| Output | Consumer |
|---|---|
| `dist/text.py` | cron collectors, briefings, mini CLI tools (vendored by copy) |
| `dist/text.json` | anything needing raw ladders without the renderer |
| `dist/tokens.json` `text` block | same spec, next to the colour manifest |
| `dist/css/text.css` | `pre.kt` styling so a text block sits in a Konstrukt page |

Stamp a vendored copy:

```python
# konstrukt-text v1.2.0  sha256:3f9c…  do not edit
```

A copy without a version stamp is indistinguishable from a fork.

Gates:

```
npm run check       # colour parity
npm run check:text  # linter + golden board + generated renderer
python3 src/text/lint.py --file <rendered> --budget 44
```

There is no JavaScript renderer and no Swift text output in this release. The
Python renderer is the supported implementation.

## 9. Still to do

These are follow-ups, not part of 1.2.0:

- A live `docs/text.html` demo page driven from a `dist/text.js` renderer, with
  one section per primitive in the `components.html` anatomy.
- Retrofit of live consumers (morning brief, weekly review, and the rest of
  the table below) so they vendor `dist/text.py` and drop local glyph literals.
- Optional Swift output for terminal tools on the mini.
- Measured column budgets (see open questions).

## 10. Migration targets

Where the grammar pays for itself, in order of reach:

| Surface | Primitives | Why |
|---|---|---|
| Morning brief | spark, annotate, frame, kv | the weather chart already ships; it is the first consumer |
| Fitness Sunday programming | hbar, grid, multi | adherence is a pattern over weeks, not a sentence |
| Weekly review | kv, hbar, frame | counts and ratios in aligned columns |
| Usage digest | spark, hbar | model usage is a time series with a ceiling |
| Workday start reminder | kv, pill | agenda and priorities with mono metadata |
| Workspace dashboard | grid, hbar | already Konstrukt in HTML, same grammar in text |
| Job pipeline | kv, hbar | stage counts, not prose |

## 11. Out of scope

- Image charts, and anything needing a rasteriser.
- Markdown tables as a delivery format. Aligned plain text survives a paste
  into a chat; markdown tables do not.
- Emoji as a data encoding.
- Interactive TUI layout, panes, key handling. A framework, not a design system.
- ASCII illustration.

## 12. Open questions

1. Separate package or same package with a second output? Same package, decided:
   it shares the palette, the authority rules and the docs site, and shares none
   of the px tokens. A second repo would drift.
2. Measured column budgets. The numbers in `column` are the shipping defaults.
   Run `ruler` in iPhone Telegram, Slack desktop, Slack iOS and Terminal with
   the same fixture and record what survives. Block glyph advance is the
   specific risk.
3. Keep 8 spark levels or drop to 5? 8 ships and gives resolution, 5 is more
   legible at small sizes. Keep 8 for narrow rows, revisit after the measured
   matrix.
4. Does the palette map to ANSI? If yes, each palette needs a 256-colour value
   plus a documented `--no-color` contract for logs.

## 13. Review sheet

`python3 scripts/text_board_page.py` writes `docs/text-review.html`. Every
string on the sheet comes from the renderer, so the sheet cannot drift from
the grammar it documents.
