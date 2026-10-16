# Project progress — Japan savings habits

- **Current stage:** Complete. The final Hindi Vox-style master was rendered and QC'd; the generated project and media remain in the Git-ignored `projects/japan-savings-habits/` directory.
- **Brief:** Approved Version B for an Indian audience, Hindi in Devanagari, selected masculine `voice-02` entertainment narration, target duration over 10 minutes.
- **Narration:** 631.76 seconds (10:31.76), 138 sentence timing rows and 1,894 word timing rows. Word and sentence timings are estimated proportionally within speech chunks, not forced-aligned.
- **Master:** `projects/japan-savings-habits/japan-savings-habits.mp4` — 632.71 seconds (10:32.71), 1920×1080, 24 fps, H.264 video and AAC stereo audio. A companion Hindi SRT contains 221 cues through 631.76 seconds.
- **Visuals:** 120 animated scenes and 393 scene cues, including 40 opening continuity holds. Nine supplementary cut-out illustrations were generated; 29 assets are registered. Scene 106's ₹500 chart bar was corrected to remain a short vertical zero-based bar.
- **Audio QC:** Mix measured −14.1 LUFS integrated, 3.2 LU LRA and −1.5 dBFS true peak; the AAC master measured −14.1 LUFS, 3.2 LU LRA and −1.3 dBFS true peak.
- **Fact-check:** ₹13,000 is a hypothetical household example, not an average or promised saving. Categories avoid double counting; kintsugi/repair has no fixed monthly amount. Removed an unsupported “20% household food waste” claim, clarified that the 24-hour pause and batch-cooking routine are practical suggestions rather than ancient traditions, distinguished modern danshari from older Japanese practices, and included the small/context-dependent cashless-spending research caveat.
- **QC artifacts:** `projects/japan-savings-habits/qc/master-contact.jpg`, `qc/contact-01.jpg`–`contact-08.jpg`, `qc/full/`, and `qc/continuity-contact.jpg`.
- **Repository note:** Generated audio, images, shots, QC frames and the final MP4 are intentionally excluded from Git via `.gitignore`; the PR contains the workflow, reusable tools and approved script, not the large rendered media.
