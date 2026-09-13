# English Spelling & Vocab (Anki)

Anki card deck for English spelling, vocabulary, synonyms, and IELTS writing
(trend describing), built with [AnkiDaiku](https://github.com/anomalyco/AnkiDaiku).

## Decks

Built from `cards/` (folder nesting = sub-decks):

| Deck | Card type | Front | You do | Answer |
|------|-----------|-------|--------|--------|
| `Spelling` | Definition → spelling | definition + hint | **type the word** | word, IPA, spelling tip |
| `Definitions` | Word → definition | word + IPA | recall the meaning | definition + example |
| `Synonyms` | Context → synonyms | sentence with the word underlined + POS | **type a synonym that fits this context** | fitting synonyms + essay tip |
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
  tries. Anki's built-in `{{type:...}}` only supports exact matches, which is
  why the answer box is supplied by a **widget** (below). Omit `# Type` for
  plain recall cards.
- `# Widget` (optional) — inline HTML/JS that replaces the answer box for this
  single card. `{{answers}}` is replaced with the escaped `# Type` list.
  Omitting it uses the deck default (see Widgets).
- `# Style` (optional) — per-card CSS.

On **AnkiDroid**, enable **Settings → Advanced → "Type answer into the card"**
so the on-screen keyboard appears for these custom inputs.

## Widgets: templating on top of "Type"

Two templating levels work together:

- **Type** is the Anki-native template — the notetype's Front/Back shells the
  deck ships. It is shared by every card, one copy per notetype:
  `{{Front}}` + `{{#Type}}{{Widget}}{{/Type}}`. It is meant to stay stable:
  Anki only conditionally applies note-type template changes on import. Fully
  overridable via `cards/template.yaml` (qfmt/afmt/fields/css) if a deck needs
  a different shell.
- **Widget** is *our* card templating on top of Type — a per-card HTML/JS
  interaction built at build time and stored in the note's `Widget` field
  (plain field updates apply on every import, on any Anki version).

The most specific widget wins:

1. `# Widget` section in a single card's `.md` (per-card).
2. `# Widget` section inside `cards/types/<name>.html`, rendered with that
   type's props like any other section (per component type).
3. `widget: <name>` front matter on a card or component type → uses
   `cards/widgets/<name>.html`.
4. `cards/widgets/default.html` — this deck's answer box (deck-wide default).
5. AnkiDaiku's built-in fallback (used when no deck file exists).

Fragments reference the accepted answers as `{{answers}}` (HTML-escaped into
the `data-answers` attribute at build time). Cards without `# Type` get no
widget. Editing `cards/widgets/default.html` restyles the box deck-wide;
per-type cards can carry their own `# Widget` section (e.g. a mini-synonym map).

Shared styling lives in `shared.css` (merged into the notetype). The type-in box,
IPA, part-of-speech and answer colors are defined there.

## Word decks: components + data

The `Spelling`, `Definitions`, and `Synonyms` decks are **data-driven**. Their
card HTML comes from reusable component templates (`cards/types/*.html`) rendered
with props from `cards/words.yaml` — no hand-written HTML per word.

- `cards/schema.yaml` — tells the builder which data file drives the word
  decks, which fields are required, and the type of each container field
  (`synonyms`, `components`: plain lists; `syn_examples`: list of records).
  AnkiDaiku auto-detects it; nothing about the record shape is hardcoded in
  the builder.
- `cards/types/spelling.html`, `definitions.html`, `synonyms.html` — each is a
  standard card body (`# Front` / `# Type` / `# Back`) containing `{{prop}}`
  placeholders plus template expressions (`{{#if}}`, `{{#each}}`, `{{join}}`,
  `{{letters}}`, `{{underline}}`, …), and a small front matter declaring the
  sub-deck and card id: `deck: Spelling` and `id: "{{word}}"`.
- `cards/words.yaml` — one entry per word with all fields (ipa, pos, spelling
  tip, definition, example, synonym list, syn_pos, syn_example) and the
  `components` it should fan out to (e.g. `[spelling, definitions, synonyms]`).

The build fans each word out to the requested components and renders each
template, producing one card per deck. All derived presentation is computed
inside the templates themselves — no deck-specific props are injected: the
spelling hint (`{{letters(word)}} letters · starts with <b>{{upper_first(word)}}</b> …`)
falls back to an explicit `spelling_hint` when given, and the synonym card
builds its examples/mapping from `syn_examples`.

### Synonym drills: one card per context

`synonyms.html` declares `each: syn_examples` in its front matter, so every
`syn_examples` entry becomes its **own card**: the front shows the sentence
with the word `<u>underlined</u>`, and you must supply the synonym that fits
*that specific context* (per-context `syns` lists the fitting synonyms;
plurals/inflections are matched via a per-context `types` field, so answers
like `prospects`/`possibilities` are accepted too). The `# Type` header lists
every fitting synonym, and the back shows each with `<small>` notes from
`syn_notes` so you learn the *distinction* (e.g. `attain` = by age/status,
`accomplish` = by effort). Ids are stable per context (`syn-<word>-<n>` or
`<syn_id>-<n>`), so rebuilding does not duplicate or churn cards.

To add a word to all three decks, add one entry to `words.yaml` listing the three
components (inventing 2–3 context sentences for `syn_examples`), then run
`./build.sh`. Many words (esp. the hard B2–C1 additions) are `[spelling,
definitions]` only — the `synonyms`/`syn_examples` fields are still required but
no drill cards fan out without `syn_examples`. To spin up a brand-new card type,
add a new template in `cards/types/`.

### Deck sizes (current)

| Deck | Cards |
|------|-------|
| Spelling | 318 (1 per word, all with spelling tips) |
| Definitions | 318 (1 per word) |
| Synonyms | 236 (1 per context sentence) |
| IELTS-Writing::Trends | 8 |
| Pronunciation (all) | 56 |
| **Total** | **937** |

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
When an `id` naturally changes, AnkiDaiku warns about orphaned old cards — that's fine
(delete them in Anki after importing), never answer "Continue" by force.

## Adding words

**Word decks (Spelling / Definitions / Synonyms):** add one entry to
`cards/words.yaml` (with the fields above and `components:`), then `./build.sh`.
The build renders all three cards for you.

**Other decks (IELTS, Pronunciation, manual synonym cards):**

1. Copy an existing card in the relevant deck folder and rename the file.
2. Change the `id` and the front/type/back content.
3. Run `./build.sh`.

To remove a card, `ankidaiku delete <id>` (soft delete) rather than just deleting
the file, so Anki stays in sync.