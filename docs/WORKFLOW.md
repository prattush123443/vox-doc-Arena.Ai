# Vox-style documentary video workflow (Arena)

এই repo-তে upstream `Prattush07/vox-doc`-এর পূর্ণ playbook, উদাহরণ, renderer, sound-design tools এবং bundled sound/music assets `third_party/vox-doc/` submodule-এ রাখা আছে। Submodule-টি নির্দিষ্ট commit-এ pin করা; upstream-এর সম্পূর্ণ গাইড ওই ফোল্ডারেই। নতুন ভিডিওর আগে `AGENTS.md` এবং নিচে দেওয়া upstream playbook-গুলো পড়ুন।

> এই workflow-তে “Vox-style” বলতে editorial explainer-এর ভিজ্যুয়াল ভাষা বোঝায়—Vox-এর logo/branding নকল করা নয়। Arena-তে ছবি ও কথার অডিও তৈরির জন্য built-in image/speech tools ব্যবহার হবে; upstream-এর Google Flow installer নয়।

## স্টাইলের মূল নিয়ম

- **কথা আর ছবি একই মুহূর্তে মিলবে।** narration-এ যে শব্দে একটি জায়গা, বস্তু বা সংখ্যা আসে, সেই word cue-তে তার visual আসবে। অনুমান করে line-level timing নয়—`WORDS.tsv` থেকে word-level timing ব্যবহার করুন।
- **প্রতিটি গুরুত্বপূর্ণ noun-এর নিজস্ব ছবি।** একই generic icon বারবার ব্যবহার করবেন না। ছবি না থাকলে নতুন asset তৈরি করুন।
- **সুনির্দিষ্ট তথ্য code-এ আঁকুন।** ঘড়ি, তারিখ, সংখ্যা, চার্ট, axis, counter, pin ও route AI artwork-এ আঁকবেন না; সেগুলি exact value-সহ renderer/code-এ আঁকুন।
- **প্রতিটি ছবিতে ছোট label।** সংখ্যা ও তথ্য narration, graphic এবং caption—তিন জায়গায় এক অর্থে থাকবে। Bengali/অন্যান্য জটিল লিপিতে সঠিক font ও complex shaping যাচাই করুন।
- **দেখার সময় দিন।** প্রতিটি reveal, clock sweep বা বড় পরিবর্তন কাটের আগে অন্তত 0.7 সেকেন্ড ধরে রাখুন। label যেন frame-এর বাইরে না যায় বা অন্য কিছুর সঙ্গে না মেলে।
- **একই visual palette।** 16:9, 1920×1080, 24 fps; উষ্ণ cream/paper background, সূক্ষ্ম grain/vignette, রাতের দৃশ্যে dark navy, সংযত red/yellow accent; cut-out editorial illustration-এ পাতলা dark outline ও muted vintage রং। প্রতিটি বিষয়ে palette-টি ধারাবাহিক রাখুন।
- **QC বাধ্যতামূলক।** প্রতিটি scene-এর শেষ frame-সহ contact sheet দেখে ছবির অর্থ, label, overlap, map pin এবং সংখ্যার যথার্থতা ঠিক করুন; শেষে পুরো ভিডিও sound-সহ দেখুন।

## কাজের ধাপ

