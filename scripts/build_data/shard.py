from __future__ import annotations

import json
from datetime import datetime, timezone

from .groups import (
    EXCLUDE_DIR,
    MANIFEST_PATH,
    SHARD_TARGET_BYTES,
    SHARDS_DIR,
    WORD_LENGTHS,
)


def _bucket_name(tier: str, length: int | None) -> str:
    if tier == "chars":
        return "chars"
    return f"{tier}-len{length}"


def _encode_row(row: dict) -> str:
    return f"{row['t']}\t{row['pm']}\t{row['fr']}\t{row['g']}\t{row['l']}\n"


def write_shards(all_rows: dict[str, list[dict]]) -> list[dict]:
    shards = []
    for tier, rows in all_rows.items():
        buckets: dict[int | None, list[dict]] = {}
        if tier == "chars":
            buckets[None] = rows
        else:
            buckets = {length: [] for length in sorted(WORD_LENGTHS)}
            for row in rows:
                buckets[len(row["t"])].append(row)

        for length, bucket_rows in buckets.items():
            if not bucket_rows:
                continue
            bucket_name = _bucket_name(tier, length)
            part = 1
            current_lines: list[str] = []
            current_rows: list[dict] = []
            current_bytes = 0
            for row in bucket_rows:
                line = _encode_row(row)
                line_bytes = len(line.encode("utf-8"))
                if current_rows and current_bytes + line_bytes > SHARD_TARGET_BYTES:
                    shards.append(
                        _flush_shard(
                            bucket_name, tier, length, part, current_lines, current_rows
                        )
                    )
                    part += 1
                    current_lines = []
                    current_rows = []
                    current_bytes = 0
                current_lines.append(line)
                current_rows.append(row)
                current_bytes += line_bytes
            if current_rows:
                shards.append(
                    _flush_shard(
                        bucket_name, tier, length, part, current_lines, current_rows
                    )
                )
    return shards


def _flush_shard(
    bucket_name: str,
    tier: str,
    length: int | None,
    part: int,
    lines: list[str],
    rows: list[dict],
) -> dict:
    filename = f"{bucket_name}.part-{part:03d}.tsv"
    path = SHARDS_DIR / filename
    path.write_text("".join(lines), encoding="utf-8")
    return {
        "path": f"data/shards/{filename}",
        "tier": tier,
        "len": length,
        "rows": len(rows),
        "bytes": path.stat().st_size,
        "fr_min": min(row["fr"] for row in rows),
        "fr_max": max(row["fr"] for row in rows),
    }


def write_excludes(build_result: dict) -> None:
    for tier in ("edu", "modern", "phrase"):
        rows = build_result[tier].get("exclude_rows", [])
        if not rows:
            continue
        path = EXCLUDE_DIR / f"{tier}.tsv"
        with path.open("w", encoding="utf-8") as f:
            for row in rows:
                f.write(f"{row['t']}\t{row['pm_raw']}\t{row['fr']}\t{row['reason']}\n")


def write_manifest(
    source_manifest: list[dict], build_result: dict, shards: list[dict]
) -> None:
    manifest = {
        "version": 1,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "sources": source_manifest,
        "totals": {
            "chars": build_result["chars"]["stats"]["total"],
            "edu": build_result["edu"]["stats"]["total"],
            "modern": build_result["modern"]["stats"]["total"],
            "phrase": build_result["phrase"]["stats"]["total"],
            "shards": len(shards),
        },
        "word_buckets": build_result["word_buckets"],
        "shards": shards,
    }
    MANIFEST_PATH.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
