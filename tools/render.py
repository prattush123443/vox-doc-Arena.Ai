#!/usr/bin/env python3
"""Arena-compatible entry point for the pinned upstream Vox Doc renderer.

The pinned upstream render.py contains a nested f-string that Python 3.11
cannot parse (it is accepted by Python 3.12+). Apply the one-line compatibility
rewrite in memory, then execute the upstream renderer unchanged. This keeps the
third_party submodule clean and makes no assumptions about the project's CWD.
Run this script from inside projects/<slug> just as you would run upstream
render.py: python ../../tools/render.py plan|shots|master.
"""
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = REPO_ROOT / "third_party/vox-doc/skills/vox-doc/scripts/render.py"

if not UPSTREAM.is_file():
    raise SystemExit(
        f"Missing upstream renderer: {UPSTREAM}\n"
        "Initialize the submodule with: git submodule update --init --recursive"
    )

source = UPSTREAM.read_text(encoding="utf-8")
old = r'''            f.write(f"file '{os.path.abspath(f'{SHOTS}/{s['id']}.mp4')}'\n".replace("\\", "/"))'''
new = r'''            path = os.path.abspath(os.path.join(SHOTS, f"{s['id']}.mp4")).replace("\\", "/")
            f.write(f"file '{path}'\n")'''
if old in source:
    source = source.replace(old, new, 1)

try:
    code = compile(source, str(UPSTREAM), "exec")
except SyntaxError as exc:
    raise SystemExit(
        f"The upstream renderer has an incompatible syntax error at {exc.lineno}: {exc.msg}. "
        "Check the pinned Vox Doc source before rendering."
    ) from exc

if "--syntax-check" in sys.argv[1:]:
    print("upstream render.py syntax OK (Arena compatibility applied in memory)")
    raise SystemExit(0)

# Upstream renderer reads/writes project files relative to the current directory.
# Keep the caller's arguments intact; only the source file's __file__ is changed.
exec(code, {"__name__": "__main__", "__file__": str(UPSTREAM)})
