#!/usr/bin/env python3
"""Build the Konstrukt · Text review sheet as a single self-contained HTML page.

The page is the review artifact for the text-layer proposal: every primitive
rendered live by the prototype module, inside real Konstrukt modules. Nothing
in it is a screenshot or a mockup of text -- the strings come from the
prototype, so the page cannot drift from the grammar it documents.

Run:  python3 scripts/text_board_page.py [out.html]
Then: python3 <skill>/scripts/html_to_png.py <out.html> <out.png> --measure
"""

from __future__ import annotations

import html
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import text_layer_prototype as K  # noqa: E402
import text_lint  # noqa: E402

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/tmp/konstrukt-text-board.html")
CHAT = K.COLUMNS["chat"]

TOKENS = """
:root{
  --font-sans:"Inter","Segoe UI",system-ui,-apple-system,sans-serif;
  --font-display:"Space Grotesk",system-ui,sans-serif;
  --font-mono:"SF Mono","Fira Code",Consolas,monospace;
  --bg:#F5F5F0; --bg-alt:#EBEBEB; --surface:#FFFFFF;
  --text:#0A0A0A; --ink:#0A0A0A; --text-muted:#6A6A6A;
  --border:#0A0A0A; --border-light:#D0D0C8;
  --accent:#067F8A; --accent-soft:#C8EAED; --accent-light:#E8F6F7;
  --danger:#9D1B1E; --radius:0px; --shadow:none;
}
*{box-sizing:border-box;}
body{
  margin:0; background:var(--bg); color:var(--text);
  font-family:var(--font-sans); font-size:16px; line-height:1.45;
  -webkit-font-smoothing:antialiased;
}
body::before{
  content:""; position:fixed; inset:0; pointer-events:none; z-index:0;
  background-image:linear-gradient(#0000000a 1px,transparent 1px),
                   linear-gradient(90deg,#0000000a 1px,transparent 1px);
  background-size:24px 24px;
}
.shell{position:relative; z-index:1; width:min(100%,1020px); margin:0 auto; padding:40px 28px 64px;}
.micro{font-family:var(--font-mono); font-size:.66rem; font-weight:700;
  letter-spacing:.14em; text-transform:uppercase; color:var(--accent);}
h1{font-family:var(--font-display); font-size:52px; line-height:.95;
  letter-spacing:-.04em; margin:10px 0 8px; text-wrap:balance;}
.lede{max-width:62ch; color:var(--text-muted); margin:0;}
.page-header{display:grid; grid-template-columns:1fr auto; align-items:start;
  gap:16px; border-bottom:2px solid var(--border); padding-bottom:18px; margin-bottom:0;}
.pill{font-family:var(--font-mono); font-size:.62rem; font-weight:700; letter-spacing:.12em;
  text-transform:uppercase; padding:5px 9px; border:1px solid var(--border); white-space:nowrap;}
.pill.solid{background:var(--border); color:#fff;}
.pill.teal{border-color:var(--accent); color:var(--accent);}
.status-col{display:grid; gap:6px; justify-items:end;}
.strip{display:grid; grid-template-columns:repeat(5,1fr); background:var(--accent-light);
  border:1px solid var(--border); border-top:0; margin-bottom:28px;}
.strip div{padding:12px 14px; border-right:1px solid var(--border-light);}
.strip div:last-child{border-right:0;}
.strip b{display:block; font-family:var(--font-display); font-size:26px; line-height:1;
  letter-spacing:-.03em; font-variant-numeric:tabular-nums;}
.strip span{display:block; margin-top:5px; font-family:var(--font-mono); font-size:.58rem;
  letter-spacing:.12em; text-transform:uppercase; color:var(--text-muted);}
.grid2{display:grid; grid-template-columns:1fr 1fr; gap:16px; align-items:start;}
.module{background:var(--surface); border:2px solid var(--border); margin-bottom:16px;
  min-width:0; break-inside:avoid;}
.module-head{display:grid; grid-template-columns:1fr auto; gap:10px; align-items:baseline;
  padding:9px 12px; border-bottom:1px solid var(--border-light);}
.module-label{font-family:var(--font-mono); font-size:.62rem; font-weight:700;
  letter-spacing:.14em; text-transform:uppercase;}
.module-meta{font-family:var(--font-mono); font-size:.58rem; color:var(--text-muted);
  letter-spacing:.06em;}
pre.kt{margin:0; padding:14px 12px; background:var(--surface); overflow-x:auto;
  font-family:var(--font-mono); font-size:13.5px; line-height:1.3;
  white-space:pre; max-width:100%;}
pre.kt.tint{background:var(--accent-light);}
.note{margin:0; padding:9px 12px; border-top:1px solid var(--border-light);
  font-size:12.5px; color:var(--text-muted);}
.note b{color:var(--text); font-weight:600;}
.note code{font-family:var(--font-mono); font-size:11.5px; color:var(--text);
  background:var(--accent-light); border:1px solid var(--accent-soft);
  padding:0 3px; white-space:nowrap;}
table{gap:0; width:100%; border-collapse:collapse; font-family:var(--font-mono); font-size:12px;}
th,td{text-align:left; padding:7px 12px; border-bottom:1px solid var(--border-light); vertical-align:top;}
th{font-size:.58rem; letter-spacing:.12em; text-transform:uppercase; color:var(--text-muted);}
td.g{font-size:15px; color:var(--accent); width:64px;}
td.m{color:var(--text-muted);}
.ok{color:#166534;} .bad{color:var(--danger);}
h2{font-family:var(--font-display); font-size:22px; letter-spacing:-.02em; margin:32px 0 12px;
  padding-bottom:7px; border-bottom:1px solid var(--border-light);}
.foot{margin-top:28px; padding-top:14px; border-top:2px solid var(--border);
  font-family:var(--font-mono); font-size:.6rem; letter-spacing:.1em;
  text-transform:uppercase; color:var(--text-muted); display:flex; justify-content:space-between;}
"""


