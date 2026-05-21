from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def main() -> int:
    # Keep routing transparent so add/import/history and cloze payloads stay CLI-owned.
    return subprocess.call([str(ROOT / "bin" / "tutor"), *sys.argv[1:]])


if __name__ == "__main__":
    raise SystemExit(main())
