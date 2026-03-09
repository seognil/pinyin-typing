from __future__ import annotations

from .fetch import fetch_sources
from .groups import reset_data_dir
from .build_edu import build_edu
from .build_modern import build_modern
from .build_phrase import build_phrase
from .build_chars import build_chars
from .meta import build_meta
from .shard import write_excludes, write_manifest, write_shards
from .word_order import assign_word_fr


def main() -> int:
    source_manifest = fetch_sources()
    reset_data_dir()
    chars_result = build_chars()
    edu_result = build_edu(chars_result["char_levels"])
    modern_result = build_modern(edu_result["texts"], chars_result["char_levels"])
    phrase_result = build_phrase(
        edu_result["texts"] | modern_result["texts"], chars_result["char_levels"]
    )
    ordered_words = assign_word_fr(
        edu_result["rows"],
        modern_result["rows"],
        modern_result["source_rank"],
        phrase_result["rows"],
    )
    edu_result["rows"] = ordered_words["edu"]
    modern_result["rows"] = ordered_words["modern"]
    phrase_result["rows"] = ordered_words["phrase"]
    build_result = {
        "chars": chars_result,
        "edu": edu_result,
        "modern": modern_result,
        "phrase": phrase_result,
        "word_buckets": ordered_words["word_buckets"],
    }
    shards = write_shards(
        {
            "chars": chars_result["rows"],
            "edu": edu_result["rows"],
            "modern": modern_result["rows"],
            "phrase": phrase_result["rows"],
        }
    )
    write_excludes(build_result)
    write_manifest(source_manifest, build_result, shards)
    build_meta(build_result, shards)
    print(f"chars_total={chars_result['stats']['total']}")
    print(f"edu_total={edu_result['stats']['total']}")
    print(f"modern_total={modern_result['stats']['total']}")
    print(f"phrase_total={phrase_result['stats']['total']}")
    print(f"shard_total={len(shards)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