1. **Script:** ব্যবহারকারীর script ও ভাষা ধরে রাখুন; প্রয়োজন হলে fact-check করুন। Hook → context/facts → সমস্যা/খরচ → তুলনা → প্রশ্ন/reframe → reveal → closing কাঠামো কেবল উপযুক্ত হলে নিন। `SCRIPT.md` এবং `LINES.tsv` (`id`, `text`, `gap`) তৈরি করুন; script অনুমোদনের checkpoint দিন।
2. **Voice:** Arena-র `add_voice` দিয়ে 30–45 শব্দের audition দিন, ব্যবহারকারীকে পছন্দ করতে দিন, তারপর নির্বাচিত `voice_id`-এর `generate_speech` ব্যবহার করুন। একেক লাইনের WAV `takes/NN.wav` হিসেবে রাখুন। `generate_speech` শুধু spoken narration—music বা SFX তৈরি করে না।
3. **Join ও timing:** upstream `vo_join.py` দিয়ে `VO.wav`/`VO.tsv` বানান, তারপর sound skill-এর `align.py` দিয়ে `WORDS.tsv` বানান। লাইন ভুল align হলে আগে ঠিক করুন।
4. **Storyboard:** `SCENES.tsv`, `ELEMENTS.tsv`, প্রয়োজনে `PLACES.tsv` লিখুন। দৃশ্যের ক্রম narration থেকে আসবে—আগে থেকে ইচ্ছামতো shot list নয়। প্রতি লাইনে সাধারণত 2–4টি অর্থবহ visual যথেষ্ট।
5. **Image assets:** Arena-র image tool দিয়ে `ELEMENTS.tsv`-এর প্রতিটি asset আলাদাভাবে তৈরি করুন। Contact sheet/montage নয়, ছবির ভেতরে লেখা নয়। প্রস্তাবিত prompt-এর ভিত্তি:

   ```text
   [specific object and period/place], bold flat editorial vector illustration,
   thin dark outline, warm muted vintage palette, one isolated object centered
   with generous margin, crisp edges, no text, no letters, no numbers, no logo,
   no shadow; uniform pure magenta #FF00FF background for clean cut-out.
   ```

   বস্তুটি যেন নির্দিষ্ট হয় (উদাহরণ: “a tea worker plucking leaves in a tea garden”, শুধু “worker” নয়)। generated image `elements/raw/<id>.png`-এ রাখুন; upstream `key.py` দিয়ে `elements/cut/<id>.png`-এ transparent cut-out বানিয়ে দেখে নিন। `elements.py` ব্যবহার করবেন না—ওটি Google Flow-র উপর নির্ভর করে।
6. **Edit/render:** project folder থেকে `python ../../tools/render.py plan` দিয়ে cue সময় পরীক্ষা করুন, `python ../../tools/render.py shots` দিয়ে shots render করুন; contact sheet QC শেষে `python ../../tools/render.py master` দিয়ে master render করুন। Wrapper-টি upstream-এর একটি nested f-string Python 3.11-এ চালানোর আগে memory-তে সামঞ্জস্য করে; submodule-এ কোনো পরিবর্তন করে না। Bengali text-এর জন্য Bengali glyph-সমর্থিত font (যেমন system-এ ইনস্টল করা `Noto Sans Bengali`) `VOX_FONT`-এ দিন, এবং `ass=...:shaping=complex` shaping-সহ render যাচাই করুন।
7. **Sound:** `third_party/vox-doc/skills/vox-doc-sound/sfx/` ও `music/` থেকে মিলিয়ে file বেছে নিন। প্রথমবার/asset বদলালে `index_sfx.py` চালিয়ে catalog বানান। `cues.tsv`-তে catalog-এর আসল filename ও word cue ব্যবহার করুন। Voice যেন সবসময় পরিষ্কার শোনা যায়—music নরমভাবে (প্রায় −23 dB), ambience প্রায় −14 থেকে −17 dB, ছোট accent প্রায় −19 থেকে −21 dB; অকারণে প্রতি cut-এ whoosh নয়। এক ভিডিওতে এক palette, প্রতি 3–4 সেকেন্ডে সর্বোচ্চ এক accent, act change-এ মোট 3–5 whoosh-এর বেশি নয়। Trailer boom/braam, cartoon বা meme SFX ব্যবহার করবেন না। উপযুক্ত শব্দ না থাকলে ভুল শব্দ বসাবেন না; নীরব রাখুন বা ব্যবহারকারীকে জানান।
8. **Mix/QC/delivery:** upstream `mix.py` দিয়ে voice ducking-সহ final mix করুন; লক্ষ্য প্রায় −14 LUFS integrated এবং true peak −1.5 dBTP বা তার কম। Hook, ব্যস্ত অংশ ও reveal শুনে দেখুন; তারপর পুরো MP4 sync-সহ দেখুন। সত্যিকারের render করা ফাইল থাকলেই সেটি final বলে জানান ও `present_file` দিয়ে খুলুন।

