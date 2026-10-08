"""Word-level transcription of a long recording with ElevenLabs Scribe, called through fal.ai.

Usage:
    uv run python transcribe_scribe.py <media> <out.json> [--lang fra] [--chunk 540]

- Same engine as Nate's kit (Scribe), billed on a fal.ai key instead of an ElevenLabs account.
  Key: env FAL_KEY, else a FAL_KEY= line in the nearest .env (current folder or its
  parents, then the kit root). Get one at https://fal.ai/dashboard/keys
- Long audio is split into ~9 min chunks, each boundary moved to the middle of the
  nearest silence, so no word is cut. Chunk results are cached next to out.json
  (<out>.chunks/), a rerun only sends the missing chunks.
- Output = the kit's common format, on the media's own timeline:
    {"text", "language_code", "audio_duration_secs",
     "words": [{"text", "start", "end", "type": "word"|"audio_event"}]}
  Spacing tokens are dropped. Audio events ([rire], [tousse]) are kept with
  type "audio_event": cut-silences/cut-mistakes treat them as words, drop them
  first if that is not wanted.
"""
import argparse
import base64
import json
import os
import re
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

ENDPOINT = "https://fal.run/fal-ai/elevenlabs/speech-to-text"


def fal_key():
    if os.environ.get("FAL_KEY"):
        return os.environ["FAL_KEY"].strip()
    here = Path(__file__).resolve()
    for folder in [Path.cwd(), *Path.cwd().parents, *here.parents]:
        env = folder / ".env"
        if not env.is_file():
            continue
        for line in env.read_text().splitlines():
            k, _, v = line.partition("=")
            if k.strip() == "FAL_KEY" and v.strip():
                return v.strip().strip('"').strip("'")
    raise SystemExit("FAL_KEY not found: set it in the environment or in the kit's .env")


def duration(path):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                 "-of", "csv=p=0", str(path)], check=True,
                                capture_output=True, text=True).stdout)


def silences(path):
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(path), "-vn", "-af",
                          "silencedetect=noise=-35dB:d=0.4", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", err)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
    return list(zip(starts, ends))


def boundaries(total, chunk, sil):
    cuts, t = [0.0], chunk
    while t < total - 30:
        cands = [(s + e) / 2 for s, e in sil if abs((s + e) / 2 - t) < 60]
        c = min(cands, key=lambda m: abs(m - t)) if cands else t
        cuts.append(c)
        t = c + chunk
    cuts.append(total)
    return cuts


def call(mp3, key, lang):
    uri = "data:audio/mpeg;base64," + base64.b64encode(mp3.read_bytes()).decode()
    body = json.dumps({"audio_url": uri, "language_code": lang, "diarize": False,
                       "tag_audio_events": True}).encode()
    req = urllib.request.Request(ENDPOINT, data=body, headers={
        "Authorization": "Key " + key, "Content-Type": "application/json"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=900) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            msg = e.read()[:300]
            if e.code in (429, 500, 502, 503, 504) and attempt < 3:
                time.sleep(10 * (attempt + 1))
                continue
            raise RuntimeError(f"fal HTTP {e.code}: {msg}")
        except (urllib.error.URLError, TimeoutError):
            if attempt < 3:
                time.sleep(10 * (attempt + 1))
                continue
            raise


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("media")
    ap.add_argument("out")
    ap.add_argument("--lang", default="fra")
    ap.add_argument("--chunk", type=float, default=540)
    a = ap.parse_args()
    media, out = Path(a.media), Path(a.out)
    cache = out.with_suffix(".chunks")
    cache.mkdir(parents=True, exist_ok=True)
    key = fal_key()

    total = duration(media)
    cuts = boundaries(total, a.chunk, silences(media))
    words, texts = [], []
    for i, (s, e) in enumerate(zip(cuts[:-1], cuts[1:])):
        res_path = cache / f"chunk{i:02d}_{s:.2f}_{e:.2f}.json"
        if res_path.exists():
            res = json.loads(res_path.read_text())
            print(f"[{i + 1}/{len(cuts) - 1}] cache {s:.1f}-{e:.1f}")
        else:
            mp3 = cache / f"chunk{i:02d}.mp3"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{s:.3f}", "-to", f"{e:.3f}",
                            "-i", str(media), "-vn", "-ac", "1", "-ar", "16000", "-b:a", "48k",
                            str(mp3)], check=True)
            print(f"[{i + 1}/{len(cuts) - 1}] Scribe {s:.1f}-{e:.1f} ...", flush=True)
            res = call(mp3, key, a.lang)
            res_path.write_text(json.dumps(res, ensure_ascii=False))
            mp3.unlink()
        texts.append(res.get("text", "").strip())
        for w in res.get("words", []):
            if w.get("type") == "spacing":
                continue
            words.append({"text": w["text"].strip(), "start": round(w["start"] + s, 3),
                          "end": round(w["end"] + s, 3), "type": w.get("type", "word")})

    words.sort(key=lambda w: w["start"])
    doc = {"text": " ".join(texts), "language_code": a.lang, "audio_duration_secs": round(total, 3),
           "source": str(media.resolve()), "provider": "elevenlabs-scribe via fal.ai",
           "words": words}
    out.write_text(json.dumps(doc, ensure_ascii=False, indent=1))
    print(f"{len(words)} tokens, {total / 60:.1f} min -> {out}")


if __name__ == "__main__":
    main()
