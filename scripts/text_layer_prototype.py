#!/usr/bin/env python3
"""Konstrukt · Text — prototype renderer.

NOT a package output yet. This exists to test the proposed grammar before any
token lands in tokens/text.json. It is deliberately dependency-free and single
file, because the real consumers are standalone scripts (cron collectors,
briefings, CLI tools) that cannot take an npm dependency.

Every primitive here is a pure function returning a string. The board at the
bottom is the design review artifact: if a rule cannot be demonstrated on the
board, the rule does not belong in the spec.

Run: python3 scripts/text_layer_prototype.py
"""

from __future__ import annotations

# ---------------------------------------------------------------- glyph sets
# Two encodings, same ladder positions. `unicode` is the default; `ascii` is the
# fallback for channels that mangle block/box glyphs (SMS, some email clients,
# some terminals). One ladder, two renderings -- never two different ladders.
GLYPHS = {
    "unicode": {
        "spark8": "▁▂▃▄▅▆▇█",
        "bar4": "░▒▓█",
        "hbar_full": "█",
        "hbar_empty": "░",
        "box_light": ("┌", "┐", "└", "┘", "─", "│"),
        "box_ink": ("┏", "┓", "┗", "┛", "━", "┃"),
        "caret": "▲",
        "rule": "─",
        "dot": "·",
        "dot_on": "●",
        "pointer": "›",
        "spin": "▘▝▗▖",
    },
    "ascii": {
        "spark8": ".:-=+*#@",
        "bar4": "-=#@",
        "hbar_full": "#",
        "hbar_empty": ".",
        "box_light": ("+", "+", "+", "+", "-", "|"),
        "box_ink": ("+", "+", "+", "+", "=", "|"),
        "caret": "^",
        "rule": "-",
        "dot": ".",
        "dot_on": "o",
        "pointer": ">",
        "spin": "|/-\\",
    },
}

# Column budgets. A chart never wraps: it is truncated at the budget instead.
COLUMNS = {"phone": 34, "chat": 44, "terminal": 78}

# Glyphs already claimed by a meaning somewhere in the family. A mark may not be
# reused for a second meaning, because the reader has already learned the first
# one. Arrows are the live case: the existing weather surfaces spend them on high/low,
# so a wind arrow reads as a temperature trend.
RESERVED = {
    "↑": "high temperature / increase",
    "↓": "low temperature / decrease",
    "▲": "caret: points at the column annotated below",
    "›": "bullet / list lead-in",
    "·": "separator or idle state",
    "●": "active or present",
    "[NORMAL]": "status pill",
    "▁▂▃▄▅▆▇█": "data ladder: height means magnitude",
    "▘▝▗▖": "motion only: never carries a value",
}


def g(enc: str, key: str) -> str:
    return GLYPHS[enc][key]


# ---------------------------------------------------------------- sampling
def sample(values: list, n: int) -> list:
    """Pick n evenly spaced points. Compression is a design decision, not a
    side effect of slicing: 15 hourly values -> 8 cells is a readable curve,
    15 cells is noise on a phone."""
    if not values:
        return []
    if len(values) <= n:
        return list(values)
    step = (len(values) - 1) / (n - 1)
    return [values[round(i * step)] for i in range(n)]


# ---------------------------------------------------------------- primitives
def spark(values, n=8, low=None, high=None, min_spread=None, enc="unicode"):
    """One row, self-normalised. Caller MUST carry the numbers alongside."""
    cells = sample([v for v in values if v is not None], n)
    if not cells:
        return ""
    ladder = g(enc, "spark8")
    lo = min(cells) if low is None else low
    hi = max(cells) if high is None else high
    if hi <= lo:
        hi = lo + 1
    if min_spread is not None and (hi - lo) < min_spread:
        # A flat range must not render as mountains. Widen it instead.
        mid = (hi + lo) / 2
        lo, hi = mid - min_spread / 2, mid + min_spread / 2
    last = len(ladder) - 1
    out = []
    for value in cells:
        idx = int(round((value - lo) / (hi - lo) * last))
        out.append(ladder[max(0, min(last, idx))])
    return "".join(out)


def hbar(value, top, cells=8, enc="unicode", fixed=None):
    """Fixed-scale bar with a right-aligned magnitude. `fixed=(lo,hi)` pins the
    scale for bounded domains (percentages, rubric scores); omit it and the bar
    is relative to `top`, which is only honest when `top` is a real maximum."""
    lo, hi = fixed if fixed else (0, top if top > 0 else 1)
    ratio = 0 if hi <= lo else (value - lo) / (hi - lo)
    ratio = max(0.0, min(1.0, ratio))
    full = int(round(ratio * cells))
    bar = g(enc, "hbar_full") * full + g(enc, "hbar_empty") * (cells - full)
    return bar


