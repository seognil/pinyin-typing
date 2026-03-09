from __future__ import annotations

from datetime import datetime, timezone

from .groups import META_PATH, WORD_LENGTHS


def _incremental_counts(rows: list[dict], length: int) -> tuple[int, int, int]:
    lv1 = 0
    lv2 = 0
    lv3 = 0
    for row in rows:
        if len(row["t"]) != length:
            continue
        if row["l"] == 1:
            lv1 += 1
        elif row["l"] in {2, 3}:
            lv2 += 1
        else:
            lv3 += 1
    return lv1, lv2, lv3


def build_meta(build_result: dict, shards: list[dict]) -> None:
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    edu_rows = build_result["edu"]["rows"]
    modern_rows = build_result["modern"]["rows"]
    phrase_rows = build_result["phrase"]["rows"]
    chars_stats = build_result["chars"]["stats"]
    lines = [
        "# Data Meta",
        "",
        f"- generated_at: `{generated_at}`",
        f"- chars total: `{chars_stats['total']}`",
        f"- chars lv1: `{chars_stats['lv1']}`",
        f"- chars lv2: `{chars_stats['lv2']}`",
        f"- chars lv3: `{chars_stats['lv3']}`",
        f"- edu total: `{build_result['edu']['stats']['total']}`",
        f"- modern total: `{build_result['modern']['stats']['total']}`",
        f"- phrase total: `{build_result['phrase']['stats']['total']}`",
        f"- shard total: `{len(shards)}`",
        "",
        "## Word Buckets",
        "",
    ]
    for bucket in build_result["word_buckets"]:
        lines.append(
            "- {id}: `{rows}` rows, `fr {start}..{end}`".format(
                id=bucket["id"],
                rows=bucket["rows"],
                start=bucket["fr_start"],
                end=bucket["fr_end"],
            )
        )

    lines.extend(
        [
            "",
            "## Edu",
            "",
        ]
    )
    for length in sorted(WORD_LENGTHS):
        lv1, lv2, lv3 = _incremental_counts(edu_rows, length)
        lines.extend(
            [
                f"- len{length} lv1: `{lv1}`",
                f"- len{length} lv2 +=: `{lv2}`",
                f"- len{length} lv3 +=: `{lv3}`",
            ]
        )
    lines.extend(["", "### Filtered", ""])
    for key, value in build_result["edu"]["stats"]["filters"].items():
        lines.append(f"- {key}: `{value}`")

    lines.extend(["", "## Modern", ""])
    for length in sorted(WORD_LENGTHS):
        lv1, lv2, lv3 = _incremental_counts(modern_rows, length)
        lines.extend(
            [
                f"- len{length} lv1: `{lv1}`",
                f"- len{length} lv2 +=: `{lv2}`",
                f"- len{length} lv3 +=: `{lv3}`",
            ]
        )
    lines.extend(["", "### Filtered", ""])
    for key, value in build_result["modern"]["stats"]["filters"].items():
        lines.append(f"- {key}: `{value}`")

    lines.extend(["", "## Phrase", ""])
    for length in sorted(WORD_LENGTHS):
        lv1, lv2, lv3 = _incremental_counts(phrase_rows, length)
        lines.extend(
            [
                f"- len{length} lv1: `{lv1}`",
                f"- len{length} lv2 +=: `{lv2}`",
                f"- len{length} lv3 +=: `{lv3}`",
            ]
        )
    lines.extend(["", "### Filtered", ""])
    for key, value in build_result["phrase"]["stats"]["filters"].items():
        lines.append(f"- {key}: `{value}`")

    lines.extend(["", "## Chars", ""])
    for key, value in chars_stats.items():
        if key in {"total", "lv1", "lv2", "lv3"}:
            continue
        lines.append(f"- {key}: `{value}`")

    META_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
