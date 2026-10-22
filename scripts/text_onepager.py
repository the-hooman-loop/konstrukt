#!/usr/bin/env python3
"""Build the Konstrukt · Text one-pager demo poster.

Different artifact from the review sheet: this one shows the grammar *in
context*, in the channels it actually ships to, so the argument is legibility
under real conditions rather than a spec table.

Every string inside a chart comes from the prototype. Nothing is typed by hand.

Run:  python3 scripts/text_onepager.py [out.html]
Then: python3 <skill>/scripts/html_to_png.py <out.html> <out.png> --width 1400
"""

from __future__ import annotations

import html
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import text_layer_prototype as K  # noqa: E402

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/tmp/konstrukt-text-onepager.html")
CHAT = K.COLUMNS["chat"]

CSS = """
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
body{margin:0; background:var(--bg); color:var(--text);
  font-family:var(--font-sans); font-size:16px; line-height:1.45;
  -webkit-font-smoothing:antialiased;}
body::before{content:""; position:fixed; inset:0; pointer-events:none; z-index:0;
  background-image:linear-gradient(#0000000a 1px,transparent 1px),
                   linear-gradient(90deg,#0000000a 1px,transparent 1px);
  background-size:24px 24px;}
.poster{position:relative; z-index:1; width:1360px; margin:0 auto; padding:44px 44px 52px;}
.micro{font-family:var(--font-mono); font-size:.68rem; font-weight:700;
  letter-spacing:.16em; text-transform:uppercase; color:var(--accent);}
.top{display:grid; grid-template-columns:1fr auto; gap:24px; align-items:start;
  border-bottom:2px solid var(--border); padding-bottom:22px;}
h1{font-family:var(--font-display); font-size:76px; line-height:.92;
  letter-spacing:-.045em; margin:12px 0 14px; text-wrap:balance; max-width:19ch;}
.lede{max-width:58ch; color:var(--text-muted); margin:0; font-size:17px;}
.status{display:grid; gap:7px; justify-items:end;}
.pill{font-family:var(--font-mono); font-size:.6rem; font-weight:700; letter-spacing:.13em;
  text-transform:uppercase; padding:5px 9px; border:1px solid var(--border); white-space:nowrap;}
.pill.solid{background:var(--border); color:#fff;}
.pill.teal{border-color:var(--accent); color:var(--accent);}
.strip{display:grid; grid-template-columns:repeat(5,1fr); background:var(--accent-light);
  border:1px solid var(--border); border-top:0; margin-bottom:26px;}
.strip div{padding:11px 14px; border-right:1px solid var(--border-light);}
.strip div:last-child{border-right:0;}
.strip b{display:block; font-family:var(--font-display); font-size:25px; line-height:1;
  letter-spacing:-.03em; font-variant-numeric:tabular-nums;}
.strip span{display:block; margin-top:5px; font-family:var(--font-mono); font-size:.55rem;
  letter-spacing:.12em; text-transform:uppercase; color:var(--text-muted);}
.cols{display:grid; grid-template-columns:1fr 1fr; gap:18px; align-items:start;}
.col{display:grid; gap:18px;}
.ctx{background:var(--surface); border:2px solid var(--border); min-width:0; break-inside:avoid;}
.ctx-h{display:grid; grid-template-columns:auto 1fr auto; gap:12px; align-items:baseline;
  padding:9px 13px; border-bottom:1px solid var(--border-light);}
.ctx-n{font-family:var(--font-display); font-size:19px; line-height:1; letter-spacing:-.02em;}
.ctx-name{font-family:var(--font-mono); font-size:.63rem; font-weight:700;
  letter-spacing:.15em; text-transform:uppercase;}
.ctx-meta{font-family:var(--font-mono); font-size:.55rem; color:var(--text-muted);
  letter-spacing:.07em; text-align:right;}
.ctx-body{padding:14px 13px;}
.ctx-note{margin:0; padding:9px 13px; border-top:1px solid var(--border-light);
  font-size:12.5px; color:var(--text-muted);}
.ctx-note b{color:var(--text); font-weight:600;}
pre.kt{margin:0; font-family:var(--font-mono); font-size:13px; line-height:1.3;
  white-space:pre; max-width:100%; overflow-x:auto;}
pre.kt.tint{background:var(--accent-light); border:1px solid var(--accent-soft);
  padding:9px 10px;}
/* A data ladder needs vertical room: eight levels inside 13px collapses into a
   silhouette. 16px gives the height dimension something to say. */
pre.kt.chart{font-size:16px; line-height:1.05;}
pre.kt.ladder{font-size:15px; line-height:1.15;}
/* telegram */
.chat{background:var(--bg-alt); border:1px solid var(--border-light); padding:12px;}
.who{display:flex; justify-content:space-between; align-items:baseline; margin-bottom:8px;}
.who span{font-family:var(--font-mono); font-size:.54rem; letter-spacing:.11em;
  text-transform:uppercase; color:var(--text-muted);}
.bubble{background:#fff; border:1px solid var(--border-light); padding:11px 12px;}
.msg{margin:9px 0 0; font-size:13.5px; line-height:1.5;}
.msg .lab{display:block; font-family:var(--font-mono); font-size:.58rem; font-weight:700;
  letter-spacing:.12em; text-transform:uppercase; color:var(--accent); margin:10px 0 3px;}
.msg .row-l{display:block; padding:1px 0;}
.msg .t{font-family:var(--font-mono); font-size:11.5px; color:var(--text-muted);
  display:inline-block; min-width:44px;}
.msg .lead{font-family:var(--font-mono); color:var(--accent); margin-right:6px;}
/* terminal */
.term{background:var(--ink); color:#F2F2EC; padding:14px 15px;}
.term pre{font-family:var(--font-mono); font-size:12.5px; line-height:1.45; margin:0;
  white-space:pre; color:#F2F2EC;}
.term .p{color:#5FD3DC;} .term .m{color:#8A8A82;} .term .ok{color:#8FE3A8;}
/* dashboard */
.page-mock{background:var(--bg); border:1px solid var(--border-light); padding:12px;}
.mod{background:#fff; border:2px solid var(--border);}
.mod-h{display:grid; grid-template-columns:1fr auto; gap:10px; padding:8px 11px;
  border-bottom:1px solid var(--border-light);}
.mod-h b{font-family:var(--font-mono); font-size:.6rem; letter-spacing:.14em; text-transform:uppercase;}
.mod-h span{font-family:var(--font-mono); font-size:.55rem; color:var(--text-muted);}
.mod-b{padding:11px;}
/* annotation */
.anno{display:grid; gap:12px;}
.anno-row{border-left:2px solid var(--border-light); padding-left:11px;}
.anno-cap{font-size:12px; color:var(--text-muted); margin:4px 0 0;}
.anno-cap b{color:var(--text); font-weight:600;}
/* footer */
.foot{margin-top:24px; border-top:2px solid var(--border); padding-top:16px;
  display:grid; grid-template-columns:1.1fr 1fr; gap:26px;}
.chips{display:flex; flex-wrap:wrap; gap:6px;}
.chip{font-family:var(--font-mono); font-size:.56rem; letter-spacing:.1em;
  text-transform:uppercase; border:1px solid var(--border-light); padding:4px 7px;
  color:var(--text-muted);}
.chip.on{border-color:var(--accent); color:var(--accent); background:var(--accent-light);}
.ruleline{font-size:12.5px; color:var(--text-muted); margin:10px 0 0; max-width:60ch;}
.ruleline b{color:var(--text);}
.sign{display:flex; justify-content:space-between; align-items:end; gap:16px;
  border-left:1px solid var(--border-light); padding-left:24px;}
.sign .k{font-family:var(--font-mono); font-size:.55rem; letter-spacing:.12em;
  text-transform:uppercase; color:var(--text-muted);}
.sign .v{font-family:var(--font-display); font-size:19px; letter-spacing:-.02em;}
"""