def row(label, value_text, bar, label_w=16, bar_w=8, enc="unicode"):
    """The .row grammar: label left, bar, value right-aligned to the budget."""
    return f"  {label[:label_w].ljust(label_w)} {bar.ljust(bar_w)}  {value_text.rjust(5)}"


def grid(rows, header=None, enc="unicode"):
    """Heat grid. Cell values 0-3 index the 4-step ladder; None is blank."""
    ladder = g(enc, "bar4")
    out = []
    if header:
        out.append(f"  {''.ljust(10)} " + " ".join(header))
    for label, cells in rows:
        body = " ".join(" " if c is None else ladder[max(0, min(3, c))] for c in cells)
        # rstrip: a blank cell at the end of a row is not a trailing space, it
        # is the absence of a mark.
        out.append(f"  {label.ljust(10)} {body}".rstrip())
    return "\n".join(out)


def annotate(line, col: int, label: str, width=None, enc="unicode"):
    """Mark a column in the row above. Annotation lives directly under its
    target -- no legend, no counting across lines.

    Two placements, one meaning. If the label fits to the right of the caret it
    starts there. If it would run past the budget it is right-aligned so it ends
    at the caret instead, which reads as a footnote mark rather than a label
    that slid away from its target.
    """
    pad = " " * max(0, col)
    caret = f"{pad}{g(enc, 'caret')}"
    if width is None or col + len(label) <= width:
        start = col
    else:
        start = max(0, col - len(label) - 1)
    return f"{line}\n{caret}\n{' ' * start}{label}"


def peak_col(line: str, enc: str = "unicode") -> int:
    """Column of the tallest glyph in a rendered row -- what an annotation
    points at. Derived from the string, never hand-counted (hand-counting is
    how carets drift)."""
    ladder = GLYPHS[enc]["spark8"]
    best, col = -1, 0
    for i, ch in enumerate(line):
        if ch in ladder and ladder.index(ch) > best:
            best, col = ladder.index(ch), i
    return col


def frame(head_label, head_meta, body_lines, width=44, ink=True, enc="unicode"):
    """A Konstrukt module in text: heavy frame = --border, label left, meta
    right-aligned to the same column the rows end on."""
    tl, tr, bl, br, h, v = g(enc, "box_ink" if ink else "box_light")
    inner = width - 2
    top = f"{tl}{h * inner}{tr}"
    label = f" {head_label} "
    meta = f" {head_meta} "
    head = f"{v}{label}{' ' * max(1, inner - len(label) - len(meta))}{meta}{v}"
    rule = f"{v}{h * inner}{v}"
    rows = [f"{v} {line.ljust(inner - 2)} {v}" for line in body_lines]
    return "\n".join([top, head, rule, *rows, f"{bl}{h * inner}{br}"])


def pill(state, enc="unicode"):
    return f"[{state.upper()}]"


def ruler(columns=44, enc="unicode"):
    """Paste-in calibration strip. Tens marked, dots between.

    The width contract cannot be asserted from a build machine: it depends on
    the client's font. So the system ships a measuring device. Paste the ruler
    into the channel once; if it comes back ragged, the channel is proportional
    and every chart in it must live inside a code block.
    """
    line = "".join(str(i % 10) for i in range(columns))
    tick = "".join("|" if i % 5 == 0 else g(enc, "dot") for i in range(columns))
    return f"{line}\n{tick}"


def range_bar(lo, hi, value, cells=16, enc="unicode"):
    """A span with the current value marked inside it.

    For quantities where the range carries as much meaning as the point: a
    sleep window, a price band, a load range. The bar is drawn in empty cells
    so the marked value still reads as a position, not a fill.
    """
    span = max(1.0, float(cells))
    out = []
    for i in range(cells):
        at = i / (span - 1) if cells > 1 else 0.0
        out.append("▒" if lo <= at * 100 <= hi else g(enc, "dot"))
    pos = int(round(max(0.0, min(1.0, value / 100)) * (cells - 1)))
    out[pos] = g(enc, "caret")
    return "".join(out)


def kv(rows, key_w=13, width=44, enc="unicode"):
    """Metadata block: dot leaders keep the eye on the value column without a
    second border. This is the text form of `.row-meta`."""
    out = []
    for key, value in rows:
        lead = max(2, width - 4 - key_w - len(value))
        # One space before the value: leaders that touch a value read as if the
        # value were part of the leader run.
        out.append(f"  {key.ljust(key_w)}{g(enc, 'dot') * lead} {value}")
    return "\n".join(out)


def multi(series, cells=12, enc="unicode", width=44):
    """Small multiples on ONE shared scale.

    The shared scale is the point: three independent sparklines cannot be
    compared, three rows sharing a range can. Labels are padded to the same
    column so the rows read as a table of shapes.
    """
    values = [v for _, vals in series for v in vals if v is not None]
    lo, hi = min(values), max(values)
    label_w = max(len(name) for name, _ in series)
    out = []
    for name, vals in series:
        out.append(f"  {name.ljust(label_w)}  {spark(vals, cells, low=lo, high=hi, enc=enc)}")
    return "\n".join(out)