## প্রজেক্ট ফোল্ডার ও setup

Generated project ও বড় output `projects/<slug>/`-এ রাখুন; `.gitignore`-এ এই ফোল্ডার বাদ দেওয়া আছে। একটি project-এ অন্তত `PROGRESS.md`, `SCRIPT.md`, `LINES.tsv`, `VO.wav`, `VO.tsv`, `WORDS.tsv`, `SCENES.tsv`, `ELEMENTS.tsv`, `cues.tsv` এবং final MP4 রাখুন। Project directory থেকে script চালান:

```bash
python ../../third_party/vox-doc/skills/vox-doc-sound/scripts/vo_join.py takes LINES.tsv --out VO
python ../../third_party/vox-doc/skills/vox-doc-sound/scripts/align.py --vo VO.wav --lines VO.tsv --out WORDS.tsv --lang bn
python ../../third_party/vox-doc/skills/vox-doc/scripts/key.py elements/raw elements/cut
python ../../tools/render.py plan
python ../../tools/render.py shots
python ../../third_party/vox-doc/skills/vox-doc-sound/scripts/mix.py cues.tsv --vo VO.wav --lines VO.tsv --words WORDS.tsv --out mix.wav
python ../../tools/render.py master
```

`--lang bn` Bengali narration-এর উদাহরণ; অন্য ভাষায় সঠিক code দিন। `key.py` কেবল magenta/white-background source image-এর জন্য; Arena tool যদি ইতিমধ্যে transparent PNG দেয়, keying বাদ দিয়ে file-টি `elements/cut/<id>.png`-এ রাখুন। `mix.py`-এর cue filename `CATALOG.tsv`-এর actual path হতে হবে।

নতুন clone-এ upstream assets আনতে:

```bash
git submodule update --init --recursive
```

Core renderer-এর জন্য Python 3.11+ ও `requirements-video.txt`-এর packages লাগবে। এছাড়া FFmpeg/ffprobe-এ `ass` filter থাকতে হবে। FFmpeg না থাকলে final MP4 render সম্ভব নয়—প্রথমে runtime যাচাই করুন; অসম্পূর্ণ asset-কে final video বলে দেবেন না।

Bundled audio/music-এর license আলাদা করে দেখুন:

- `third_party/vox-doc/skills/vox-doc-sound/sfx/StableAudio/LICENSE.md`
- `third_party/vox-doc/skills/vox-doc-sound/sfx/Kenney_CC0/LICENSE_CC0.txt`
- `third_party/vox-doc/skills/vox-doc-sound/music/Gemini/LICENSE.md`

কোনো third-party pack-এর শর্ত bundled pack-এর মতো ধরে নেবেন না। API key/password কখনো chat-এ চাইবেন বা project file-এ রাখবেন না।

## পূর্ণ upstream নির্দেশিকা

- `third_party/vox-doc/skills/vox-doc/PLAYBOOK.md` — সম্পূর্ণ storyboarding ও rendering method
- `third_party/vox-doc/skills/vox-doc/SKILL.md` — end-to-end video stages
- `third_party/vox-doc/skills/vox-doc/SETUP.md` — upstream machine setup (Arena-র জন্য Flow/Claude Code ধাপ বাদ দিয়ে)
- `third_party/vox-doc/skills/vox-doc-sound/SKILL.md` — narration, sound design, mix ও QC
- `third_party/vox-doc/skills/vox-doc-sound/music/README.md` — music library ও prompt guide
