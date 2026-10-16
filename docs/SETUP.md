# Local rendering setup

The repository contains the guide and media library, but a playable MP4 still needs a working local FFmpeg toolchain. Check the machine first; do not reinstall tools that already work.

## 1. Initialize the upstream source

From the repository root:

```bash
git submodule update --init --recursive
```

## 2. Python dependencies

Use Python 3.11 or newer. From the repository root:

```bash
python -m venv .venv
# Linux/macOS
. .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements-video.txt
```

The included `tools/render.py` adapter handles one Python 3.11 parsing issue in the pinned upstream renderer without changing the submodule. Arena's built-in speech tool is used for narration, so Kokoro, Kaggle, ElevenLabs and Flow are not prerequisites for the Arena workflow.

## 3. FFmpeg and complex-script captions

Install FFmpeg using the operating system's trusted package manager (for example, `winget install Gyan.FFmpeg` on Windows, `brew install ffmpeg` on macOS, or `sudo apt install ffmpeg` on Debian/Ubuntu). Verify that both commands work:

```bash
ffmpeg -version
ffprobe -version
ffmpeg -hide_banner -filters
```

The FFmpeg build must include the `ass` filter (libass) and `shaping=complex` support for correct Bengali/Indic text. If it does not, use a full FFmpeg build that includes libass; do not render a Bengali master with broken conjuncts.

For Bengali titles, install a Bengali-capable font (for example Noto Sans Bengali) and set `VOX_FONT` to its installed font family name before rendering. Verify the actual font is found by the local libass/Fontconfig installation.

## 4. Smoke checks

From the repository root:

```bash
python tools/render.py --syntax-check
python third_party/vox-doc/skills/vox-doc-sound/scripts/mix.py --selfcheck
```

After entering an actual `projects/<slug>/` folder, run the renderer's `plan` first. `render.py shots` and `render.py master` need the project's TSVs/assets, the Python packages, and FFmpeg; do not treat the smoke checks as proof that a finished video has rendered.

## Audio catalog

The bundled library's `CATALOG.tsv` is generated metadata, not a prebuilt file. Once FFmpeg and Python dependencies are ready, run:

```bash
python third_party/vox-doc/skills/vox-doc-sound/scripts/index_sfx.py
```

It writes the catalog alongside the upstream sound skill, so it can remain a local untracked artifact inside the submodule. Re-run it after adding media. Always read and honor the sound/music license files before use.
