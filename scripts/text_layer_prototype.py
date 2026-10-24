#!/usr/bin/env python3
"""Print the Konstrukt · Text review board.

Thin wrapper around the shipped renderer. Prefer `python3 dist/text.py` after
`npm run build`; this entry point keeps the original command working.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from text.renderer import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