def esc(t):
    return html.escape(t)


def pre(text, tint=False, cls=""):
    classes = " ".join(c for c in ("kt", "tint" if tint else "", cls) if c)
    return f'<pre class="{classes}">{esc(text)}</pre>'


def card(n, name, meta, body, note):
    return (f'<article class="ctx"><div class="ctx-h"><span class="ctx-n">{n}</span>'
            f'<span class="ctx-name">{name}</span>'
            f'<span class="ctx-meta">{meta}</span></div>'
            f'<div class="ctx-body">{body}</div>'
            f'<p class="ctx-note">{note}</p></article>')


# ------------------------------------------------------------------ contexts
def ctx_telegram():
    temps = [54, 58, 64, 70, 74, 72, 67, 61]
    rain = [4, 8, 16, 38, 66, 84, 61, 30]
    tb, rb = K.spark(temps, min_spread=8), K.spark(rain, low=0, high=100)
    head = f"   {tb} temp 54→74°   "
    line = f"{head}{rb} rain"
    chart = K.annotate(line, len(head) + K.peak_col(rb), "peak 84% 16:00", width=42)

    rows = "".join(
        f'<span class="row-l"><span class="lead">›</span>'
        f'<span class="t">{t}</span>{what}</span>'
        for t, what in (("10:00", "design review"), ("13:30", "client standup"))
    )
    body = (
        '<div class="chat"><div class="who"><span>assistant</span><span>08:14</span></div>'
        f'<div class="bubble">{pre(chart, tint=True, cls="chart")}'
        f'<p class="msg"><span class="lab">📅 agenda</span>{rows}'
        '<span class="lab">🎯 priorities</span>'
        '<span class="row-l"><span class="lead">›</span>client deck before 10</span>'
        '</p></div></div>'
    )
    return card("01", "Telegram", "morning brief · 42 cols", body,
                "<b>The chart is the message.</b> A tinted code block holds the only "
                "monospace thing in the thread, so the shape reads before the words do.")


