# Runtime Pipeline

Current frozen baseline: `docs/current-status.md`

## Upstream Sources

- `zispace/hanzi-words-cycb` - `https://github.com/zispace/hanzi-words-cycb`
- `mozillazg/python-pinyin` - `https://github.com/mozillazg/python-pinyin`
- `iDvel/The-Table-of-General-Standard-Chinese-Characters` - `https://github.com/iDvel/The-Table-of-General-Standard-Chinese-Characters`

## Active Build Flow

The rebuild path stays intentionally small:

1. `python3 -m scripts.build`

## Stage 1: Fetch Sources

- Keep raw upstream files under `.source/`.
- Write `.source/manifest.json` with fetched file metadata.
- Fetch on every build, but skip any local file that already exists and is non-empty.
- Cache both official `8105` character order and character pronunciation sources.

## Stage 2: Build Unified Rows

`python3 -m scripts.build` fetches sources, resets `data/`, and writes runtime assets directly.

- Build `chars` from the official `8105` order file plus the pronunciation file.
- Validate that deduped pronunciation order matches the official `8105` order exactly.
- Build `base` from `cycb`.
- Build `extend` from `phrases_dict.json`.
- Resolve confusion groups from `pm` and encode them into a compact row field.
- Resolve character levels from the official `8105` backbone and encode them into a compact bitmap field.
- Filter rows that use characters outside the official `8105` table.

## Stage 3: Write Shards

- Use a single row schema for all runtime data: `t<TAB>pm<TAB>fr<TAB>g<TAB>l`.
- Keep `tier` out of each row; infer it from shard metadata instead.
- Write shards under `data/shards/`.
- Bucket by `tier`, then by `len` for `base` and `extend`, then split by target file size.
- Avoid pre-splitting by confusion group or level, so one row is written once.

## Stage 4: Write Metadata

- Write `data/manifest.json` with shard metadata for runtime loading.
- Keep shard metadata minimal; runtime filtering happens after shard contents are loaded.
- Write `.source/output-exclude/*.tsv` for manual review of dirty rows only.
- Write `data/meta.md` with human-readable totals, per-length level summaries, and filter counts.
- Print a short build summary to the console.

## Distribution Outputs

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

## Runtime Asset Roles

- `data/shards/...`: final runtime shards.
- `data/manifest.json`: shard index used to select and load the right shards.
- `data/meta.md`: human-readable build summary only.
- Runtime should treat `extend` as a delta layer appended after `base`, not as a replacement tier.

## Design Rules

- Keep the pipeline source-oriented and minimal.
- Use the official `8105` table as the single source of truth for character coverage and levels.
- Treat phrase dictionaries as enhancement layers, not replacement lexicons.
- Keep confusion logic in code instead of in separate runtime source files.
- Prefer unified rows plus runtime filtering over precomputed combination files.
