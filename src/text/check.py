#!/usr/bin/env python3
"""Text-layer verification gate.

  1. Linter self-test (11 of 11 rules).
  2. Reference board lints clean in both encodings at the chat budget.
  3. Board render matches the committed golden file.
  4. If dist/text.py exists, it renders byte-identical to the source renderer.
  5. Review-sheet and one-pager generators produce non-empty HTML.

Run via `npm run check:text`.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
GOLDEN = ROOT / "build" / "canonical-text-board.txt"
BUDGET = 44


def _run(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd or ROOT, text=True, capture_output=True)


def _fail(message: str, proc: subprocess.CompletedProcess | None = None) -> int:
    print(message, file=sys.stderr)
    if proc is not None:
        if proc.stdout:
            sys.stderr.write(proc.stdout)
        if proc.stderr:
            sys.stderr.write(proc.stderr)
    return 1


def main() -> int:
    sys.path.insert(0, str(SRC))
    from text.lint import EXPECTED_RULES, SEEDED, lint  # noqa: E402
    from text.renderer import render_board  # noqa: E402

    hits = lint(SEEDED, budget=BUDGET)
    caught = {rule for rule, _, _ in hits}
    missing = EXPECTED_RULES - caught
    if missing:
        return _fail(f"linter self-test missed {sorted(missing)}")
    print(f"linter self-test OK ({len(caught)} of {len(EXPECTED_RULES)})")

    for enc in ("unicode", "ascii"):
        board = render_board(enc)
        findings = lint(board, budget=BUDGET)
        if findings:
            for rule, n, msg in findings:
                print(f"{enc} {rule:<4} line {n}: {msg}", file=sys.stderr)
            return _fail(f"reference board ({enc}) failed lint")
        print(f"board {enc} clean at budget {BUDGET}")

    rendered = render_board("both") + "\n"
    if not GOLDEN.is_file():
        return _fail(f"missing golden file: {GOLDEN}")
    expected = GOLDEN.read_text(encoding="utf-8")
    if rendered != expected:
        return _fail(
            f"board render drifted from {GOLDEN.relative_to(ROOT)} "
            f"({len(rendered)} bytes vs {len(expected)} bytes)"
        )
    print(f"golden board matches {GOLDEN.relative_to(ROOT)}")

    dist_py = ROOT / "dist" / "text.py"
    if dist_py.is_file():
        proc = _run([sys.executable, str(dist_py), "--encoding", "both"])
        if proc.returncode != 0:
            return _fail("dist/text.py failed to render the board", proc)
        if proc.stdout != expected:
            return _fail("dist/text.py board does not match the source renderer")
        print("dist/text.py matches the source renderer")
    else:
        print("dist/text.py not built; skip generated-renderer check")

    for script, dest in (
        (ROOT / "scripts" / "text_onepager.py", Path("/tmp/konstrukt-text-onepager.html")),
        (ROOT / "scripts" / "text_board_page.py", Path("/tmp/konstrukt-text-board.html")),
    ):
        proc = _run([sys.executable, str(script), str(dest)])
        if proc.returncode != 0 or not dest.is_file() or dest.stat().st_size == 0:
            return _fail(f"{script.name} did not write {dest}", proc)
        print(f"{script.name} wrote {dest} ({dest.stat().st_size} bytes)")

    print("text layer check passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
