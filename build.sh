#!/usr/bin/env bash
set -euo pipefail

# Path to the AnkiDaiku binary (modified with `# Type` typed-answer support).
ANKIDAIKU="${ANKIDAIKU:-$HOME/Desktop/coding/AnkiDaiku/target/release/anki-daiku}"

cd "$(dirname "$0")"

# Generate any missing pronunciation audio (edge-tts via the project venv).
if [ -x tools/.venv/bin/python ] && [ -x tools/fetch_audio.py ]; then
  tools/.venv/bin/python tools/fetch_audio.py
fi

"$ANKIDAIKU" build .