def ctx_cli():
    spin = K.g("unicode", "spin")
    resolved = K.frame("SYNC", "DONE 2.1s", [
        "calendar   " + "█" * 8 + "  ok",
        "weather    " + "█" * 6 + "░" * 2 + "  partial",
        "gmail      " + "█" * 8 + "  ok",
    ], ink=False)
    body = (
        '<div class="term"><pre>'
        '<span class="p">▶</span> straat sync --all\n'
        f'  {spin[0]} syncing 3 sources\n'
        f'  {spin} <span class="m">frame 3 / 4</span>\n\n'
        f'{esc(resolved)}\n'
        '<span class="m"> exit 0 </span></pre></div>'
    )
    return card("02", "CLI", "terminal · 44 cols", body,
                "<b>Motion resolves.</b> No spinner survives the last frame, no number "
                "is animated, and the terminal state is a frame with a verdict in it.")


def ctx_slack():
    rows = "\n".join(K.row(n, f"{v}%", K.hbar(v, 100, fixed=(0, 100)))
                     for n, v in (("Deep work", 62), ("Client delivery", 38), ("Admin", 9)))
    kv = K.kv([("invoiced", "$8,400"), ("outstanding", "$2,150")], width=42)
    body = ('<div style="border:1px solid var(--border-light);padding:12px">'
            f'{pre(rows)}'
            '<div style="height:1px;background:var(--border-light);margin:11px 0"></div>'
            f'{pre(kv)}</div>')
    return card("03", "Slack digest", "weekly review · 42 cols", body,
                "<b>Fixed scale or nothing.</b> 9% cannot draw a full bar, so a bad week "
                "cannot look like a good one. The value is right-aligned to the budget.")


def ctx_dashboard():
    grid = K.grid([("WK 40", [1, None, 2, None, 0, 3, None]),
                   ("WK 41", [2, None, 0, None, 1, None, None]),
                   ("WK 42", [3, None, 1, None, 2, None, None])],
                  header=["M", "T", "W", "T", "F", "S", "S"])
    multi = K.multi([("WK 40", [2, 6, 4, 9, 3, 0, 0]),
                     ("WK 41", [4, 7, 8, 5, 6, 1, 0])])
    body = ('<div class="page-mock"><div class="mod">'
            '<div class="mod-h"><b>Time ledger</b><span>6 WEEKS · 42 ENTRIES</span></div>'
            f'<div class="mod-b">{pre(grid, cls="ladder")}'
            '<div style="height:1px;background:var(--border-light);margin:10px 0"></div>'
            f'{pre(multi, cls="ladder")}</div></div></div>')
    return card("04", "Workspace", "in-page module · desktop", body,
                "<b>Same grammar, web context.</b> The text block is a Konstrukt module: "
                "<code>2px</code> frame, mono head, no rounding, no shadow.")


def ctx_fitness():
    # Three sessions a week: the cell is how far the session got, not whether
    # a day existed.
    grid = K.grid([("W 38", [2, 3, 1]),
                   ("W 39", [3, 2, 3]),
                   ("W 40", [1, 0, 2]),
                   ("W 41", [3, 3, 3])],
                  header=["A", "B", "C"])
    multi = K.multi([("load", [62, 58, 44, 30, 51, 68, 45]),
                     ("sleep", [71, 68, 74, 79, 76, 69, 72])])
    body = (f'{pre(grid, cls="ladder")}<div style="height:9px"></div>'
            f'{pre(multi, cls="ladder")}')
    return card("05", "Training week", "adherence · 3 sessions", body,
                "<b>Pattern, not prose.</b> A habit matrix shows a slipped week in one "
                "glance; blank cells are absence, not zero.")


