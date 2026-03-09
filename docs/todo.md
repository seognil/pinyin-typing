# Todo

## Completed Data Work

- [x] Reduce the default pipeline to active product sources only
- [x] Export a base word tier from `cycb`
- [x] Export an extend append tier from `phrases_dict.json`
- [x] Export the full `8105` single-character tier as shard-based runtime data under `data/shards/`
- [x] Remove broad-corpus and support-layer dependencies from the default path
- [x] Remove old experimental preprocessing scripts and reports
- [x] Absorb reusable confusion rules into code

## Current Direction

- Keep the project minimal and fast to iterate.
- Use `cycb` as the default word corpus.
- Keep `phrases_dict.json` only as an optional enhancement layer.
- Keep the full standard single-character table for coverage and mastery tracking.
- Treat word training as the main mode.
- Treat single-character training as coverage and补漏.

## Next Product Work

- Implement typing using the `data/` distribution files and input normalization against `pm`.
- Add word-level and character-level mastery tracking.
- Let word attempts feed back into character mastery.
- Use single-character mode to reinforce weak or under-seen characters.
