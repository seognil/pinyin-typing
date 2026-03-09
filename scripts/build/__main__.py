from __future__ import annotations

from .fetch import fetch_sources
from .groups import reset_data_dir
from .build_base import build_base
from .build_extend import build_extend
from .build_chars import build_chars
from .meta import build_meta
from .shard import write_excludes, write_manifest, write_shards


def main() -> int:
    source_manifest = fetch_sources()
    reset_data_dir()
    chars_result = build_chars()
    base_result = build_base(chars_result["char_levels"])
    extend_result = build_extend(base_result["texts"], chars_result["char_levels"])
    build_result = {
        "chars": chars_result,
        "base": base_result,
        "extend": extend_result,
    }
    shards = write_shards(
        {
            "chars": chars_result["rows"],
            "base": base_result["rows"],
            "extend": extend_result["rows"],
        }
    )
    write_excludes(build_result)
    write_manifest(source_manifest, build_result, shards)
    build_meta(build_result, shards)
    print(f"chars_total={chars_result['stats']['total']}")
    print(f"base_total={base_result['stats']['total']}")
    print(f"extend_total={extend_result['stats']['total']}")
    print(f"shard_total={len(shards)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