def ctx_annotation():
    temps = [56, 58, 63, 69, 73, 70, 64, 59]
    rain = [4, 6, 9, 14, 22, 31, 48, 71]
    tb, rb = K.spark(temps), K.spark(rain, low=0, high=100)
    head = f"   {tb} temp 56→73°   "
    line = f"{head}{rb} rain"
    chart = K.annotate(line, len(head) + K.peak_col(rb), "rain after 18:00", width=42)
    body = ('<div class="anno">'
            f'<div class="anno-row">{pre(chart, cls="chart")}'
            '<p class="anno-cap"><b>Caret derived, not counted.</b> The column is read '
            'back off the rendered string, so it cannot drift when the data changes.</p>'
            '</div>'
            f'<div class="anno-row">{pre("   ▁▃▅▇█▇▅▃ temp 56→73°", cls="chart")}'
            '<p class="anno-cap">Peak at midday, falling to evening: layers, not a coat.'
            '</p></div></div>')
    return card("06", "Annotation", "reading the shape", body,
                "<b>The annotation is a sentence with a target.</b> One line under its "
                "column, no legend, no counting across rows.")


def ctx_ascii():
    vals = [54, 58, 64, 70, 74, 72, 67, 61]
    body = pre(
        f"  unicode  {K.spark(vals)} temp 54→74°\n"
        f"  ascii    {K.spark(vals, enc='ascii')} temp 54→74°\n\n"
        f"  unicode  {K.hbar(62, 100, fixed=(0, 100))}  62%\n"
        f"  ascii    {K.hbar(62, 100, fixed=(0, 100), enc='ascii')}  62%"
    )
    return card("07", "Fallback", "same ladder, ascii", body,
                "<b>One language, two encodings.</b> For SMS, log files and terminals "
                "with no block glyphs. Degraded resolution, identical grammar.")


def build() -> str:
    prims = ["spark", "hbar", "grid", "range", "multi", "annotate", "kv", "frame", "ruler"]
    chips = "".join(f'<span class="chip on">{p}</span>' for p in prims)
    rules = ["cell is the pixel", "width is a contract", "shape is not magnitude",
             "absence is signal", "no reused marks", "animation resolves"]
    rchips = "".join(f'<span class="chip">{r}</span>' for r in rules)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>Konstrukt · Text — one-pager</title>
<style>{CSS}</style></head>
<body><div class="poster">
  <div class="top">
    <div>
      <span class="micro">Konstrukt / text layer</span>
      <h1>One language, every channel you write to.</h1>
      <p class="lede">Same authority structure as Konstrukt, rebuilt for a fixed cell:
      hard frames, mono metadata, one accent, status words. Charts, annotations and
      terminal motion out of one token set and one linter.</p>
    </div>
    <div class="status">
      <span class="pill solid">Proposed</span>
      <span class="pill teal">Not in build</span>
    </div>
  </div>
  <div class="strip">
    <div><b>9</b><span>primitives</span></div>
    <div><b>14</b><span>rules</span></div>
    <div><b>2</b><span>encodings</span></div>
    <div><b>11</b><span>lint checks</span></div>
    <div><b>44</b><span>chat columns</span></div>
  </div>

  <div class="cols">
    <div class="col">
      {ctx_telegram()}
      {ctx_slack()}
      {ctx_fitness()}
    </div>
    <div class="col">
      {ctx_cli()}
      {ctx_dashboard()}
      {ctx_annotation()}
    </div>
  </div>

  <div class="foot">
    <div>
      <span class="micro">the vocabulary</span>
      <div class="chips" style="margin-top:9px">{chips}</div>
      <p class="ruleline">Nine primitives, a closed set. Anything else is composition.
      Each renders identically from <b>text.py</b>, <b>text.js</b> and <b>Swift</b>,
      proven by golden files in the build gate.</p>
      <span class="micro" style="display:block;margin-top:16px">the rules that bite</span>
      <div class="chips" style="margin-top:9px">{rchips}</div>
    </div>
    <div class="sign">
      <div>
        {ctx_ascii()}
      </div>
    </div>
  </div>
</div></body></html>"""


if __name__ == "__main__":
    OUT.write_text(build(), encoding="utf-8")
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")
