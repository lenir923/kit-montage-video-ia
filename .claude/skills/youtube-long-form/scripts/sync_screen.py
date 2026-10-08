"""Find where the screen recording sits on the face-cam timeline.

Usage:
    uv run --with numpy python sync_screen.py --sources assets/sources.json \
        --activity analysis/activity10hz.npy --out analysis/sync.json \
        [--transcript assets/raw.json] [--cam-audio assets/cam.wav] [--offset 146.9 --note "..."]

Convention (used by every other script):  cam_time = screen_time + offset

For a SILENT screen recording. If the screen recording has its own audio (mic on),
use sync_audio.py instead: audio against audio, with clock drift. Evidence, by trust:
  1. --offset given by hand (after a visual check) : used as is.
  2. Spoken countdown in the transcript ("trois, deux, un, maintenant" / "3 2 1 top"):
     said out loud while clicking "record". offset = start of the last word,
     accepted when within 3 s of the metadata guess.
  3. Metadata: screen creation_time - cam creation_time (1 s precision, truncated,
     so the true start is usually a fraction of a second later).
Checks written in the output, never used blindly:
  - anchors: action words ("j'envoie", "je glisse", "je clique"...) should be
    followed within ~0-1.5 s by a screen change. Median residual near 0 to +0.5 s
    = good offset. Consistently negative or > 1 s = offset off by that much.
  - xcorr: key/click sounds vs screen changes. Weak on speech-heavy takes, a
    diagnostic only (it can peak on a wrong lag).
Always confirm by eye at 2-3 anchors before cutting, and note it in VERIFY.md.
"""
import argparse
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path

import numpy as np

RATE = 10
ACTION = re.compile(r"^(j'envoie|envoie|envoyer|glisse|clique|cliquez|ouvre|j'ouvre|tape|entrée|valide)", re.I)
COUNT = ["trois", "deux", "un"]


def norm(w):
    return re.sub(r"[^\w']", "", w.lower())


def parse_time(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def countdown(words, guess):
    toks = [(norm(w["text"]), w["start"]) for w in words if w.get("type", "word") == "word"]
    hits = []
    for i in range(len(toks) - 3):
        if [t for t, _ in toks[i:i + 3]] == COUNT and toks[i + 3][1] - toks[i][1] < 4:
            hits.append(toks[i + 3][1])
    hits = [h for h in hits if abs(h - guess) < 3]
    return hits[-1] if hits else None


def onsets(act, thr=0.002):
    on = (act[1:] > thr) & (act[:-1] <= thr)
    return (np.nonzero(on)[0] + 1) / RATE


def anchor_check(words, act, offset):
    ons = onsets(act)
    rows = []
    for w in words:
        if not ACTION.match(norm(w["text"])):
            continue
        s = w["start"] - offset
        near = ons[(ons > s - 1.5) & (ons < s + 2.5)]
        if len(near):
            rows.append({"word": w["text"], "cam": round(w["start"], 2),
                         "residual": round(float(near[np.argmin(np.abs(near - s))] - s), 2)})
    res = [r["residual"] for r in rows]
    return {"n": len(rows), "median_residual": round(float(np.median(res)), 2) if res else None,
            "anchors": rows[:40]}


def xcorr(wav, act, guess, search=20):
    sr = 16000
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(wav), "-ac", "1", "-ar", str(sr),
                          "-f", "s16le", "-"], check=True, capture_output=True).stdout
    x = np.frombuffer(raw, np.int16).astype(np.float32)
    hop = sr // RATE
    n = len(x) // hop
    spec = np.abs(np.fft.rfft(x[: n * hop].reshape(n, hop) * np.hanning(hop), axis=1))
    f = np.fft.rfftfreq(hop, 1 / sr)
    hi = np.log1p(spec[:, (f > 3000) & (f < 7500)].sum(1))
    lo = np.log1p(spec[:, (f > 120) & (f < 1000)].sum(1))
    on = np.maximum(np.diff(hi, prepend=hi[0]), 0)
    on[lo > np.percentile(lo, 60)] = 0  # mask speech
    aud = (on - on.mean()) / (on.std() + 1e-9)
    ev = np.maximum(np.diff((act > 0.0005).astype(np.float32), prepend=0), 0)
    scr = (ev - ev.mean()) / (ev.std() + 1e-9)
    lags = np.arange(round((guess - search) * RATE), round((guess + search) * RATE) + 1)
    sc = []
    for lag in lags:
        s0, c0 = max(0, -lag), max(0, lag)
        m = min(len(scr) - s0, len(aud) - c0)
        sc.append(float(np.dot(scr[s0:s0 + m], aud[c0:c0 + m]) / m))
    sc = np.array(sc)
    b = int(np.argmax(sc))
    return {"peak_offset": round(lags[b] / RATE, 2),
            "peak_z": round(float((sc[b] - np.median(sc)) / (sc.std() + 1e-9)), 2)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sources", required=True)
    ap.add_argument("--activity", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--transcript")
    ap.add_argument("--cam-audio")
    ap.add_argument("--offset", type=float)
    ap.add_argument("--note", default="")
    a = ap.parse_args()

    src = json.loads(Path(a.sources).read_text())
    meta = (parse_time(src["screen"]["creation_time"]) - parse_time(src["cam"]["creation_time"])).total_seconds()
    act = np.load(a.activity)
    words = json.loads(Path(a.transcript).read_text())["words"] if a.transcript else []

    if a.offset is not None:
        offset, method = a.offset, "manual: " + (a.note or "set by hand")
    elif words and countdown(words, meta) is not None:
        offset, method = round(countdown(words, meta), 2), "spoken countdown (last word start)"
    else:
        offset, method = meta + 0.5, "metadata (+0.5 s, creation times are truncated to the second)"

    res = {"offset": offset, "convention": "cam_time = screen_time + offset", "method": method,
           "metadata_guess": round(meta, 2),
           "screen_covers_cam": [round(offset, 2), round(offset + len(act) / RATE, 2)]}
    if words:
        res["anchor_check"] = anchor_check(words, act, offset)
    if a.cam_audio:
        res["xcorr_diagnostic"] = xcorr(a.cam_audio, act, meta)
    Path(a.out).write_text(json.dumps(res, ensure_ascii=False, indent=2))
    print(json.dumps({k: v for k, v in res.items() if k != "anchor_check"}, ensure_ascii=False, indent=2))
    if words:
        ac = res["anchor_check"]
        print(f"anchor check: {ac['n']} action words, median residual {ac['median_residual']} s")


if __name__ == "__main__":
    main()
