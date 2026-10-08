"""Prepare the two raw recordings of a long-form YouTube edit.

Usage:
    uv run python prep_sources.py --cam <iphone.MOV> --screen <screen.mov> --out <project>/assets [--test 20]

Writes into --out:
    cam.mp4       face cam, rotation applied, HDR (HLG/PQ) tonemapped to SDR bt709,
                  constant 30 fps, h264 high quality, with its audio (AAC 48 kHz)
    screen.mp4    screen recording, constant 30 fps, native resolution, h264
    cam.wav       mono 48 kHz PCM of the cam audio (the master audio of the edit)
    screen.wav    mono 48 kHz PCM of the screen audio, only when the screen recording has
                  an audio track (input of sync_audio.py)
    sources.json  durations, resolutions, HDR flag, creation times (used by sync_screen.py)

--test N only processes the first N seconds (to validate settings fast).
--grade "eq=..." appends a grade after the tonemap. An iPhone HLG face cam that came out
too bright needed this anti-burn grade: "eq=brightness=-0.11:contrast=1.16:saturation=1.10:gamma=0.96"
(that one was tuned after a libplacebo tonemap, hable is already darker: compare
frames with --test before choosing, never apply blind).
Raw files are never modified.
"""
import argparse
import json
import subprocess
from pathlib import Path

FPS = 30
TONEMAP = ("zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,"
           "tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p")


def probe(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "format=duration:format_tags=creation_time,com.apple.quicktime.creationdate"
         ":stream=index,codec_type,width,height,color_transfer,avg_frame_rate"
         ":stream_side_data=rotation", "-of", "json", str(path)],
        check=True, capture_output=True, text=True).stdout
    return json.loads(out)


def video_info(meta):
    v = next(s for s in meta["streams"] if s["codec_type"] == "video")
    rot = 0
    for sd in v.get("side_data_list", []) or []:
        if "rotation" in sd:
            rot = int(sd["rotation"])
    has_audio = any(s["codec_type"] == "audio" for s in meta["streams"])
    tags = meta["format"].get("tags", {})
    return {
        "duration": float(meta["format"]["duration"]),
        "coded_size": [v["width"], v["height"]],
        "rotation": rot,
        "hdr": v.get("color_transfer") in ("arib-std-b67", "smpte2084"),
        "has_audio": has_audio,
        "creation_time": tags.get("creation_time"),
        "apple_creationdate": tags.get("com.apple.quicktime.creationdate"),
    }


def run(cmd):
    print("+", " ".join(cmd[:6]), "...")
    subprocess.run(cmd, check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cam", required=True)
    ap.add_argument("--screen", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--test", type=float, default=0)
    ap.add_argument("--grade", default="")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    limit = ["-t", str(a.test)] if a.test else []

    cam = video_info(probe(a.cam))
    scr = video_info(probe(a.screen))

    # Face cam: ffmpeg autorotates by default; tonemap only if HDR.
    vf = ([TONEMAP] if cam["hdr"] else ["format=yuv420p"]) + ([a.grade] if a.grade else []) + [f"fps={FPS}"]
    run(["ffmpeg", "-v", "error", "-stats", "-y", "-i", a.cam, *limit,
         "-map", "0:v:0", "-map", "0:a:0", "-vf", ",".join(vf),
         "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p",
         "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
         "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-movflags", "+faststart",
         str(out / "cam.mp4")])
    run(["ffmpeg", "-v", "error", "-y", "-i", a.cam, *limit, "-vn", "-ac", "1",
         "-ar", "48000", "-c:a", "pcm_s16le", str(out / "cam.wav")])

    # Screen: constant 30 fps, native resolution, crisp text (low CRF, stillimage-friendly).
    run(["ffmpeg", "-v", "error", "-stats", "-y", "-i", a.screen, *limit,
         "-map", "0:v:0", "-vf", f"fps={FPS},format=yuv420p",
         "-c:v", "libx264", "-preset", "medium", "-crf", "14", "-tune", "stillimage",
         "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
         "-movflags", "+faststart", str(out / "screen.mp4")])
    if scr["has_audio"]:
        run(["ffmpeg", "-v", "error", "-y", "-i", a.screen, *limit, "-vn", "-ac", "1",
             "-ar", "48000", "-c:a", "pcm_s16le", str(out / "screen.wav")])

    info = {"fps": FPS, "cam_raw": str(Path(a.cam).resolve()), "screen_raw": str(Path(a.screen).resolve()),
            "cam": cam, "screen": scr,
            "cam_display_size": cam["coded_size"][::-1] if abs(cam["rotation"]) == 90 else cam["coded_size"],
            "test_seconds": a.test or None, "grade": a.grade or None}
    (out / "sources.json").write_text(json.dumps(info, indent=2))
    print(json.dumps(info, indent=2))


if __name__ == "__main__":
    main()
