# English Spelling & Vocab (Anki)

Anki card deck for English spelling, vocabulary, synonyms, grammar (tense),
and IELTS writing (trend describing), built with
[AnkiDaiku](https://github.com/anomalyco/AnkiDaiku).

## Decks

Built from `cards/` (folder nesting = sub-decks):

| Deck | Card type | Front | You do | Answer |
|------|-----------|-------|--------|--------|
| `Spelling` | Definition → spelling | definition + hint | **type the word** | word, IPA, spelling tip |
| `Definitions` | Word → definition | word + IPA | recall the meaning | definition + example |
| `SynonymsV2` | Context → synonyms | sentence with the word underlined + POS | **type a synonym that fits this context** | fitting synonyms + essay tip |
| `IELTS-Writing::Trends` | Cloze | sentence with a gap | **type the missing word(s)** | filled sentence + explanation |
| `Tense` | Grammar contrast | sentence with a gap, or the wrong verb form underlined | **type the correct tense form** | filled sentence + pattern + why the other tense is wrong |
| `Collocation::{Cause,Data,Comparison,Problem,Preposition,Paraphrase}` | Pattern cloze | sentence with a gap + tag hint | **type the whole collocation** | filled sentence + pattern skeleton + wrong forms + tip |
| `Pronunciation::Sound-ID` | Listen → sound | audio clip | **type the vowel among 4** | word, IPA, spelling rule |
| `Pronunciation::{Schwa,Short-U,Foot-U,Long-U}` | Listen (grouped) | audio clip | recall after reveal | word, IPA, spelling rule |
| `Pronunciation::Contrasts` | Two clips, one target | 2 audio clips | **type 1 or 2** | both words + IPA |

Decks named `Spelling`, `Definitions`, `SynonymsV2`, `IELTS-Writing::Trends`,
`Tense`, the `Collocation` family and the `Pronunciation` family live under the
root deck **English Spelling & Vocab** (from `package.json`).

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
  `significant, crucial` marks either as correct. Whatever you type is scored:
  the box reports how many entries are right and how many are left, a
  **Show answers** button reveals the full list, and it auto-reveals after 3
  failed tries (see [The shared answer box](#the-shared-answer-box-spelling--synonymsv2--collocation--tense--cloze)).
  Anki's built-in `{{type:...}}` only supports exact matches, which is
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

### The shared answer box (Spelling + SynonymsV2 + Collocation + Tense + cloze)

`cards/widgets/default.html` is the only answer box in the deck: `Spelling`,
`SynonymsV2`, `Collocation`, `Tense` and the IELTS cloze cards all grade through
it, so every typed card behaves identically. Grading rules:

- **Any one accepted entry passes** — a list is a set of alternatives, not a
  set of required slots, so no card turns into a guessing game.
- **Your answer is scored, not just accepted/rejected.** Type more than one
  alternative (comma or semicolon separated) and it reports how many are right
  and how many are left: *"1 is correct · 6 more left"*, *"2 are correct ·
  Unrecognized: banana"*, *"1 is correct — all of them"*. A card with a
  **single** accepted answer (`Spelling`, a bare preposition like `in`) has
  nothing to count, so it just reads **Correct ✓**.
- **A half-remembered phrase gets a targeted hint** instead of a flat "wrong",
  matched by first word, then a 4-character stem, then a substring:

  | You type | It says |
  |----------|---------|
  | `resulted in` | 1 is correct · 6 more left ✓ |
  | `resulted in, banana` | 1 is correct · 6 more left · Unrecognized: banana |
  | `resulted` | Right idea, wrong form — this card wants: **resulted in** … |
  | `banana` | None of those are in the answer list. Try again (1/3) or tap Show answers. |
  | `accommodation` (Spelling card) | Correct ✓ |

- **Show answers lists every accepted answer, untruncated** (with the count),
  and it also fires automatically after 3 failed tries. Answers match case- and
  space-insensitively, and the back of the card is always the full reference
  anyway.

Shared styling lives in `shared.css` (merged into the notetype). The type-in box,
IPA, part-of-speech and answer colors are defined there.

## Word decks: components + data

The `Spelling`, `Definitions`, and `SynonymsV2` decks are **data-driven**. Their
card HTML comes from reusable component templates (`cards/types/*.html`) rendered
with props from `cards/words/*.yaml` — no hand-written HTML per word.

- `cards/schema.yaml` — tells the builder which data files drive the word
  decks, which fields are required, and the type of each container field
  (`synonyms`, `components`: plain lists; `syn_examples`: list of records).
  AnkiDaiku auto-detects it; nothing about the record shape is hardcoded in
  the builder.

  ```yaml
  data:
    files: ["words/*.yaml"]   # globs, read in sorted path order
    list: words               # root key holding the records
    components: components    # field listing the templates to fan out to
  ```

  `files:` takes any number of paths or globs (`*` stays inside one directory,
  `**` spans directories) and concatenates every match, so the deck spreads its
  records over as many files as it likes with no merge step. `file: words.yaml`
  is still accepted as a one-file shorthand.
- `cards/types/spelling.html`, `definitions.html`, `synonyms.html` — each is a
  standard card body (`# Front` / `# Type` / `# Back`) containing `{{prop}}`
  placeholders plus template expressions (`{{#if}}`, `{{#each}}`, `{{join}}`,
  `{{letters}}`, `{{underline}}`, …), and a small front matter declaring the
  sub-deck and card id: `deck: Spelling` and `id: "{{word}}"`.
- `cards/words/<letter>.yaml` — the vocabulary itself: one file per initial
  letter (`a.yaml`, `b.yaml`, …), each holding that letter's entries under the
  same top-level `words:` key, read alphabetically by the builder. One entry per
  word with all fields (ipa, pos, spelling tip, definition, example, synonym
  list, syn_pos, syn_example) and the `components` it should fan out to (e.g.
  `[spelling, definitions, synonyms]`). There is no aggregate `words.yaml`.

```bash
python3 tools/words.py check               # YAML, fields, synonym coverage, file placement
python3 tools/words.py extract assumption  # print one entry, verbatim
python3 tools/words.py list                # counts per letter file and per component
```

`check` catches what the builder cannot: a malformed file, a missing required
field, an accepted synonym with no `syn_notes` gloss, a rejected synonym with no
`syn_avoid` reason, and an entry sitting in the wrong letter file.

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

### The back of a synonym card: fits, does not fit, nuance

The back teaches the difference instead of just listing answers:

1. **The slot** — the context sentence with the target word blanked out
   (`{{replace(the, ../word, "__________")}}`).
2. **Fits this sentence** — the accepted `syns` of that context, each with its
   `syn_notes` gloss.
3. **Not this sentence** — strikethrough rejects with a reason. The list is
   built as `merge(without(../synonyms, syns, types), ../syn_near, ../avoid)`:
   every family word this context rejects, plus the near-miss distractors from
   `syn_near`, de-duplicated, each looked up in `syn_avoid` for its reason.
   Reasons are written to name the collocation or frame that fails, not to
   declare the word non-English — most are perfectly good elsewhere.
4. **Nuance** — `syn_nuance`, one or two sentences contrasting the whole family
   (what they share and which frame or degree each one takes).

Three optional per-word fields supply 3 and 4 (`cards/words/<letter>.yaml`):

| Field | Shape | Meaning |
| --- | --- | --- |
| `syn_near` | list of 1–5 words | Near misses a learner would wrongly type; must never be accepted in any context of that word |
| `syn_avoid` | map word → reason | Why a rejected word fails; must cover every derived reject plus every `syn_near` word |
| `syn_nuance` | 1–3 sentences | The family contrast shown in the nuance box |
| `avoid` (inside a `syn_examples` record) | map word → reason | Per-sentence reason that **overrides** `syn_avoid` for that one context |

The override exists because a reason that is right for one frame is often wrong
for another: `necessary` fails in "play a crucial role" because of that verb
pattern, but in "is necessary for success" because it belongs with *for*. Put a
sentence in a context record's `avoid` map and the card shows that text on that
card only; every other reason still falls back to the word-level `syn_avoid`.

```yaml
- the: Trust plays a crucial role here.
  syns: [essential, vital]
  avoid:
    necessary: = required, and it belongs with for, as in "necessary for
      success"; the frame here is "play a crucial role"
```

All of them are rendered only when present, so `[spelling, definitions]`-only
entries are unaffected. Write the reasons in plain text (no HTML, no markdown
asterisks) and keep them under ~200 characters.

To add a word to all three decks, add one entry to its letter file in
`cards/words/` listing the three components (inventing 2–3 context sentences for
`syn_examples`), then run `./build.sh`. Many words (esp. the hard B2–C1
additions) are `[spelling, definitions]` only — the `synonyms`/`syn_examples`
fields are still required but no drill cards fan out without `syn_examples`. To
spin up a brand-new card type, add a new template in `cards/types/`.

### Collocation drills: patterns, not synonyms

`cards/Collocation/` is a hand-written deck (one `.md` per card, like the IELTS
cloze cards) built around **collocation patterns** for IELTS Task 1/2 — the
point is not "do I know this word" but "what comes after it". Each card is a
cloze sentence; you **type the whole pattern**, so both the collocation and the
spelling are drilled:

```md
# Front
<div class="hint">TASK1_CAUSE &middot; the <b>cause</b> is the subject</div>
<span class="ex">"Population growth ____________ a sharp rise in housing prices."</span>

---

# Type

resulted in, led to, gave rise to, brought about, caused, triggered, spurred

---

# Back

Population growth **<span class="ans">resulted in</span>** a sharp rise in housing prices.

<div class="pat">X <b>results in / leads to</b> Y</div>
*Tip: <span class="no">attributed with</span> is wrong …
```

Sub-decks map 1:1 to the study tags:

| Sub-deck | Tag | Covers |
|----------|-----|--------|
| `Collocation::Cause` | `TASK1_CAUSE` | cause vs effect direction, `account for` (both meanings), `attribute … to`, `result from/in`, `lead to`, `contribute to`, `main cause of/in` |
| `Collocation::Data` | `TASK1_DATA` | `accounted for X%`, `constitute/make up/represent`, `proportion/percentage of`, `increase/decline in`, strength of change, `increase to/by/from … to`, `doubled`, `twice as high as` |
| `Collocation::Comparison` | `TASK1_COMPARISON` | `higher than`, `compared with`, `whereas`, `respectively`, `disparity between/in/among`, `uneven distribution`, `difference` vs `disparity` |
| `Collocation::Problem` | `TASK2_PROBLEM` | `address`/`tackle` (≠ `account for`), `exacerbate`/`worsen`/`alleviate`, `increasingly severe`, `experienced`, `put pressure/strain on`, `regarding` vs `about`, `holistically` vs `overall` |
| `Collocation::Preposition` | `PREPOSITION` | the highest-value category: `increase **in**`, `impact/effect/influence **on**`, `pressure/burden **on**`, `reliance **on**`, `demand **for**`, `contribute **to**`, `attribute … **to**`, `reason **for**`, `difference **between**` |
| `Collocation::Paraphrase` | `PARAPHRASE` | instinct → academic collocation: `benefit from`, `put pressure **on**`, `X accounted for 70%`, `the dominant/least significant cause`, `surged`, `worsened`, `a substantial disparity` |

Cards with no `# Type` section (`Cause::direction-map`, `Comparison::difference-vs-disparity`)
are plain front/back reference cards. Every card that does have one grades
through the deck's shared answer box (above) — no per-deck widget, and no
`widget:` front matter: the counts ("1 is correct / 6 more left") and the
untruncated **Show answers** list work exactly as they do in `SynonymsV2`.
Extra CSS used by these cards lives in
`shared.css`: `.pat` (pattern skeleton), `.no` (wrong form, struck through),
`.ok` (recommended form).

### Tense drills: type the tense, or fix the wrong one

`cards/Tense/` is a hand-written deck (one `.md` per card) that drills **tense
choice as a typed answer**, not as a question you answer in your head. All 9
cards have a `# Type` list, so they grade through the shared answer box exactly
like `Spelling`, `SynonymsV2` and `Collocation`, in two flavours chosen per card:

| Flavour | Cards | Front |
|---------|-------|-------|
| Cloze | 7 | sentence with `__________`, e.g. `"By 2023, the water __________ so the village was submerged."` |
| Wrong form underlined | 2 | a sentence whose tense is wrong, the bad form marked `<span class="no"><u>…</u></span>`, e.g. `"In 2020, the company <u>has launched</u> the product."` |

The wrong-form style mirrors `SynonymsV2`: the underlined token is the thing you
replace, and **only the correction is accepted** — `launched` and `rose` pass,
while the printed wrong form (`has launched`, `had risen`) is never an answer.
Cloze answers are kept deliberately tight (`have visited`, not `visited`,
`have done`, not `did`), so the tense is the thing being graded; a couple of
cards also accept a natural variant (`had risen, had already risen`).

The back keeps the teaching content the old question-style cards had: the filled
sentence, the `<div class="pat">` skeleton for the contrast
(`action completed before a past point → had + past participle`), and a
`<span class="no">` line naming the rejected tense and why it fails. The two
former rule cards (`past-perfect-timeline`, `present-perfect-vs-simple-past-keys`)
were turned into cloze drills — the rule moved to the back rather than being
asked as a question.

### Deck sizes (current)

| Deck | Cards |
|------|-------|
| Spelling | 320 (1 per word, all with spelling tips) |
| Definitions | 320 (1 per word) |
| SynonymsV2 | 246 (1 per context sentence) |
| IELTS-Writing::Trends | 8 |
| Tense | 9 |
| Collocation (all) | 69 (11 Cause, 14 Data, 10 Comparison, 13 Problem, 13 Preposition, 8 Paraphrase) |
| Pronunciation (all) | 56 |
| Deck guide | 1 |
| **Total** | **1029** |

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

**Word decks (Spelling / Definitions / SynonymsV2):** add one entry to the
right letter file in `cards/words/` (e.g. `cards/words/t.yaml` for `tentative`),
with the fields above and `components:`, then `./build.sh`. The builder reads
every letter file and renders all the cards for you. Run
`python3 tools/words.py check` first to catch missing fields, unglossed accepted
synonyms, rejected synonyms that have no reason, and entries in the wrong file.

**Other decks (IELTS, Collocation, Pronunciation, manual synonym cards):**

1. Copy an existing card in the relevant deck folder and rename the file
   (`id` and filename should match).
2. Change the `id` and the front/type/back content.
3. Run `./build.sh`.

Adding a **collocation** card: put it in `cards/Collocation/<Tag>/`, keep the
`# Type` list to answers that are all natural in that exact sentence (the check
accepts any of them, so a too-generous list makes the card too easy), and put
the skeleton in `<div class="pat">`, the wrong form in `<span class="no">` and
the recommended form in `<span class="ok">` on the back. No `widget:` front
matter: a `# Type` list is enough — the deck's shared answer box grades it.

**Prepositions are typed, always.** A `# Type` entry carries the verb *and* its
preposition (`attributed to`, not `attributed`), so the preposition itself is
drilled. Two cases:

- The preposition follows the verb in the blank (`can be ____________ higher
  demand` → `attributed to`) — nothing to do.
- The preposition follows the object, so the sentence already prints it
  (`The company ____________ the failure to poor communication`) — bold that
  `<b>to</b>` in the front sentence, keep the `to` printed, and still list the
  full form in `# Type`. On the back, highlight verb and preposition as two
  `.ans` spans (the object sits between them), so the answer reads as one
  collocation and the sentence stays grammatical.

Only list verbs whose preposition is actually `to` in that frame — `blame` is
not (`blame X on Y` / `blame X for Y`), and its wrong form belongs in the
`<span class="no">` tip, not in `# Type`.

To remove a card, `ankidaiku delete <id>` (soft delete) rather than just deleting
the file, so Anki stays in sync.