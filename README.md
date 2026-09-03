# English Spelling & Vocab (Anki)

Anki card deck for English spelling, vocabulary, synonyms, and IELTS writing
(trend describing), built with [AnkiDaiku](https://github.com/anomalyco/AnkiDaiku).

## Decks

Built from `cards/` (folder nesting = sub-decks):

| Deck | Card type | Front | You do | Answer |
|------|-----------|-------|--------|--------|
| `Spelling` | Definition → spelling | definition + hint | **type the word** | word, IPA, spelling tip |
| `Definitions` | Word → definition | word + IPA | recall the meaning | definition + example |
| `Synonyms` | Word → synonyms (per POS) | word + part of speech | **type a synonym** | POS synonym list + essay tip |
| `IELTS-Writing::Trends` | Cloze | sentence with a gap | **type the missing word(s)** | filled sentence + explanation |
| `Pronunciation::Sound-ID` | Listen → sound | audio clip | **type the vowel among 4** | word, IPA, spelling rule |
| `Pronunciation::{Schwa,Short-U,Foot-U,Long-U}` | Listen (grouped) | audio clip | recall after reveal | word, IPA, spelling rule |
| `Pronunciation::Contrasts` | Two clips, one target | 2 audio clips | **type 1 or 2** | both words + IPA |

Decks named `Spelling`, `Definitions`, `Synonyms`, `IELTS-Writing::Trends`, and
the `Pronunciation` family live under the root deck **English Spelling & Vocab**
(from `package.json`).

## Card format

Cards are single markdown files with sections separated by `---`:

```md
---
id: some-word
dependencies: []
---

# Front

Definition or prompt shown on the question side.

# Type            <- optional

significant, crucial, vital, essential, key   <- accepted answers, matched as ANY of these

# Back

<div class="w">some word</div>
<div class="phon">/səm wɜːd/</div>
```

- `id` (required) — unique within its sub-deck; changes nothing, but keeps Anki in sync.
- `dependencies` (optional) — tags; `[prereq]` orders cards.
- `# Type` (optional) — accepted typed answers, separated by commas or semicolons.
  The check accepts **any** of them (case/space-insensitive), so
  `significant, crucial` marks either as correct. Wrong input is reported per
  token ("Recognized: rise. Not in this card's answer list: foo."), a
  **Show answers** button reveals the list, and it auto-reveals after 3 failed
  tries. This is a small script in the card template — Anki's built-in
  `{{type:...}}` only supports exact matches. Omit `# Type` for plain recall
  cards. Requires the AnkiDaiku build with `# Type` support (see `build.sh`).

  On **AnkiDroid**, enable **Settings → Advanced → "Type answer into the card"**
  so the on-screen keyboard appears for these custom inputs.
- `# Style` (optional) — per-card CSS.

Shared styling lives in `shared.css` (merged into the notetype). The type-in box,
IPA, part-of-speech and answer colors are defined there.

## Pronunciation audio

Audio is generated from text with [edge-tts](https://github.com/rany2/edge-tts)
(free Microsoft neural voices, no API key). A card plays a word via:

```html
<audio class="pron-audio" controls preload="none" src="pron-schwa-about.mp3" data-word="about"></audio>
```

`tools/fetch_audio.py` scans the cards for `<audio>` tags, synthesises each
`data-word` into `media/` (skipping files that already exist), and `build.sh`
runs it automatically every build. To change the voice or pacing for one clip,
add `data-voice`, `data-rate`, or `data-pitch` attributes (edge-tts syntax).
Setup once: `python3 -m venv tools/.venv && tools/.venv/bin/pip install edge-tts`.

## Building

```sh
./build.sh                     # uses ~/Desktop/coding/AnkiDaiku/target/release/anki-daiku
ANKIDAIKU=/path/to/anki-daiku ./build.sh   # or point elsewhere
```

Output: `dist/output.apkg` — import into Anki. Rebuilding the same deck updates
existing notes instead of duplicating, as long as `id`s (and folder paths) stay the same.

## Adding words

1. Copy an existing card in the relevant deck folder and rename the file.
2. Change the `id` and the front/type/back content.
3. Run `./build.sh`.

To remove a card, `ankidaiku delete <id>` (soft delete) rather than just deleting
the file, so Anki stays in sync.