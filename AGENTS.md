# Vox Doc — instructions for Arena agents

## Source of truth

- The upstream Vox Doc project is installed as the Git submodule `third_party/vox-doc`, pinned to commit `6a40f93a316af4f10109733d35fa2546f645edfd`.
- Before making a video, read these files in full:
  - `third_party/vox-doc/skills/vox-doc/PLAYBOOK.md`
  - `third_party/vox-doc/skills/vox-doc/SKILL.md`
  - `third_party/vox-doc/skills/vox-doc-sound/SKILL.md`
  - `third_party/vox-doc/skills/vox-doc-sound/music/README.md`
  - Relevant examples under `third_party/vox-doc/skills/vox-doc/example/` and `.../vox-doc-sound/examples/`.
- Treat `third_party/vox-doc/CLAUDE.md` and its global installer/Flow Connector steps as instructions for **Claude Code only**. Do not install global Claude skills or depend on `flow-auto` in Arena. Use Arena's built-in image and speech tools for creative assets; use the upstream renderer, keyer, examples, sound library, and playbook where compatible.
- Keep the submodule pinned. Do not edit or stage changes inside it; make Arena-specific changes in this repository.

## When the user gives a video script

Answer in Bengali when the user writes in Bengali. Preserve the script's language and wording. Do not silently rewrite an approved script or invent facts. If an essential choice is missing, ask briefly (for example: voice gender, aspect ratio, or target duration). Follow the user's explicit request to proceed; the script/voice checkpoints in the playbook still apply.

Create each video under `projects/<short-lowercase-slug>/`. That directory is intentionally ignored by Git because it contains generated media. Maintain a `PROGRESS.md` there so the work can resume. A useful layout is:

```text
projects/<slug>/
  PROGRESS.md  SCRIPT.md  LINES.tsv
  takes/                 # one generated narration take per line
  VO.wav  VO.tsv  WORDS.tsv
  SCENES.tsv  ELEMENTS.tsv  PLACES.tsv
  elements/raw/ elements/cut/
  cues.tsv  mix.wav  shots/  <slug>.mp4
```

Run the upstream scripts with the project directory as the working directory. Their paths are under `../../third_party/vox-doc/skills/` from a `projects/<slug>/` folder.

## Required production order