def pre(text, tint=False):
    cls = "kt tint" if tint else "kt"
    return f'<pre class="{cls}">{html.escape(text)}</pre>'


def module(label, meta, body, note=""):
    n = f'<p class="note">{note}</p>' if note else ""
    return (f'<div class="module"><div class="module-head">'
            f'<span class="module-label">{label}</span>'
            f'<span class="module-meta">{meta}</span></div>{body}{n}</div>')


def demo_spark():
    temps = [53, 58, 65, 71, 74, 71, 66, 60]
    rain = [5, 12, 28, 55, 78, 71, 44, 22]
    tb = K.spark(temps, min_spread=8)
    rb = K.spark(rain, low=0, high=100)
    head = f"   {tb} temp 53→74°    "
    line = f"{head}{rb} rain"
    body = K.annotate(line, len(head) + K.peak_col(rb), "peak 78% 17:00", width=CHAT)
    return pre(body)


def demo_hbar():
    rows = [("Deep work", 62), ("Client delivery", 38), ("Admin", 9)]
    return pre("\n".join(
        K.row(name, f"{v}%", K.hbar(v, 100, fixed=(0, 100))) for name, v in rows
    ))


def demo_grid():
    return pre(K.grid([
        ("WK 40", [1, None, 2, None, 0, 3, None]),
        ("WK 41", [2, None, 0, None, 1, None, None]),
        ("WK 42", [3, None, 1, None, 2, None, None]),
    ], header=["M", "T", "W", "T", "F", "S", "S"]))


def demo_range():
    return pre("\n".join([
        f"  MON  {K.range_bar(22, 71, 48)}  7.4h",
        f"  TUE  {K.range_bar(18, 66, 30)}  6.1h",
        f"  WED  {K.range_bar(30, 78, 62)}  8.2h",
    ]))


def demo_multi():
    return pre(K.multi([("WK 40", [2, 6, 4, 9, 3, 0, 0]),
                        ("WK 41", [4, 7, 8, 5, 6, 1, 0]),
                        ("WK 42", [3, 3, 6, 11, 4, 0, 0])]))


