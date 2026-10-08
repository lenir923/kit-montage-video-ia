---
name: youtube-long-form
description: Edit a long-form YouTube tutorial recorded as TWO files (face cam + screen recording) into a clean Nate-Herk-style video - take selection against the script, silence and mistake cuts, automatic face-cam / screen layout switching, purposeful zooms, HyperFrames motion graphics, rendered section by section. Use for any "montage YouTube format long", "tuto écran + face cam", or when a project folder holds a cam file and a screen file. Builds on edit-video, cut-silences, cut-mistakes, video-storytelling and hyperframes-video-beats; this skill adds the two-source plumbing and the layout/zoom grammar they lack.
---

# Long-form YouTube edit, two sources

The kit's cutting tools assume ONE video. Here there are two: the face cam (it
carries the master audio) and the screen recording (with or without its own audio).
Rule of the whole pipeline: **the raw cam timeline is the reference**.
Every decision is expressed on it, composed into one timeline, and both sources are
cut once, frame-accurately, by `scripts/dual_edit.py`. Never cut the two files
separately, never render the kit's intermediate videos (plan-only mode).

Python scripts need Python 3 and numpy. Run them with `uv run --with numpy python <script>`
(or plain `python3` when numpy is installed). Read `references/layouts-and-zooms.md`
before planning visuals.

## Pipeline

All paths relative to the project folder `video-projects/<slug>/` (create it with
`npm run new-video -- <slug>`, raw files in `assets/raw/`, script and notes in `brief/`).
S = `../../.claude/skills/youtube-long-form/scripts`, K = `../../.claude/skills`.

1. **Prepare** (about 40 min for 45 min of iPhone HLG, run in background):
   `python3 $S/prep_sources.py --cam assets/raw/<cam> --screen assets/raw/<screen> --out assets`
   Test first with `--test 20` in a temp folder, look at a frame, decide on `--grade`.
   Output: `assets/cam.mp4` (upright, SDR, 30 fps), `assets/screen.mp4` (30 fps, native res), `assets/cam.wav`,
   `assets/screen.wav` (only when the screen recording has audio), `assets/sources.json`.
2. **Transcribe** the cam with word timestamps. Default: ElevenLabs Scribe through fal.ai
   (`FAL_KEY` in the kit's `.env`, about 1-2 USD for 45 min, cached per chunk):
   `uv run python $S/transcribe_scribe.py assets/cam.wav assets/raw.json`
   Alternatives: the kit's ElevenLabs helper (`ELEVENLABS_API_KEY`, run from the kit root:
   `npm run transcribe -- video-projects/<slug>/assets/cam.mp4 --language fr --output video-projects/<slug>/assets/raw.json`)
   or local Whisper (see `docs/TOOLS-AND-API-KEYS.md`). Whatever the provider, the
   output must be the kit's common format on the cam timeline.
3. **Map the screen**: `uv run --with numpy python $S/screen_map.py assets/screen.mp4 analysis`
   Then LOOK at every `analysis/sheets/*.jpg` and write `analysis/screen-segments.md`: screen time ranges labelled with what is visible (chat window, spreadsheet, code editor, teleprompter, desktop, file browser...) and a SHOWABLE yes/no.
4. **Sync**. Convention everywhere: `cam_time = screen_time + offset`.
   - **Screen recorded with its own audio** (recommended: record the screen with the
     mic on). Audio against audio, it also measures clock drift between the two devices:
     `uv run --with numpy python $S/sync_audio.py --cam assets/cam.wav --screen assets/screen.wav --sources assets/sources.json --out analysis/sync.json`
     Read the probes: z-scores should be high (above 8) and the offsets aligned on a
     line. `dual_edit.py cut` applies `offset0` + `drift` automatically.
   - **Silent screen recording**: say a countdown out loud ("trois, deux, un, maintenant")
     when you start the screen recording. After the transcript:
     `uv run --with numpy python $S/sync_screen.py --sources assets/sources.json --activity analysis/activity10hz.npy --transcript assets/raw.json --out analysis/sync.json`
     The script finds the countdown, otherwise it falls back on metadata. Read
     `anchor_check`: action words ("j'envoie", "je glisse"...) should be followed by a
     screen change, median residual between 0 and +0.5 s. Keyboard/screen
     cross-correlation (`--cam-audio`) is a weak diagnostic only.
   In both cases verify by eye at 2-3 action moments (frame of the screen at
   `cam_time - offset`), adjust with `--offset X --note "..."` if needed, and write the
   check in VERIFY.md.
