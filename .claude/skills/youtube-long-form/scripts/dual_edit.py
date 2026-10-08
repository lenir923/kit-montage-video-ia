"""Two-source (face cam + screen) edit engine for long-form videos.

The cam carries the audio, so the RAW CAM TIMELINE is the reference. Every
decision (take selection, silence cuts, mistake cuts, timelapses) is composed
into one list of pieces on that timeline, then BOTH sources are cut once, from
the prepared files, frame-accurately. No generation loss, no drift.

Subcommands
-----------
select   selects.json + raw transcript  ->  sel.transcript.json + sel.map.json
         selects.json (times on the raw cam timeline, in playback order):
           {"items": [
             {"kind": "speech",    "start": 81.2, "end": 140.9, "section": "01-intro"},
             {"kind": "timelapse", "start": 420.0, "end": 470.0, "speed": 6,
              "section": "02-methode1", "note": "Claude writes the answer"}
           ]}
         sel.transcript.json is the kit format on the "selects" timeline: feed it to
         cut-silences (no --video, writes sel.silence-*.json) then cut-mistakes
         (find-cut-candidates + apply-cuts without --video, writes sel.mistakes-*.json).

compose  sel.map.json [+ silence EDL] [+ mistakes EDL]  ->  timeline.json + final.transcript.json
         timeline.json = ordered pieces on the raw cam timeline, snapped to the
         30 fps grid, with their position on the output timeline and their section.
         final.transcript.json = kit format on the OUTPUT timeline (beats, captions,
         validate-beat-sync).

cut      timeline.json + cam.mp4 + screen.mp4 + cam.wav + sync.json  ->  edit/
         sync.json comes from sync_screen.py (constant offset) or sync_audio.py
         (offset0 + drift: cam = screen + offset0 + drift * screen).
         edit/cam.mp4, edit/screen.mp4, edit/voice.wav on the output timeline,
         plus edit/sections/<section>/{cam.mp4,screen.mp4,voice.wav} and
         edit/sections.json (start/end of each section on the output timeline).
         Screen frames that do not exist (before the screen recording started)
         are black: never show them, use a cam layout there.
         Timelapse pieces: both videos sped up, voice silent (music covers it).
         A timelapse with speed 1 is a protected screen action (silent demo moment the
         silence cutter would otherwise delete): kept at normal speed WITH its sound.
         Speech joins get 12 ms audio fades.
         Gap items ({"kind": "gap", "duration": 18.5, "media": "...", "section": ...}) reserve a
         silent hole on the output timeline for an inserted media played full screen
         (both videos black there, voice silent); the composition puts the media on top.

Usage
-----
  uv run --with numpy python dual_edit.py select  --transcript raw.json --selects selects.json --out work/
  uv run --with numpy python dual_edit.py compose --map work/sel.map.json \
        [--silence-edl work/sel.silence-edl.json] \
        [--mistakes-edl work/sel.mistakes-edl.json] \
        --transcript raw.json --out work/
  uv run --with numpy python dual_edit.py cut --timeline work/timeline.json --cam assets/cam.mp4 \
        --screen assets/screen.mp4 --voice assets/cam.wav --sync analysis/sync.json --out assets/edit/
"""
import argparse
import json
import subprocess
import wave
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

FPS = 30
EPS = 1e-6


def snap(t):
    return round(round(t * FPS) / FPS, 4)


def load(p):
    return json.loads(Path(p).read_text())


def dump(p, obj):
    Path(p).write_text(json.dumps(obj, ensure_ascii=False, indent=1))


def words_in(words, a, b):
    return [w for w in words if w["start"] >= a - 0.02 and w["end"] <= b + 0.02]