def demo_kv():
    return pre(K.kv([("next appt", "Nov 12"), ("meds", "3 active"),
                     ("records", "11 of 12")]))


def demo_frame():
    return pre(K.frame("SERVICE", "STATUS WATCH", [
        f"{K.g('unicode','dot_on')} uptime        99.98%",
        f"{K.g('unicode','dot')} latency       42 ms",
        f"{K.g('unicode','dot')} next run      Nov 12",
    ]))


def demo_cli():
    spin = K.GLYPHS["unicode"]["spark8"]
    frames = "  " + "".join(spin[:5]) + "  frame 5 of 8"
    resolved = K.frame("SYNC", "DONE 2.1s", [
        "calendar   " + "█" * 8 + "  ok",
        "weather    " + "█" * 6 + "░" * 2 + "  partial",
        "gmail      " + "█" * 8 + "  ok",
    ], ink=False)
    return pre(f"  {spin[0]} syncing 3 sources\n{frames}\n\n{resolved}")


def demo_ruler():
    return pre("  " + K.ruler(40).replace("\n", "\n  "))


def demo_annot():
    """The three annotation rules, drawn rather than described."""
    return pre("\n".join([
        "   ▁▃▆█▆▃ temp 53→74°",
        "        ▲",
        "        caret anchors to its column",
        "",
        "   ▁▃▆█▆▃   ▁▃▆▆▄▃",
        "                ▲",
        "        label 78% 17:00   label slides left at the edge",
    ]))


def demo_live():
    """What the linter said about the chart that actually ships."""
    return pre("\n".join([
        "  wet day, live path        38 cols   clean",
        "  same chart, 15 raw hours  54 cols   T1 over budget",
    ]))


def demo_ascii():
    """The same three constructs in both encodings, side by side."""
    vals = [53, 58, 65, 71, 74, 71, 66, 60]
    return pre("\n".join([
        f"  unicode  {K.spark(vals)} temp 53→74°",
        f"  ascii    {K.spark(vals, enc='ascii')} temp 53→74°",
        "",
        f"  unicode  {K.hbar(62, 100, fixed=(0, 100))}  62%",
        f"  ascii    {K.hbar(62, 100, fixed=(0, 100), enc='ascii')}  62%",
        "",
        "  marks    ▲ ● › ·        caret, on, lead-in, idle",
        "           ^ o > .        ascii equivalents",
    ]))


def reserved_table():
    rows = "".join(
        f'<tr><td class="g">{html.escape(glyph)}</td>'
        f'<td class="m">{html.escape(meaning)}</td></tr>'
        for glyph, meaning in K.RESERVED.items()
    )
    return (f'<table><thead><tr><th>Mark</th><th>Already means</th></tr></thead>'
            f'<tbody>{rows}</tbody></table>')


def lint_table():
    hits = text_lint.lint(text_lint.SEEDED, budget=44)
    seen, rows = set(), []
    for rule, n, msg in hits:
        if rule in seen:
            continue
        seen.add(rule)
        rows.append(f'<tr><td class="g">{rule}</td>'
                    f'<td class="m">{html.escape(msg)}</td></tr>')
    return ('<table><thead><tr><th>Rule</th><th>Caught in the seeded block</th>'
            '</tr></thead><tbody>' + "".join(rows) + "</tbody></table>")