5. **Select** (editorial, the part that makes or breaks the video). Read the script and the production notes, then the transcript. Speakers who read a teleprompter restart sentences: for every script paragraph find all takes in `raw.json`, keep the best complete one (usually the LAST clean one), drop set-up chatter, tests, off-script asides, dead waits. Write `work/selects.json` (format in `dual_edit.py`), sections named `NN-name` in playback order. Screen-only moments without speech that must stay (Claude generating, a table appearing) are `timelapse` items (`speed` 4-12, or `speed: 1` to keep a silent action at normal pace with its sound). An already rendered video to play full screen (a demo, an ad, a showreel) is a `gap` item (`{"kind": "gap", "duration": 18.5, "media": "...", "section": "..."}`): a silent hole on the timeline, the composition plays the media on top.
   `uv run --with numpy python $S/dual_edit.py select --transcript assets/raw.json --selects work/selects.json --out work`
6. **Silences and mistakes** with the kit, plan-only (never `--video`, never `--apply`):
   `node $K/cut-silences/scripts/cut-silences.mjs work/sel.transcript.json --out-dir work`
   `node $K/cut-mistakes/scripts/find-cut-candidates.mjs work/sel.silence-transcript.json --out-dir work`
   Review every candidate in context (cut-mistakes/SKILL.md), write `work/approved-cuts.json`, then
   `node $K/cut-mistakes/scripts/apply-cuts.mjs work/sel.silence-transcript.json --cuts work/approved-cuts.json --out-dir work`
7. **Compose + cut** both sources in one pass:
   `uv run --with numpy python $S/dual_edit.py compose --map work/sel.map.json --silence-edl work/sel.silence-edl.json --mistakes-edl work/sel.mistakes-edl.json --transcript assets/raw.json --out work`
   `uv run --with numpy python $S/dual_edit.py cut --timeline work/timeline.json --cam assets/cam.mp4 --screen assets/screen.mp4 --voice assets/cam.wav --sync analysis/sync.json --out assets/edit`
   Result: `assets/edit/{cam.mp4,screen.mp4,voice.wav}` + one folder per section + `sections.json`, and `work/final.transcript.json` on the output timeline (use it for beats, captions, beat-sync validation).
   Re-running after a change only re-renders missing piece files: delete `assets/edit/pieces` when the timeline changed.
8. **Global art direction, then layout + zoom plan**: fix ONE art direction for the whole video first (DESIGN.md: background, frames, palette, type, motion language, sound) and hold every section to it. Then write `work/visual-plan.md` per section: shot list on the output timeline (layout, zoom target and timing, transitions), then the beat sheet (video-storytelling + hyperframes-video-beats). Grammar and rules: `references/layouts-and-zooms.md`.
9. **Build and render section by section**: one HyperFrames composition per section, using that section's `assets/edit/sections/<s>/` files (muted videos, animate a non-timed wrapper for layout and zoom moves, shared tokens and components). Render each section video-only, then assemble with ffmpeg: concat the section renders, mix `voice.wav` (processed: highpass 80 Hz, light denoise, gentle compression, loudnorm to -14 LUFS integrated, true peak -1 dB) with music and SFX, export `renders/final.mp4` (1920x1080, 30 fps, h264 high, AAC 320k).
10. **Verify** (kit rules plus): hero frames of every layout change and every zoom, each section join, the first 30 s frame by frame, no black screen frame ever visible, no useless screen (teleprompter) on air, nothing private readable on screen (names, emails, phone numbers, tabs), A/V sync on 3 random speech moments, loudness measured. Write `VERIFY.md`.

## Delivery mode

Honor the checkpoints the user asks for. When none are given, do not stop in the
middle: work as an orchestrator, delegate stages to sub-agents with precise briefs,
verify their output yourself (frames, timings, levels), send fix passes, and come
back with `renders/final.mp4` when every goal is met. Record your own internal
gates in VERIFY.md (cut plan reviewed, intro judged against the hook criteria, full
draft reviewed). Paid calls beyond what the user approved: give the cost first.
The first 30-60 seconds decide whether a viewer stays: they deserve most of the
editorial and motion effort, and several iterations.
Feedback often comes voice-dictated and terse. Apply it, show again.