# ---------------------------------------------------------------- select
def cmd_select(args):
    tr = load(args.transcript)
    items = load(args.selects)["items"]
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    cursor, words, speech, inserts = 0.0, [], [], []
    for idx, it in enumerate(items):
        if it["kind"] in ("timelapse", "gap"):
            inserts.append({"after_speech": len(speech) - 1, "item": idx, **it})
            continue
        a, b = it["start"], it["end"]
        for w in words_in(tr["words"], a, b):
            words.append({**w, "start": round(w["start"] - a + cursor, 3),
                          "end": round(min(w["end"], b) - a + cursor, 3)})
        speech.append({"item": idx, "raw_start": a, "raw_end": b, "sel_start": round(cursor, 4),
                       "section": it.get("section", "main"), "note": it.get("note", "")})
        cursor += b - a
    dump(out / "sel.transcript.json", {"text": " ".join(w["text"] for w in words),
                                        "audio_duration_secs": round(cursor, 3), "words": words})
    dump(out / "sel.map.json", {"speech": speech, "timelapses": inserts, "sel_duration": round(cursor, 4)})
    print(f"selects: {len(speech)} speech items ({cursor / 60:.1f} min), {len(inserts)} timelapses")


# ---------------------------------------------------------------- compose
def map_through(ranges, pieces):
    """ranges: intervals on the input timeline of `pieces`.
    pieces: [(in_start, in_end, src_start, tag)] contiguous kept pieces.
    Returns the intervals on the source timeline, in order, with tags."""
    res = []
    for a, b in ranges:
        for ps, pe, src, tag in pieces:
            lo, hi = max(a, ps), min(b, pe)
            if hi - lo > EPS:
                res.append((src + lo - ps, src + hi - ps, tag))
    return res


def keep_as_pieces(edl):
    pieces, cur = [], 0.0
    for r in edl["keep_ranges"]:
        pieces.append((cur, cur + r["end"] - r["start"], r["start"], None))
        cur += r["end"] - r["start"]
    return pieces, cur


def cmd_compose(args):
    m = load(args.map)
    tr = load(args.transcript)
    # intervals on the selects timeline that survive silence + mistakes cuts
    if args.silence_edl:
        s_pieces, s_len = keep_as_pieces(load(args.silence_edl))
        if args.mistakes_edl:
            ranges = [(r["start"], r["end"]) for r in load(args.mistakes_edl)["keep_ranges"]]
        else:
            ranges = [(0, s_len)]
        sel_ranges = [(a, b) for a, b, _ in map_through(ranges, s_pieces)]
    else:
        sel_ranges = [(0, m["sel_duration"])]
    # selects timeline -> raw cam timeline, tagged by speech item index
    sp = [(s["sel_start"], s["sel_start"] + s["raw_end"] - s["raw_start"], s["raw_start"], i)
          for i, s in enumerate(m["speech"])]
    raw = map_through(sel_ranges, sp)

    pieces = []
    for a, b, i in raw:
        a, b = snap(a), snap(b)
        if b - a < 1 / FPS - EPS:
            continue
        if pieces and pieces[-1]["kind"] == "speech" and pieces[-1]["speech_idx"] == i \
                and abs(pieces[-1]["src_end"] - a) < EPS:
            pieces[-1]["src_end"] = b  # merge contiguous
            continue
        pieces.append({"kind": "speech", "src_start": a, "src_end": b, "speed": 1,
                       "section": m["speech"][i]["section"], "speech_idx": i})
    # timelapses after the last piece of their speech item
    for tl in reversed(m["timelapses"]):
        k = tl["after_speech"]
        pos = max((j for j, p in enumerate(pieces) if p["kind"] == "speech" and p["speech_idx"] <= k),
                  default=-1) + 1
        if tl["kind"] == "gap":  # silent hole for an inserted media (rendered video played full screen)
            pieces.insert(pos, {"kind": "gap", "src_start": 0.0, "src_end": snap(tl["duration"]), "speed": 1,
                                "section": tl.get("section", "main"), "media": tl.get("media", ""),
                                "note": tl.get("note", "")})
            continue
        pieces.insert(pos, {"kind": "timelapse", "src_start": snap(tl["start"]), "src_end": snap(tl["end"]),
                            "speed": tl.get("speed", 4), "section": tl.get("section", "main"),
                            "note": tl.get("note", "")})
    t, words = 0.0, []
    for p in pieces:
        dur = snap((p["src_end"] - p["src_start"]) / p["speed"])
        p["out_start"], p["out_end"] = snap(t), snap(t + dur)
        if p["kind"] == "speech":
            for w in words_in(tr["words"], p["src_start"], p["src_end"]):
                words.append({**w, "start": round(w["start"] - p["src_start"] + t, 3),
                              "end": round(min(w["end"], p["src_end"]) - p["src_start"] + t, 3),
                              "section": p["section"]})
        t = p["out_end"]
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    dump(out / "timeline.json", {"fps": FPS, "reference": "raw cam timeline", "duration": round(t, 4),
                                 "pieces": pieces})
    dump(out / "final.transcript.json", {"text": " ".join(w["text"] for w in words),
                                          "audio_duration_secs": round(t, 3), "words": words})
    print(f"timeline: {len(pieces)} pieces, {t / 60:.2f} min -> {out / 'timeline.json'}")


