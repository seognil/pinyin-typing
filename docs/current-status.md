# Current Status

## Project State

- The data layer now builds three runtime tiers: `chars`, `base`, and `extend`.
- `chars` is anchored to the official `8105` standard-character order and level split.
- `base` uses `hanzi-words-cycb` as the default training lexicon.
- `extend` is an append-only delta over `base`, built from `python-pinyin/phrases_dict.json`.
- Confusion rules are resolved in build code and stored as compact row metadata instead of pre-sliced files.
- `data/` contains the runtime shards, shard manifest, and human summary.
- `.source/` contains rebuild-only upstream source files.

## Active Sources

- `zispace/hanzi-words-cycb` - `https://github.com/zispace/hanzi-words-cycb`
- `mozillazg/python-pinyin` - `https://github.com/mozillazg/python-pinyin`
- `iDvel/The-Table-of-General-Standard-Chinese-Characters` - `https://github.com/iDvel/The-Table-of-General-Standard-Chinese-Characters`

## Active Pipeline

1. `python3 -m scripts.build`

## Runtime Assets

- Runtime shards: `data/shards/*.tsv`
- Review-only dirty-row exports: `.source/output-exclude/*.tsv`
- Runtime shard index: `data/manifest.json`
- Human summary: `data/meta.md`

Distribution rows use `t<TAB>pm<TAB>fr<TAB>g<TAB>l`:

- `t`: text
- `pm`: space-joined marked pinyin
- `fr`: source-order rank inside the row's `tier`
- `g`: comma-joined confusion groups; empty means `rest`
- `l`: level bitmap derived from official `8105` character levels

`tier` is not stored per row. It comes from the shard name and `data/manifest.json`.

## Product Interpretation

- Word typing is still the natural main training flow.
- `base` remains the default cleaner tier.
- `extend` remains an optional append layer for broader phrase coverage.
- Character training keeps the full official `8105` table.
- Runtime filtering should use row metadata instead of choosing from precomputed combination files.

## Current Decisions

- The official `8105` table is the source of truth for single-character coverage, character `fr`, and character levels.
- Character pronunciations come from the pronunciation table, but only after strict order validation against the official `8105` list.
- `phrases_dict.json` is treated as an enhancement layer rather than a replacement for `cycb`.
- Rows are stored once and filtered at runtime by `g` and `l`.
- Shards are split by `tier`, then by `len`, then by target file size.

## Current Counts

- Chars total: `8105`
- Chars lv1: `3500`
- Chars lv2: `3000`
- Chars lv3: `1605`
- Base total: `53382`
- Base len2 lv1: `38532`
- Base len2 lv2 +=: `1927`
- Base len2 lv3 +=: `12`
- Base len3 lv1: `6698`
- Base len3 lv2 +=: `158`
- Base len3 lv3 +=: `0`
- Base len4 lv1: `5646`
- Base len4 lv2 +=: `409`
- Base len4 lv3 +=: `0`
- Extend total: `23357`
- Extend len2 lv1: `4914`
- Extend len2 lv2 +=: `468`
- Extend len2 lv3 +=: `26`
- Extend len3 lv1: `1720`
- Extend len3 lv2 +=: `105`
- Extend len3 lv3 +=: `3`
- Extend len4 lv1: `13581`
- Extend len4 lv2 +=: `2344`
- Extend len4 lv3 +=: `196`
- Shard total: `17`

## Current Filters

- Base non-`8105` filtered: `3`
- Base invalid `pm` filtered: `4`
- Base no-valid-candidate filtered: `4`
- Extend non-`8105` filtered: `329`
- Extend duplicate-by-base filtered: `22425`
- Extend invalid length filtered: `1000`
- Char pronunciation duplicates collapsed: `668`

## Representative Runtime Outputs

- `data/shards/chars.part-001.tsv`: `8105`
- `data/shards/base-len2.part-001.tsv`: `6977`
- `data/shards/base-len3.part-001.tsv`: `5078`
- `data/shards/base-len4.part-001.tsv`: `4119`
- `data/shards/extend-len4.part-001.tsv`: `4199`
- `.source/output-exclude/base.tsv`: `7`
- `.source/output-exclude/extend.tsv`: `329`
- `data/manifest.json`: shard metadata for runtime filtering

## Next Phase

- Build runtime loaders on top of `data/shards/` and `data/manifest.json`.
- Let runtime choose shards first, then filter rows by `g` and `l`.
- Track both word-level and character-level mastery.