# ---------------------------------------------------------------- the board
def board(enc="unicode"):
    W = 44
    out = []
    add = out.append

    add(f"  KONSTRUK · TEXT  {enc}  {COLUMNS['chat']} cols")
    add("")

    # 1. SPARK -- the shipped weather microchart, rebuilt from the grammar.
    add("  01 SPARK")
    temps = [56, 54, 58, 63, 68, 72, 70, 64]
    rain = [5, 4, 8, 18, 44, 78, 61, 22]
    temp_bar = spark(temps, min_spread=8, enc=enc)
    rain_bar = spark(rain, low=0, high=100, enc=enc)
    head = f"   {temp_bar} temp 56→72°    "
    line = f"{head}{rain_bar} rain"
    # Annotate inside the rain series only: the tallest glyph on the whole line
    # belongs to temp, so the offset is computed per-series, not per-row.
    add(annotate(line, len(head) + peak_col(rain_bar, enc), "peak 78% 17:00",
                 width=COLUMNS["chat"], enc=enc))
    add("")

    # 2. HBAR -- fixed scale, right-aligned magnitudes.
    add("  02 HBAR  fixed 0-100")
    add(row("Deep work", "62%", hbar(62, 100, fixed=(0, 100), enc=enc), enc=enc))
    add(row("Client delivery", "38%", hbar(38, 100, fixed=(0, 100), enc=enc), enc=enc))
    add(row("Admin", "9%", hbar(9, 100, fixed=(0, 100), enc=enc), enc=enc))
    add("")

    # 3. GRID -- pattern over weeks; M T W T F S S.
    add("  03 GRID  habit matrix  4-step ladder")
    add(grid([
        ("WK 40", [1, None, 2, None, 0, 3, None]),
        ("WK 41", [2, None, 0, None, 1, None, None]),
        ("WK 42", [3, None, 1, None, 2, None, None]),
    ], header=["M", "T", "W", "T", "F", "S", "S"], enc=enc))
    add("")

    # 4. FRAME -- a module, in text.
    add("  04 FRAME")
    add(frame(
        "SERVICE", "STATUS " + "WATCH",
        [f"{g(enc,'dot_on')} uptime        99.98%",
         f"{g(enc,'dot')} latency       42 ms",
         f"{g(enc,'dot')} next run      Nov 12"],
        width=W, enc=enc))
    add("")

    # 5. CLI -- animation resolves; never animates numbers.
    add("  05 CLI  animation resolves")
    spin = g(enc, "spin")
    add(f"  {spin[0]} syncing 3 sources")
    add("  " + spin + "  four frames, then resolved")
    add("")
    add(frame("SYNC", "DONE 2.1s",
              [f"calendar   {g(enc,'hbar_full')*8}  ok",
               f"weather    {g(enc,'hbar_full')*6}{g(enc,'hbar_empty')*2}  partial",
               f"gmail      {g(enc,'hbar_full')*8}  ok"],
              width=W, ink=False, enc=enc))

    # 6. RANGE -- a span with the value inside it.
    add("  06 RANGE  sleep window, 7 nights")
    add(f"  MON  {range_bar(22, 71, 48, enc=enc)}  7.4h")
    add(f"  TUE  {range_bar(18, 66, 30, enc=enc)}  6.1h")
    add("")

    # 7. MULTI -- one scale, three rows.
    add("  07 MULTI  deep work, shared scale 0-14")
    add(multi([("WK 40", [2, 6, 4, 9, 3, 0, 0]),
               ("WK 41", [4, 7, 8, 5, 6, 1, 0]),
               ("WK 42", [3, 3, 6, 11, 4, 0, 0])], enc=enc))
    add("")

    # 8. KV -- metadata with dot leaders.
    add("  08 KV")
    add(kv([("next appt", "Nov 12"), ("meds", "3 active"),
            ("records", "11 of 12")], enc=enc))
    add("")

    # 9. RULER -- the measuring device, not a chart.
    add("  09 RULER  paste into a new channel once")
    add("  " + ruler(40, enc=enc).replace("\n", "\n  "))
    return "\n".join(out)


# A block that breaks the rules on purpose, so the linter has something to
# catch. Every line here is a real defect seen in the wild.
BROKEN = """  01 SPARK
   ▁▂▃▅▆█▇▅
   ▁#▃▅ temp 56→72°
  TUE	admin  12%
  Deep work      ███░░░░░    80%
   ▂▁▃▅▆█▇▅ temp 72° 🔥
                          ▲
                                peak 78% 17:00
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ SERVICE            STATUS WATCH ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
  this line is deliberately far too long for any chat channel budget on a phone"""


if __name__ == "__main__":
    print(board("unicode"))
    print()
    print(board("ascii"))