# ---------------------------------------------------------------- cut
def ff(cmd):
    subprocess.run(["ffmpeg", "-v", "error", "-y", *cmd], check=True)


ENC = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "14", "-pix_fmt", "yuv420p",
       "-r", str(FPS), "-an", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709"]


def probe_size(p):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height:format=duration", "-of", "json", str(p)],
                         check=True, capture_output=True, text=True).stdout
    j = json.loads(out)
    return j["streams"][0]["width"], j["streams"][0]["height"], float(j["format"]["duration"])


def cut_src(src, s, e, speed, out):
    n = round((e - s) / speed * FPS)
    # Seek half a frame early: with -ss exactly on a frame boundary, ffmpeg + fps= picked the NEXT
    # source frame for about 1 piece in 3 (image 1 frame ahead of the voice).
    s0 = max(0.0, s - 0.5 / FPS)
    ff(["-ss", f"{s0:.4f}", "-i", str(src), "-t", f"{e - s0:.4f}",
        "-vf", f"setpts=(PTS-STARTPTS)/{speed},fps={FPS}", "-frames:v", str(n), *ENC, str(out)])


def black(size, s, e, speed, out):
    n = max(1, round((e - s) / speed * FPS))
    ff(["-f", "lavfi", "-i", f"color=black:s={size[0]}x{size[1]}:r={FPS}", "-frames:v", str(n), *ENC, str(out)])


def render_piece(src, a, b, speed, out, size, avail):
    """Cut [a,b] of src (seconds) at `speed`; parts outside [0, avail] become black."""
    lo, hi = max(a, 0.0), min(b, avail)
    if hi - lo <= EPS:
        return black(size, a, b, speed, out)
    if lo - a <= EPS and b - hi <= EPS:
        return cut_src(src, a, b, speed, out)
    parts = []
    for j, (kind, s, e) in enumerate([("black", a, lo), ("src", lo, hi), ("black", hi, b)]):
        if e - s <= EPS:
            continue
        p = out.with_name(out.stem + f"_{j}.mp4")
        cut_src(src, s, e, speed, p) if kind == "src" else black(size, s, e, speed, p)
        parts.append(p)
    concat(parts, out)
    for p in parts:
        p.unlink()


def concat(files, out):
    lst = out.with_suffix(".txt")
    lst.write_text("".join(f"file '{f.resolve()}'\n" for f in files))
    ff(["-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", "-movflags", "+faststart", str(out)])
    lst.unlink()


def read_wav(p):
    with wave.open(str(p)) as w:
        assert w.getnchannels() == 1 and w.getsampwidth() == 2, "voice must be mono 16-bit (prep_sources.py cam.wav)"
        return w.getframerate(), np.frombuffer(w.readframes(w.getnframes()), np.int16)


