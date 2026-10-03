#!/usr/bin/env python3
"""Inspect and validate the vocabulary data spread over cards/words/.

cards/schema.yaml declares `files: ["words/*.yaml"]`, so the builder itself
concatenates the per-letter files in sorted order — there is no generated
aggregate file. This script is the reading/QA side of that layout:

    python3 tools/words.py check                 # YAML + fields + synonym coverage + placement
    python3 tools/words.py extract assumption    # print one entry, verbatim
    python3 tools/words.py list                  # counts per file and per deck component

`check` also enforces the one convention the builder cannot: an entry lives in
the file matching its own initial letter, so a word never drifts into the wrong
file as the deck grows.
"""

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CARDS = ROOT / "cards"
PARTS = CARDS / "words"
GLOB = "words/*.yaml"
ENTRY_RE = re.compile(r"^  - word: (?P<word>.*)$")

REQUIRED = [
    "word",
    "ipa",
    "pos",
    "tip",
    "definition",
    "example",
    "synonyms",
    "syn_pos",
    "syn_example",
]


def part_files():
    return sorted(CARDS.glob(GLOB))


def parse_file(path):
    """Return the records of one part file, plus its verbatim text blocks."""
    text = path.read_text(encoding="utf-8")
    records = yaml.safe_load(text)["words"]
    lines = text.split("\n")
    starts = [i for i, line in enumerate(lines) if ENTRY_RE.match(line)]
    blocks = [
        lines[s : (starts[n + 1] if n + 1 < len(starts) else len(lines))]
        for n, s in enumerate(starts)
    ]
    return records, blocks


def letter_of(word):
    first = word.strip().lower()[:1]
    return first if "a" <= first <= "z" else "_"


def all_entries():
    """Yield (path, records, blocks) for every part file, in build order."""
    for path in part_files():
        records, blocks = parse_file(path)
        yield path, records, blocks


def cmd_check(args):
    files = part_files()
    if not files:
        print(f"FAIL no part files match {GLOB}")
        sys.exit(1)

    problems = []
    counts = Counter()
    total = 0

    for path, records, blocks in all_entries():
        if len(records) != len(blocks):
            problems.append(f"{path.name}: parsed {len(records)} records but found {len(blocks)} entries")
            continue
        total += len(records)
        for record, block in zip(records, blocks):
            word = record.get("word", "<unnamed>")
            counts[word] += 1
            if not isinstance(word, str) or not word.strip():
                problems.append(f"{path.name}: an entry has no word")
                continue
            if word != ENTRY_RE.match(block[0]).group("word").strip():
                problems.append(f"{word}: entry text does not match the parsed record")

            expected = letter_of(word)
            if path.stem != expected:
                problems.append(f"{word}: sits in {path.name}, which should hold '{expected}' words")

            missing = [f for f in REQUIRED if f not in record]
            if missing:
                problems.append(f"{word}: missing required field(s) {', '.join(missing)}")

            notes = record.get("syn_notes") or {}
            near = record.get("syn_near") or []
            avoid = dict(record.get("syn_avoid") or {})
            ctxs = record.get("syn_examples") or []
            for ctx in ctxs:
                if not ctx.get("the"):
                    problems.append(f"{word}: a syn_example has no `the` sentence")
                syns = ctx.get("syns") or []
                if not syns:
                    problems.append(f"{word}: a syn_example accepts no synonym")
                if not isinstance(syns, list):
                    problems.append(f"{word}: a syn_example has a non-list syns")
                    continue
                if "avoid" in ctx and not isinstance(ctx["avoid"], dict):
                    problems.append(f"{word}: a syn_example has a non-mapping avoid")
                    continue
                ctx_avoid = ctx.get("avoid") or {}
                sentence = ctx["the"].lower().replace(".", "").split() if ctx.get("the") else []
                for syn in syns:
                    if " " not in syn and syn.lower() in sentence:
                        problems.append(f"{word}: accepted {syn!r} is already printed in its sentence")
                    if syn not in notes:
                        problems.append(f"{word}: accepted {syn!r} has no syn_notes gloss")
                avoid.update(ctx_avoid)
                accepted = set(syns) | set(ctx.get("types") or [])
                for syn in record.get("synonyms") or []:
                    if syn not in accepted and syn not in avoid:
                        problems.append(
                            f"{word}: rejected synonym {syn!r} has no reason "
                            f"(syn_avoid or a per-context avoid)"
                        )
            for syn in near:
                if syn not in avoid:
                    problems.append(f"{word}: syn_near {syn!r} has no reject reason")
            for syn in avoid:
                if syn not in (record.get("synonyms") or []) and syn not in near:
                    problems.append(f"{word}: syn_avoid {syn!r} is never rejected")

    dupes = sorted(w for w, n in counts.items() if n > 1)
    if dupes:
        print(f"note: {len(dupes)} word(s) appear more than once: {', '.join(dupes)}")

    if problems:
        for problem in problems:
            print(f"FAIL {problem}")
        print(f"\n{len(problems)} problem(s)")
        sys.exit(1)
    print(f"ok: {total} entries in {len(files)} files, {len(counts)} words, all checks pass")


def cmd_list(args):
    total = 0
    for path, records, blocks in all_entries():
        lines = sum(len(b) for b in blocks)
        n = len(records)
        total += n
        print(f"  {path.relative_to(ROOT)}: {n} {'entry' if n == 1 else 'entries'}, {lines} lines")
    print(f"  total: {total} entries in {len(part_files())} files")

    comps = Counter()
    contexts = 0
    for _, records, _ in all_entries():
        for record in records:
            for comp in record.get("components") or []:
                comps[comp] += 1
            contexts += len(record.get("syn_examples") or [])
    print(f"  entries: {total}")
    for comp, n in comps.most_common():
        print(f"  {comp}: {n} entries")
    print(f"  contexts (SynonymsV2 cards): {contexts}")


def cmd_extract(args):
    needle = args.word.lower()
    hits = []
    for path, records, blocks in all_entries():
        for record, block in zip(records, blocks):
            hits.append((path, record.get("word", ""), block))

    exact = [h for h in hits if h[1].lower() == needle]
    loose = [h for h in hits if needle in h[1].lower() and h not in exact]
    chosen = exact or loose
    if not chosen:
        raise SystemExit(f"no entry matching {args.word!r}")
    if not exact and not args.all:
        print(f"# {len(loose)} partial matches: {', '.join(h[1] for h in loose)}", file=sys.stderr)
    for path, word, block in chosen:
        if args.paths:
            print(f"# {path.relative_to(ROOT)}")
        print("\n".join(block))
        if len(chosen) > 1:
            print()


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("check", help="validate YAML, fields, synonym coverage and file placement").set_defaults(func=cmd_check)
    sub.add_parser("list", help="counts per file and per deck component").set_defaults(func=cmd_list)

    p_extract = sub.add_parser("extract", help="print the entries for one word, verbatim")
    p_extract.add_argument("word")
    p_extract.add_argument("--all", action="store_true", help="print partial matches too")
    p_extract.add_argument("--paths", action="store_true", help="prefix each entry with its file")
    p_extract.set_defaults(func=cmd_extract)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()