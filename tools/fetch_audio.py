#!/usr/bin/env python3
"""Generate TTS audio for <audio> tags referenced in card files.

Scans every *.md under cards/ for <audio src="file.mp3" data-word="word">
tags and synthesises the spoken word into media/ using edge-tts (free
Microsoft neural voices). Existing files are kept unless --force is given,
so the script is safe to run on every build.

Usage:
  tools/fetch_audio.py
  tools/fetch_audio.py --force
"""

import argparse
import asyncio
import re
import sys
from pathlib import Path

import edge_tts

ROOT = Path(__file__).resolve().parent.parent
CARDS_DIR = ROOT / "cards"
MEDIA_DIR = ROOT / "media"

TAG_RE = re.compile(r"<audio\b([^>]*)>", re.IGNORECASE)
ATTR_RE = re.compile(
    r"""([a-zA-Z][\w-]*)\s*=\s*(?:"([^"]*)"|'([^']*)')"""
)


def parse_attrs(tag_body: str) -> dict:
    return {m.group(1).lower(): (m.group(2) or m.group(3)) for m in ATTR_RE.finditer(tag_body)}


def collect_targets():
    targets = {}  # src -> (word, voice, rate, pitch)
    for path in sorted(CARDS_DIR.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        for m in TAG_RE.finditer(text):
            attrs = parse_attrs(m.group(1))
            src = attrs.get("src")
            word = attrs.get("data-word") or ""
            if not src or not word:
                print(f"  warn: skipping {path.name}: audio tag needs src= and data-word=")
                continue
            targets[src] = (
                word.strip(),
                attrs.get("data-voice", "en-GB-SoniaNeural"),
                attrs.get("data-rate", "+0%"),
                attrs.get("data-pitch", "+0Hz"),
            )
    return targets


async def synth(src, word, voice, rate, pitch, out):
    comm = edge_tts.Communicate(word, voice=voice, rate=rate, pitch=pitch)
    await comm.save(str(out))
    return out


async def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--force", action="store_true", help="Regenerate existing audio too")
    args = ap.parse_args()

    targets = collect_targets()
    if not targets:
        print("No <audio> tags found in cards/.")
        return 0

    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    todo, skipped = [], 0
    for src, spec in targets.items():
        out = MEDIA_DIR / src
        if out.exists() and not args.force:
            skipped += 1
            continue
        todo.append((src, spec))

    print(f"Audio targets: {len(targets)}  (generating {len(todo)}, keeping {skipped})")
    failed = []
    for src, (word, voice, rate, pitch) in todo:
        try:
            out = await synth(src, word, voice, rate, pitch, MEDIA_DIR / src)
            print(f"  + {src}  <- '{word}' ({voice})")
        except Exception as exc:  # noqa: BLE001
            print(f"  ! {src} failed: {exc}")
            failed.append(src)

    if failed:
        print("Errors:", ", ".join(failed))
        return 1
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))