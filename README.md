# Vox Doc — Arena Edition

এই repo-তে Vox-style editorial explainer video তৈরির পূর্ণ workflow যুক্ত করা হয়েছে। মূল guide, Python renderer/keyer, TSV examples এবং bundled sound/music library রাখা আছে upstream GitHub repository-র pinned submodule হিসেবে:

- Upstream: `https://github.com/Prattush07/vox-doc`
- Pinned revision: `6a40f93a316af4f10109733d35fa2546f645edfd`
- Local path: `third_party/vox-doc/`

## কী আছে

- Script → voiceover → word timing → storyboard → images → edit/render → sound mix → final QC—সম্পূর্ণ pipeline
- Editorial illustration style, word-synced visuals, maps/pins, code-drawn clocks/charts/data, labels ও rendering examples
- Sound-effect ও ambience catalog, music assets, indexing/mixing scripts এবং তাদের license files
- Arena-তে built-in image/speech tools ব্যবহার করার নির্দেশনা (`AGENTS.md`, `docs/WORKFLOW.md`)
- `WORDS.tsv` থেকে aligned external Hindi SRT তৈরির helper: `tools/build_japan_captions.py`
- ব্যবহারকারী-অনুমোদিত Hindi Version B script: `content/japan-savings-habits/SCRIPT.md`

বড় audio/music assets parent repo-তে আরেকবার কপি করা হয়নি; submodule থেকেই পাওয়া যায়। Generated video projects `projects/<slug>/`-এ থাকবে এবং ইচ্ছাকৃতভাবে Git থেকে বাদ।

## নতুন clone-এ source আনুন

```bash
git submodule update --init --recursive
```

তারপর প্রথম ভিডিওর আগে পড়ুন:

1. `AGENTS.md`
2. `docs/SETUP.md` (যদি locally render করতে চান)
3. `docs/WORKFLOW.md`
4. `third_party/vox-doc/skills/vox-doc/PLAYBOOK.md`
5. `third_party/vox-doc/skills/vox-doc-sound/SKILL.md`

Arena-র workflow-তে ছবি ও narration তৈরির জন্য built-in tools ব্যবহার হবে। Upstream-এর `CLAUDE.md` installer ও Google Flow setup Claude Code-এর জন্য—Arena-তে সেগুলো চালানোর প্রয়োজন নেই।

## Rendering prerequisites

Final MP4 render করতে Python 3.11+, `requirements-video.txt`-এর packages এবং `ffmpeg`/`ffprobe`-এর `ass` filter দরকার। Setup ও smoke-check-এর নির্দেশনা `docs/SETUP.md`-এ আছে. Runtime-এ এগুলো সত্যিই উপলভ্য কি না কাজ শুরুর আগে যাচাই করুন।

## License

Upstream assets-এর license files যথাস্থানে আছে। ব্যবহারের আগে সেগুলো পড়ুন; সব third-party sound/music-এর অধিকার এক নয়।
