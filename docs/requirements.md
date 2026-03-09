# Pinyin Trainer Requirements

Current frozen baseline: `docs/current-status.md`

## Goal

Build a lightweight data pipeline for a web-based pinyin typing trainer.

The product should train pinyin through natural word typing first, while still keeping a full standard-character layer for coverage and diagnosis.

## Product Direction

- Word typing is the main training experience.
- Single-character typing is the coverage and diagnosis mode.
- Confusion groups such as `en-eng` should be trained mainly through words, but single-character mode can still filter by confusion metadata.
- Character mastery and word mastery should both exist in the future product.
- The data pipeline should stay simple, source-oriented, and runtime-friendly.

## Data Strategy

- Use `hanzi-words-cycb` as the default word source.
- Use `python-pinyin/phrases_dict.json` as the optional enhancement phrase source.
- Use the official `8105` standard-character order as the single-character backbone.
- Use the single-character pronunciation file only to fill `pm` for that official backbone.
- Keep rebuild-only source files under `.source/`.
- Export final runtime-ready shards directly under `data/`.
- Avoid precomputing every confusion and level combination into separate files.

## Runtime Assets

- Sharded runtime data: `data/shards/*.tsv`
- Runtime shard index: `data/manifest.json`
- Human-readable build summary: `data/meta.md`

Rows must use one compact schema across all tiers:

- `t`
- `pm`
- `fr`
- `g`
- `l`

These assets serve different purposes and should remain separate by shard metadata:

- `base` shards provide the default training experience.
- `extend` shards provide optional phrase coverage as an append layer over the base tier.
- `chars` shards provide full `8105` coverage.

## Word Training Requirements

- Default training units should be `2-character` words.
- Good `3/4-character` words should remain available.
- Word entries should have stable direct pinyin.
- Runtime should be able to filter by confusion groups and by character-level coverage.
- Users should be able to choose between the base tier alone and base plus the extend append tier.
- Word runtime entries should expose a single order key inside each tier.

## Character Training Requirements

- Keep the full official `8105` standard-character table.
- Keep character levels aligned to the official `3500 / 3000 / 1605` split.
- Keep the official order as the character `fr` key.
- Use the character tier for full-coverage training and for character-level mastery tracking.

## Confusion Rules

- Absorb reusable confusion rules directly into code.
- Do not keep separate runtime rule-source dependencies.
- Keep the current front/back nasal and flat/retroflex style groups.
- Add more groups only when they improve training value without complicating the product too much.

## Mastery Model Direction

- Track both words and characters.
- Keep at least `seen`, `correct`, and `wrong` for each training unit.
- Let word attempts feed back into character mastery.
- Use single-character mode to reinforce characters that word training does not cover well enough.

## Non-Goals

- No broad corpus pipeline.
- No input-method-dictionary-style coverage chase as the default mode.
- No compatibility layer for old experimental preprocessing paths.
- No explosion of runtime files from pre-slicing every confusion/level combination.

## Active Sources

- `zispace/hanzi-words-cycb` - `https://github.com/zispace/hanzi-words-cycb`
- `mozillazg/python-pinyin` - `https://github.com/mozillazg/python-pinyin`
- `iDvel/The-Table-of-General-Standard-Chinese-Characters` - `https://github.com/iDvel/The-Table-of-General-Standard-Chinese-Characters`
