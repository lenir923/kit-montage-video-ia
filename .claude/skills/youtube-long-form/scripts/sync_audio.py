"""Audio-to-audio sync of the screen recording on the face-cam timeline, with clock drift.

Usage:
    uv run --with numpy python sync_audio.py --cam assets/cam.wav --screen assets/screen.wav \
        --out analysis/sync.json [--sources assets/sources.json] [--guess 74.0]

Use it when the screen recording has its own audio (mic on while recording the
screen): both files hear the same voice. Writes the same sync.json as sync_screen.py,
plus the clock drift between the two devices:

    cam_time = screen_time + offset0 + drift * screen_time
    offset   = the offset at the middle of the screen recording (for tools that
               only read a constant)

dual_edit.py cut applies offset0 + drift. Two devices never count time at exactly
the same speed: a few hundredths of a second over 30 minutes is enough for lips to
drift away from the voice at the end of the video.

How it works: band-passed (150-1800 Hz) log envelopes at 200 Hz. A coarse
cross-correlation of the whole files gives the rough offset (unless --guess is
given). Then 60 s probes taken every 150 s of the screen audio are matched in a
+-15 s window around it, refined below one sample, and a line is fitted through
the confident probes (z-score above --min-z).
Always confirm by eye at 2-3 action moments and note it in VERIFY.md.
"""
import argparse
import json
import subprocess
from datetime import datetime
from pathlib import Path

import numpy as np

SR = 4000
HOP = 20
ER = SR / HOP  # envelope rate, 200 Hz


def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-vn", "-ac", "1", "-ar", str(SR),
                          "-af", "highpass=f=150,lowpass=f=1800", "-f", "s16le", "-"],
                         check=True, capture_output=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32)


def envelope(x):
    n = len(x) // HOP
    e = np.log1p(np.abs(x[: n * HOP]).reshape(n, HOP).mean(1))
    return e - np.convolve(e, np.ones(200) / 200, mode="same")


def xcorr(win, seg):
    """cc[k] = sum(win[i + k] * seg[i]) for k in 0..len(win) - len(seg)."""
    n = len(win) + len(seg)
    f = np.fft.rfft(win, n) * np.conj(np.fft.rfft(seg, n))
    return np.fft.irfft(f, n)


def zscore(cc, k):
    return float((cc[k] - np.median(cc)) / (cc.std() + 1e-9))


def refine(cc, k):
    if 0 < k < len(cc) - 1:
        y0, y1, y2 = cc[k - 1], cc[k], cc[k + 1]
        den = y0 - 2 * y1 + y2
        return 0.5 * (y0 - y2) / den if den else 0.0
    return 0.0


def coarse(ce, se):
    cc = xcorr(ce, se)
    n = len(cc)
    k = int(np.argmax(cc))
    lag = k if k <= n // 2 else k - n  # negative lag: the screen started before the cam
    return {"offset": round(lag / ER, 2), "z": round(zscore(cc, k), 1)}


def metadata_guess(sources):
    try:
        src = json.loads(Path(sources).read_text())
        t = lambda s: datetime.fromisoformat(s.replace("Z", "+00:00"))
        return round((t(src["screen"]["creation_time"]) - t(src["cam"]["creation_time"])).total_seconds(), 2)
    except (OSError, KeyError, TypeError, ValueError):
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cam", required=True, help="cam audio (assets/cam.wav)")
    ap.add_argument("--screen", required=True, help="screen audio (assets/screen.wav) or the raw screen file")
    ap.add_argument("--out", required=True)
    ap.add_argument("--sources", help="assets/sources.json, to report the metadata guess")
    ap.add_argument("--guess", type=float, help="rough offset in seconds, skips the coarse search")
    ap.add_argument("--probe", type=float, default=60, help="probe length (s)")
    ap.add_argument("--step", type=float, default=150, help="time between probes (s)")
    ap.add_argument("--search", type=float, default=15, help="search window around the guess (+-s)")
    ap.add_argument("--min-z", type=float, default=8)
    a = ap.parse_args()

    ce, se = envelope(load(a.cam)), envelope(load(a.screen))
    scr_dur = len(se) / ER
    print(f"cam {len(ce) / ER:.1f} s, screen {scr_dur:.1f} s")
    meta = metadata_guess(a.sources) if a.sources else None
    rough = None
    if a.guess is not None:
        guess = a.guess
    else:
        rough = coarse(ce, se)
        guess = rough["offset"]
        print(f"coarse offset {guess} s (z {rough['z']}), metadata guess {meta}")

    probes = []
    for t0 in np.arange(0, max(scr_dur - a.probe, 0) + 1e-9, a.step):
        sa, sb = int(t0 * ER), int((t0 + a.probe) * ER)
        lo, hi = int((t0 + guess - a.search) * ER), int((t0 + guess + a.search + a.probe) * ER)
        if lo < 0 or hi > len(ce) or sb > len(se):
            continue
        seg, win = se[sa:sb], ce[lo:hi]
        if seg.std() < 1e-6:
            continue
        cc = xcorr(win, seg)[: len(win) - len(seg) + 1]
        k = int(np.argmax(cc))
        off = (lo + k + refine(cc, k)) / ER - t0
        probes.append([round(float(t0), 1), round(float(off), 4), round(zscore(cc, k), 1)])
        print(probes[-1], flush=True)

    good = [p for p in probes if p[2] >= a.min_z]
    if len(good) >= 3:
        ts, offs = np.array([p[0] for p in good]), np.array([p[1] for p in good])
        drift, off0 = np.polyfit(ts, offs, 1)
        method = f"audio-to-audio cross-correlation, {len(good)} probes of {a.probe:g} s (z >= {a.min_z:g}), linear fit"
    elif good:
        drift, off0 = 0.0, float(np.median([p[1] for p in good]))
        method = f"audio-to-audio cross-correlation, only {len(good)} confident probe(s): constant offset"
    else:
        raise SystemExit("No confident probe: the two files do not share audible speech in the "
                         "searched window. Give --guess, or use sync_screen.py (silent screen).")
    drift, off0 = float(drift), float(off0)
    offset = off0 + drift * scr_dur / 2
    res = {"offset": round(offset, 4), "offset0": round(off0, 4), "drift": drift,
           "convention": "cam_time = screen_time + offset0 + drift * screen_time",
           "method": method, "coarse": rough, "metadata_guess": meta,
           "drift_over_recording_s": round(drift * scr_dur, 3),
           "screen_covers_cam": [round(off0, 2), round(off0 + scr_dur * (1 + drift), 2)],
           "probes": probes}
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(res, ensure_ascii=False, indent=1))
    print(json.dumps({k: v for k, v in res.items() if k != "probes"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