1. **Script and approval.** Divide the approved narration into short, speakable lines. Save the script as `SCRIPT.md` and a tab-separated `LINES.tsv` with `id`, `text`, and `gap`. Use the playbook's hook → explanation/context → problem or cost → comparison → question/reframe → reveal → closing structure when it fits; do not force it onto a script that has a different approved structure. Check factual claims when appropriate and clearly flag anything uncertain.
2. **Voice audition and narration.** Use Arena's `add_voice` tool before `generate_speech`; the user must select an auditioned voice. Use narration/educational delivery, the script's language, and about 30–45 words from the actual script for the audition. Do not synthesize until a voice has been selected. Use the selected `voice_id` consistently. `generate_speech` is spoken-word only, supports up to 1,500 characters per call, and is capped at 10 clips per turn; split long scripts at sentence boundaries and continue in later turns if needed. Save individual takes as WAV files named by line ID, then join them with the upstream `vo_join.py` to produce `VO.wav` and `VO.tsv`. Do not use the speech tool for music or sound effects.
3. **Word timing.** Align the approved narration with the actual audio, not estimated durations. Use the upstream sound `align.py` to make `WORDS.tsv`; check badly aligned lines before planning visuals or cues.
4. **Scene and asset plan.** Write `SCENES.tsv` from the narration and word timings, plus `ELEMENTS.tsv` for distinct, bespoke visual assets and `PLACES.tsv` for map coordinates. Use word cues so an item appears when it is named. Follow the upstream examples. Draw exact data—clocks, numbers, charts, pins, axes—in code, never in AI artwork. Label every visual, keep essential content inside the safe area, and hold a reveal/motion long enough to read (at least 0.7 seconds).
5. **Images with Arena's built-in image tool.** Generate one standalone image per `ELEMENTS.tsv` asset; do not request collages, contact sheets, or text baked into an image. These are internal assets for a larger video, so use `offer_options=false`. Use a consistent prompt style: **bold flat editorial vector illustration, thin dark outline, warm muted vintage palette, one isolated object, generous margin, crisp edges, no text/letters/numbers, no logo, no drop shadow**. For cut-outs, request a uniform pure-magenta `#FF00FF` background with no magenta in the object, then use the upstream `key.py` on `elements/raw/` to create transparent PNGs in `elements/cut/`. Inspect every result and regenerate poor or duplicated images. Do not run upstream `elements.py`: it requires Google Flow and is not the Arena image tool. Use filenames matching the IDs expected by `render.py`.
6. **Edit and render.** Use the upstream Python/Pillow + FFmpeg renderer, not a promise of an unrendered video. The reference look is 1920×1080, 24 fps, cream paper with fine grain/vignette, dark navy for night scenes, restrained red/yellow accents, labeled cut-out art, code-drawn data, and map pins. Run `python ../../tools/render.py plan`, render shots with `python ../../tools/render.py shots`, inspect a contact sheet of scene end frames for wrong images, overlaps, cut-off labels, and incorrect data, fix and re-render, then render the master with `python ../../tools/render.py master`. The wrapper applies a Python 3.11 compatibility fix in memory for one upstream nested f-string; it does not modify the submodule. Burn in complex-script captions using the upstream renderer's `ass=...:shaping=complex` path.
7. **Sound design and mix.** Use the bundled sound/music library in `third_party/vox-doc/skills/vox-doc-sound/` and obey its licenses. Index it with `scripts/index_sfx.py` if `CATALOG.tsv` is absent or the library changed. Build `cues.tsv` from actual word timings and catalog filenames. Keep narration intelligible: one quiet accent per meaningful beat at most, generally no more than one every 3–4 seconds; only 3–5 act-change whooshes in a video; a single consistent sound palette; no trailer booms, braams, meme sounds, or unnecessary whooshes. The hook starts dry or with quiet ambience; music enters gently (about −23 dB under voice); ambience is subtle. Use silence deliberately. Do not substitute an unrelated sound when no appropriate file exists—say it is missing and leave the moment quiet or ask the user. Mix and QC to the upstream target (about −14 LUFS integrated, true peak no higher than −1.5 dBTP) and listen to the hook, busiest section, and reveal.
8. **Final QC and delivery.** Watch the entire rendered MP4 with sound, verify duration and audio/video sync, then present the real MP4 with `present_file` and give its path. Also provide a concise cue-sheet summary, deliberate silences, final loudness, and any limitations. Never call a render complete unless the output file exists and has been checked.

## Runtime, assets, and privacy

- A real MP4 render requires FFmpeg/ffprobe (including the `ass` filter) and the Python packages listed in `requirements-video.txt`. Check the current runtime before starting; if a prerequisite is missing, say what is missing and either set it up safely or deliver only the completed stages. Never claim it is installed just because it is documented.
- The current environment may not retain an external audio-tool voice selection between conversations. Register a new voice with `add_voice` when no valid selected `voice_id` is available in the current session.
- The upstream sound pack includes its own license files: `sfx/StableAudio/LICENSE.md`, `sfx/Kenney_CC0/LICENSE_CC0.txt`, and `music/Gemini/LICENSE.md`. Read and follow them before reuse. Third-party or generated audio can have different restrictions; do not claim blanket commercial rights. Do not redistribute ElevenLabs, Pixabay, or purchased files as a sound pack.
- Never ask the user to paste passwords, API tokens, or secret keys into chat. Do not put secrets in project files or output artifacts.
- Keep finished videos and bulky generated media under ignored `projects/`; do not commit them unless the user specifically asks.
