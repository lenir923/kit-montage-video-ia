"""Map a long screen recording: where and when the screen changes, plus contact sheets.

Usage:
    uv run --with numpy python screen_map.py <screen.mp4> <out_dir> [--sheet-every 10]

Writes into out_dir:
    activity10hz.npy   per-frame change ratio at 10 Hz (input of sync_screen.py)
    activity.json      per 0.5 s window: {"t", "act", "bbox"} on the SCREEN timeline.
                       act  = share of pixels that changed (0..1)
                       bbox = [x0, y0, x1, y1] normalized 0..1 of the changed area
                              (ignores cursor-sized specks), null when static.
                       Use bbox to aim screen zooms at what is actually moving.
    sheets/sheet_NNN.jpg  4x4 thumbnails, one every --sheet-every seconds, stamped
                       with the screen time. Look at them to label the segments
                       (teleprompter, claude.ai, OneDrive, Excel, desktop...).
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

W, H, RATE = 294, 192, 10
FONTS = ["/System/Library/Fonts/Supplemental/Arial.ttf", "/Library/Fonts/Arial.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
FONT = next((f for f in FONTS if Path(f).exists()), None)
HWACCEL = ["-hwaccel", "videotoolbox"] if sys.platform == "darwin" else []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("screen")
    ap.add_argument("out")
    ap.add_argument("--sheet-every", type=float, default=10)
    a = ap.parse_args()
    out = Path(a.out)
    (out / "sheets").mkdir(parents=True, exist_ok=True)

    proc = subprocess.Popen(
        ["ffmpeg", "-v", "error", *HWACCEL, "-i", a.screen,
         "-vf", f"fps={RATE},scale={W}:{H},format=gray", "-f", "rawvideo", "-"],
        stdout=subprocess.PIPE)
    size = W * H
    prev, series, masks, windows = None, [], [], []
    while True:
        buf = proc.stdout.read(size)
        if len(buf) < size:
            break
        f = np.frombuffer(buf, np.uint8).reshape(H, W).astype(np.int16)
        if prev is None:
            series.append(0.0)
            masks.append(np.zeros((H, W), bool))
        else:
            m = np.abs(f - prev) > 12
            series.append(float(m.mean()))
            masks.append(m)
        prev = f
        if len(masks) > 5:
            masks.pop(0)
        if len(series) % 5 == 0:
            # flush one 0.5 s window
            union = np.logical_or.reduce(masks)
            t = (len(series) - 5) / RATE
            act = float(np.mean(series[-5:]))
            bbox = None
            ys, xs = np.nonzero(union)
            if union.sum() > 40:  # more than a cursor speck
                x0, x1 = np.percentile(xs, [2, 98])
                y0, y1 = np.percentile(ys, [2, 98])
                bbox = [round(x0 / W, 3), round(y0 / H, 3), round((x1 + 1) / W, 3), round((y1 + 1) / H, 3)]
            windows.append({"t": round(t, 1), "act": round(act, 4), "bbox": bbox})
            masks = []
    proc.wait()
    np.save(out / "activity10hz.npy", np.array(series, np.float32))
    (out / "activity.json").write_text(json.dumps(windows))
    print(f"activity: {len(series) / RATE / 60:.1f} min analysed")

    every = a.sheet_every
    font = f"fontfile={FONT}:" if FONT else ""
    stamp = (f"drawtext={font}text='%{{pts\\:hms}}':x=8:y=8:fontsize=28:"
             "fontcolor=white:box=1:boxcolor=black@0.7:boxborderw=6")
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", *HWACCEL, "-i", a.screen, "-vf",
         f"fps=1/{every},scale=480:-2,{stamp},tile=4x4:padding=4:color=white",
         "-q:v", "3", str(out / "sheets" / "sheet_%03d.jpg")], check=True)
    n = len(list((out / "sheets").glob("*.jpg")))
    print(f"{n} contact sheets (one thumb every {every:g}s, 16 per sheet) -> {out / 'sheets'}")


if __name__ == "__main__":
    main()
