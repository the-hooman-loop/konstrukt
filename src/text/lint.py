#!/usr/bin/env python3
"""Konstrukt · Text — conformance linter.

A design system without a gate is a style opinion. This checks a rendered text
block against the rules in docs/text.md and exits nonzero when the block would
embarrass itself in a chat window.

Usage:
  python3 src/text/lint.py --file block.txt --budget 44
  cat block.txt | python3 src/text/lint.py --budget 34
  python3 src/text/lint.py --self-test

Rules checked:
  T1 WIDTH      line wider than the column budget
  T2 TABS       tab characters (alignment becomes the client's guess)
  T3 TRAILING   trailing whitespace (invisible in output, breaks golden diffs)
  T4 LADDER     two different glyph families in one line
  T5 ANCHOR     a shape with no numbers on the same line
  T6 BAR-LIE    bar length contradicts the percentage beside it
  T7 CARET      caret points past its row, or at nothing
  T8 FRAME      frame lines that do not close
  T9 EMOJI      emoji used as a data mark
  T10 ARROW     up/down arrows used away from a number (reserved for high/low)
  T11 SERIES    two unlabeled series on one line
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata

SPARK_U = "▁▂▃▄▅▆▇█"
SPARK_A = ".:-=+*#@"
BAR4 = "░▒▓█"
ASCII_BAR4 = "-=#@"
CARET = "▲^"
UP, DOWN = chr(0x2191), chr(0x2193)

# Glyphs that belong to exactly one family. The shared glyphs (█ and ░) cannot
# tell a bar from a sparkline, so family detection keys on these instead.
SPARK_ONLY = "▁▂▃▄▅▆▇"
BAR_ONLY = "░▒▓"

LADDERS = {
    "spark-unicode": SPARK_U,
    "spark-ascii": SPARK_A,
    "bar4-unicode": BAR4,
    "bar4-ascii": ASCII_BAR4,
}

BOX_CHARS = "┌┐└┘├┤┬┴┼─│┏┓┗┛┣┫┳┻╋━┃"

# Emoji that are section labels in the established brief grammar, not data.
EMOJI_ALLOW = {"\U0001F4C5", "\U0001F3AF", "\U0001F4CC", "\u2705"}


def width(s: str) -> int:
    """Display columns. Wide glyphs cost 2, combining marks cost 0."""
    total = 0
    for ch in s:
        if unicodedata.combining(ch):
            continue
        total += 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1
    return total


def _runs(line: str, alphabet: str, minimum: int = 1) -> list:
    """Spans of `line` made only of alphabet characters, at least `minimum` long."""
    out, start = [], None
    for i, ch in enumerate(line):
        if ch in alphabet:
            if start is None:
                start = i
        else:
            if start is not None and i - start >= minimum:
                out.append((start, i))
            start = None
    if start is not None and len(line) - start >= minimum:
        out.append((start, len(line)))
    return out


def lint(text: str, budget: int = 44) -> list:
    findings = []
    lines = text.split("\n")

    def add(rule, lineno, message):
        findings.append((rule, lineno, message))

    for n, line in enumerate(lines, start=1):
        # T1 width
        if width(line) > budget:
            add("T1", n, f"{width(line)} columns exceeds budget {budget}")

        # T2 tabs
        if "\t" in line:
            add("T2", n, "tab character; pad with spaces")

        # T3 trailing whitespace
        if line != line.rstrip() and line.strip():
            add("T3", n, "trailing whitespace")

        # T4 mixed ladder families. A bar (length = magnitude) and a sparkline
        # (height = magnitude) may not share a line: the reader has to switch
        # decoding mid-row.
        has_spark = any(ch in line for ch in SPARK_ONLY)
        has_bar = any(ch in line for ch in BAR_ONLY) or "#" in line
        if has_spark and has_bar:
            add("T4", n, "bar and sparkline ladders mixed in one line")

        # T5 shape without magnitude. Only a curve can lie this way; a bar's
        # length is already its magnitude.
        if has_spark and _runs(line, SPARK_U, minimum=4) and not re.search(r"\d", line):
            add("T5", n, "sparkline with no number on the line; shape is not magnitude")

        # T6 bar length contradicts the percentage
        for m in re.finditer("([\u2588\u2591]+)\\s+(\\d+(?:\\.\\d+)?)%", line):
            bar, pct = m.group(1), float(m.group(2))
            cells = len(bar)
            on = bar.count("\u2588")
            expect = round(pct / 100 * cells)
            if on != expect:
                add("T6", n,
                    f"bar shows {on}/{cells} cells but the label says {pct:g}% "
                    f"(expected {expect})")

        # T9 emoji as data
        for ch in line:
            cp = ord(ch)
            is_emoji = cp >= 0x1F300 or 0x2600 <= cp <= 0x27BF
            if is_emoji and ch not in EMOJI_ALLOW:
                add("T9", n, f"emoji {ch!r} used as a data mark")
                break

        # T10 reserved arrows away from a number
        for arrow in (UP, DOWN):
            hit = False
            for i, ch in enumerate(line):
                if ch != arrow:
                    continue
                near = line[max(0, i - 2):i] + line[i + 1:i + 3]
                if not re.search(r"\d", near):
                    add("T10", n, f"{arrow} without an adjacent number "
                                  f"(arrows mean high/low, not direction)")
                    hit = True
                    break
            if hit:
                break

        # T11 two unlabeled series on one line
        runs = _runs(line, SPARK_ONLY, minimum=3)
        if len(runs) >= 2 and not re.search(r"[A-Za-z]", line):
            add("T11", n, "two series on one line with no label for either")

        # T7 caret alignment
        if line.strip() and set(line.strip()) <= set(CARET) and n > 1:
            col = line.index(line.strip()[0])
            prev = lines[n - 2]
            if col >= width(prev):
                add("T7", n, f"caret at column {col} points past its row "
                              f"({width(prev)} wide)")
            elif col > 0 and prev[col:col + 1] in (" ", ""):
                add("T7", n, f"caret at column {col} points at whitespace")

    # T8 frames close
    frame_lines = [(n, line) for n, line in enumerate(lines, start=1)
                   if line and line[0] in BOX_CHARS]
    if frame_lines:
        widths = {width(line) for _, line in frame_lines}
        if len(widths) > 1:
            add("T8", frame_lines[0][0],
                f"frame lines disagree on width: {sorted(widths)}")

    return findings


# One deliberately-broken construct per rule: the linter must catch all of them.
SEEDED = "\n".join([
    "  01 SPARK",
    "   \u2581\u2582\u2583\u2584\u2585\u2586\u2587\u2588",
    "   \u2581#\u2583\u2585 temp 56\u219272\u00b0",
    "  TUE\tadmin  12%",
    "  Deep work      \u2588\u2588\u2588\u2591\u2591\u2591\u2591\u2591    80%",
    "   \u2582\u2581\u2583\u2585\u2586\u2588\u2587\u2585 temp 72\u00b0 \U0001F525",
    "                          \u25b2",
    "                                peak 78% 17:00",
    "\u250f" + "\u2501" * 33 + "\u2513",
    "\u2503 SERVICE            STATUS WATCH \u2503",
    "\u2517" + "\u2501" * 28 + "\u251b",
    "  this line is deliberately far too long for any chat channel budget on a phone",
    "  wind " + UP + " SSW rising",
    "  padded line   ",
    "  \u2581\u2582\u2583\u2584  \u2581\u2582\u2583\u2584",
])

EXPECTED_RULES = {"T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8", "T9", "T10", "T11"}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file")
    ap.add_argument("--budget", type=int, default=44)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args(argv)

    if args.self_test:
        hits = lint(SEEDED, budget=44)
        caught = {rule for rule, _, _ in hits}
        missing = EXPECTED_RULES - caught
        for rule, n, msg in hits:
            print(f"{rule:<4} line {n}: {msg}")
        print(f"\ncaught {len(caught)} of {len(EXPECTED_RULES)} rules: "
              f"{', '.join(sorted(caught))}")
        if missing:
            print(f"MISSED: {', '.join(sorted(missing))}")
            return 1
        print("self-test OK")
        return 0

    text = open(args.file, encoding="utf-8").read() if args.file else sys.stdin.read()
    findings = lint(text, args.budget)
    for rule, n, msg in findings:
        print(f"{rule:<4} line {n}: {msg}")
    if findings:
        print(f"\n{len(findings)} finding(s)")
        return 1
    print(f"clean at budget {args.budget}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