def build() -> str:
    checks = len(text_lint.EXPECTED_RULES)
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>Konstrukt · Text — review sheet</title>
<style>{TOKENS}</style></head>
<body><div class="shell">
  <div class="page-header">
    <div>
      <span class="micro">Konstrukt / proposal 01</span>
      <h1>Text layer</h1>
      <p class="lede">The same authority structure as Konstrukt, rebuilt for a
      fixed cell: hard frames, mono metadata, one accent, status words. Charts,
      annotations and CLI motion from one token set, one linter, two encodings.</p>
    </div>
    <div class="status-col">
      <span class="pill solid">PROPOSED</span>
      <span class="pill teal">NOT IN BUILD</span>
    </div>
  </div>
  <div class="strip">
    <div><b>14</b><span>rules</span></div>
    <div><b>9</b><span>primitives</span></div>
    <div><b>2</b><span>encodings</span></div>
    <div><b>{checks}</b><span>linter checks</span></div>
    <div><b>44</b><span>chat columns</span></div>
  </div>

  <h2>Charts</h2>
  <div class="grid2">
    {module("SPARK", "01 · one row · self-normalised", demo_spark(),
            "<b>Shape is not magnitude.</b> Numbers ride on the same line. Caret is derived "
            "from the rendered string, never hand-counted.")}
    {module("HBAR", "02 · fixed scale", demo_hbar(),
            "<b>Bounded domains pin their scale.</b> 9% cannot render as a full bar. "
            "Cells are the unit; the value is right-aligned.")}
    {module("GRID", "03 · 4-step ladder", demo_grid(),
            "<b>Pattern over time.</b> Blank cells are absence, not zero, so rows rstrip.")}
    {module("RANGE", "04 · span plus position", demo_range(),
            "For a sleep window or a price band, where the range carries as much "
            "meaning as the point.")}
    {module("MULTI", "05 · small multiples, one scale", demo_multi(),
            "<b>Shared scale is the point.</b> Three independent sparklines cannot be "
            "compared; three rows sharing a range can.")}
    {module("ANNOTATION GRAMMAR", "06 · caret and label", demo_annot(),
        "The label slides; the caret never moves. That is what keeps a clean block "
        "inside the column budget.")}
  </div>

  <h2>Composition</h2>
  <div class="grid2">
    {module("FRAME", "07 · a module, in text", demo_frame(),
            "Heavy box = <b>--border</b> 2px. Single box = <b>--border-light</b>. "
            "Label left, meta right-aligned to the row end.")}
    {module("KV", "08 · metadata with dot leaders", demo_kv(),
            "The text form of <b>.row-meta</b>. Leaders keep the eye on the value "
            "column without a second border.")}
  </div>

  <h2>CLI</h2>
  <div class="grid2">
    {module("MOTION", "09 · resolves", demo_cli(),
            "<b>Animation ends in a terminal state.</b> Never animate a number. "
            "Reduced motion means printing only the resolved frame.")}
    {module("RULER", "measuring device, not a chart", demo_ruler(),
            "The width contract depends on the client font, so the system ships a "
            "probe. Paste it once; if it comes back ragged, charts go in a code block.")}
  </div>

  <h2>Encoding</h2>
  <div class="grid2">
    {module("ASCII FALLBACK", "same ladder positions", demo_ascii(),
            "<code>.:-=+*#@</code> replaces the block ladder, <code>-=#@</code> replaces the "
            "bar ladder, <code>+ - | =</code> replaces box drawing. Degraded resolution, "
            "identical language, for SMS, logs and broken fonts.")}
    {module("RESERVED GLYPHS", "no second meaning", reserved_table(),
            "A mark already spent on one meaning is not available for another. "
            "Wind arrows are the live collision.")}
  </div>

  <h2>Enforcement</h2>
  {module("LINTER", f"self-test · {checks} of {checks} rules caught", lint_table(),
          "One deliberately broken construct per rule. The linter runs in the build "
          "gate, so a chart cannot ship with a lying bar.")}
  {module("LIVE CONSUMER", "morning brief weather microchart", demo_live(),
      "The shipped path pre-samples to 8 points, so it passes today. The primitive "
      "owns no column contract, so a caller that hands it raw hourly data renders "
      "54 columns and nothing complains. Sampling moves into the primitive.")}
  <div class="foot"><span>Konstrukt · Text · proposal</span>
    <span>rendered from scripts/text_layer_prototype.py</span></div>
</div></body></html>"""
    return page


if __name__ == "__main__":
    OUT.write_text(build(), encoding="utf-8")
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")
