# Data Schema

Current frozen baseline: `docs/current-status.md`

## Source Cache Layer

- `.source/<source>/...`

Raw upstream files are stored as fetched.

## Runtime Output Layer

Directory layout:

- `data/shards/chars.part-*.tsv`
- `data/shards/base-len2.part-*.tsv`
- `data/shards/base-len3.part-*.tsv`
- `data/shards/base-len4.part-*.tsv`
- `data/shards/extend-len2.part-*.tsv`
- `data/shards/extend-len3.part-*.tsv`
- `data/shards/extend-len4.part-*.tsv`
- `.source/output-exclude/base.tsv`
- `.source/output-exclude/extend.tsv`
- `data/manifest.json`
- `data/meta.md`

The runtime layer keeps one compact row schema for all tiers and uses `manifest.json` to describe shard boundaries.

## Unified Row Schema

```text
认真\trèn zhēn\t469\ten-eng,r-l\t1
```

- Column 1: `t`
- Column 2: `pm`, joined by spaces
- Column 3: `fr`
- Column 4: `g`, confusion groups joined by commas; empty string means `rest`
- Column 5: `l`, level bitmap

`tier` is not stored in each row. It comes from the shard name and `data/manifest.json`.

`py` is omitted from distribution files.

## Field Semantics

### `fr`

- `fr` is a source-order key, not a score.
- In `chars`, `fr` is the official `8105` character position.
- In `base`, use the source row order from `cycb`.
- In `extend`, use the source row order from `phrases_dict.json`.

### `g`

- `g` stores matched confusion groups in fixed `GROUP_ORDER` order.
- Example: `en-eng,r-l`
- Empty `g` means the row belongs to `rest`.

### `l`

`l` is a bitmap based on the official `8105` level table:

- `1` -> contains level-1 characters only
- `2` -> contains level-2 characters only
- `4` -> contains level-3 characters only
- `3` -> contains level-1 and level-2 characters
- `5` -> contains level-1 and level-3 characters
- `6` -> contains level-2 and level-3 characters
- `7` -> contains level-1, level-2, and level-3 characters

For single-character rows, `l` is always one of `1`, `2`, or `4`.

## Character Backbone Rules

- The official `1-8105纯汉字（按顺序排列）.txt` file is the single source of truth for character coverage.
- Character levels come from that order directly:
  - `1..3500 -> level 1`
  - `3501..6500 -> level 2`
  - `6501..8105 -> level 3`
- The pronunciation file only fills `pm`; it does not define coverage or levels.
- Build validation requires the deduped pronunciation order to match the official `8105` order exactly.

## Manifest Schema

`data/manifest.json` is the runtime index for shards.

Each shard record contains:

- `path`
- `tier`
- `len`
- `rows`
- `bytes`
- `fr_min`
- `fr_max`

The manifest only describes how to load shards. Runtime filtering by `g` and `l` happens after shard contents are loaded.

## Exclude Review Files

The build also writes manual-review files for dirty rows only:

- `.source/output-exclude/base.tsv`
- `.source/output-exclude/extend.tsv`

Each row uses:

```text
text\tpm_raw\tfr\treason
```

Current dirty-data reasons:

- `non_8105`: contains characters outside the official `8105` backbone
- `invalid_pm`: pinyin data is empty, malformed, or length-mismatched
- `no_valid_candidate`: the row survived source parsing but produced no usable final pinyin candidate

Normal product-scope filters such as `duplicate_by_base` and `invalid_length` stay in `data/meta.md` counts only and are not exported as review rows.

## Meta Output

`data/meta.md` is a human-readable summary of generated totals, length-level distributions, and filtered rows. It is not a runtime dependency.

## Future Mastery Model

The current repo exports static data, but the product direction still assumes two mastery layers.

```json
{
  "character_mastery": {
    "丁": { "seen": 3, "correct": 3, "wrong": 0 }
  },
  "word_mastery": {
    "认真": { "seen": 8, "correct": 7, "wrong": 1 }
  }
}
```

- `word_mastery` drives the main typing flow.
- `character_mastery` tracks full-character coverage.
- Word attempts should be able to feed back into character mastery.