def write_wav(p, sr, x):
    with wave.open(str(p), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(x.astype(np.int16).tobytes())


def build_voice(pieces, sr, x):
    fade = int(0.012 * sr)
    chunks = []
    for p in pieces:
        n = round((p["out_end"] - p["out_start"]) * sr)
        if p["kind"] == "gap" or (p["kind"] != "speech" and p["speed"] != 1):
            chunks.append(np.zeros(n, np.float32))
            continue
        a = round(p["src_start"] * sr)
        c = x[a:a + n].astype(np.float32)
        c = np.pad(c, (0, n - len(c)))
        ramp = np.linspace(0, 1, fade, dtype=np.float32)
        c[:fade] *= ramp
        c[-fade:] *= ramp[::-1]
        chunks.append(c)
    return np.concatenate(chunks) if chunks else np.zeros(0, np.float32)


def cmd_cut(args):
    tl = load(args.timeline)
    sync = load(args.sync)
    offset = sync["offset"]
    # Optional clock drift (audio-to-audio sync): cam = screen + offset0 + drift * screen.
    # Without "drift" in sync.json the offset is constant, as before.
    drift, off0 = sync.get("drift", 0.0), sync.get("offset0", offset)

    def to_screen(t):
        return (t - off0) / (1 + drift) if drift else t - offset
    out = Path(args.out)
    tmp = out / "pieces"
    tmp.mkdir(parents=True, exist_ok=True)
    cam_w, cam_h, cam_dur = probe_size(args.cam)
    scr_w, scr_h, scr_dur = probe_size(args.screen)
    pieces = tl["pieces"]

    jobs = []
    for i, p in enumerate(pieces):
        a, b, sp = p["src_start"], p["src_end"], p["speed"]
        if p["kind"] == "gap":  # black frames on both sources, the composition shows the inserted media
            jobs.append((args.cam, 0.0, b, 1, tmp / f"cam_{i:04d}.mp4", (cam_w, cam_h), 0.0))
            jobs.append((args.screen, 0.0, b, 1, tmp / f"scr_{i:04d}.mp4", (scr_w, scr_h), 0.0))
            continue
        jobs.append((args.cam, a, b, sp, tmp / f"cam_{i:04d}.mp4", (cam_w, cam_h), cam_dur))
        jobs.append((args.screen, to_screen(a), to_screen(b), sp, tmp / f"scr_{i:04d}.mp4", (scr_w, scr_h), scr_dur))
    todo = [j for j in jobs if not j[4].exists()]
    print(f"rendering {len(todo)} piece files ({len(jobs) - len(todo)} cached) ...", flush=True)
    with ThreadPoolExecutor(args.workers) as ex:
        list(ex.map(lambda j: render_piece(*j), todo))

    sr, x = read_wav(args.voice)
    sections, order = {}, []
    for i, p in enumerate(pieces):
        s = p["section"]
        if s not in sections:
            sections[s] = []
            order.append(s)
        sections[s].append(i)

    concat([tmp / f"cam_{i:04d}.mp4" for i in range(len(pieces))], out / "cam.mp4")
    concat([tmp / f"scr_{i:04d}.mp4" for i in range(len(pieces))], out / "screen.mp4")
    write_wav(out / "voice.wav", sr, build_voice(pieces, sr, x))

    meta = []
    for s in order:
        d = out / "sections" / s
        d.mkdir(parents=True, exist_ok=True)
        idx = sections[s]
        concat([tmp / f"cam_{i:04d}.mp4" for i in idx], d / "cam.mp4")
        concat([tmp / f"scr_{i:04d}.mp4" for i in idx], d / "screen.mp4")
        write_wav(d / "voice.wav", sr, build_voice([pieces[i] for i in idx], sr, x))
        meta.append({"section": s, "out_start": pieces[idx[0]]["out_start"], "out_end": pieces[idx[-1]]["out_end"],
                     "pieces": idx, "contiguous": idx == list(range(idx[0], idx[-1] + 1))})
    dump(out / "sections.json", {"offset": offset, "offset0": off0, "drift": drift,
                                 "duration": tl["duration"], "sections": meta})
    got = probe_size(out / "cam.mp4")[2]
    print(f"edit: {tl['duration']:.2f}s expected, cam.mp4 {got:.2f}s; {len(order)} sections -> {out}")
    if abs(got - tl["duration"]) > 0.1:
        raise SystemExit("DURATION MISMATCH between timeline and rendered cam.mp4: investigate before editing further")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("select")
    s.add_argument("--transcript", required=True)
    s.add_argument("--selects", required=True)
    s.add_argument("--out", required=True)
    c = sub.add_parser("compose")
    c.add_argument("--map", required=True)
    c.add_argument("--silence-edl")
    c.add_argument("--mistakes-edl")
    c.add_argument("--transcript", required=True)
    c.add_argument("--out", required=True)
    k = sub.add_parser("cut")
    k.add_argument("--timeline", required=True)
    k.add_argument("--cam", required=True)
    k.add_argument("--screen", required=True)
    k.add_argument("--voice", required=True)
    k.add_argument("--sync", required=True)
    k.add_argument("--out", required=True)
    k.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()
    {"select": cmd_select, "compose": cmd_compose, "cut": cmd_cut}[a.cmd](a)


if __name__ == "__main__":
    main()
