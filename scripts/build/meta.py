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
    base_rows = build_result["base"]["rows"]
    extend_rows = build_result["extend"]["rows"]
    chars_stats = build_result["chars"]["stats"]
    lines = [
        "# Data Meta",
        "",
        f"- generated_at: `{generated_at}`",
        f"- chars total: `{chars_stats['total']}`",
        f"- chars lv1: `{chars_stats['lv1']}`",
        f"- chars lv2: `{chars_stats['lv2']}`",
        f"- chars lv3: `{chars_stats['lv3']}`",
        f"- base total: `{build_result['base']['stats']['total']}`",
        f"- extend total: `{build_result['extend']['stats']['total']}`",
        f"- shard total: `{len(shards)}`",
        "",
        "## Base",
        "",
    ]
    for length in sorted(WORD_LENGTHS):
        lv1, lv2, lv3 = _incremental_counts(base_rows, length)
        lines.extend(
            [
                f"- len{length} lv1: `{lv1}`",
                f"- len{length} lv2 +=: `{lv2}`",
                f"- len{length} lv3 +=: `{lv3}`",
            ]
        )
    lines.extend(["", "### Filtered", ""])
    for key, value in build_result["base"]["stats"]["filters"].items():
        lines.append(f"- {key}: `{value}`")

    lines.extend(["", "## Extend", ""])
    for length in sorted(WORD_LENGTHS):
        lv1, lv2, lv3 = _incremental_counts(extend_rows, length)
        lines.extend(
            [
                f"- len{length} lv1: `{lv1}`",
                f"- len{length} lv2 +=: `{lv2}`",
                f"- len{length} lv3 +=: `{lv3}`",
            ]
        )
    lines.extend(["", "### Filtered", ""])
    for key, value in build_result["extend"]["stats"]["filters"].items():
        lines.append(f"- {key}: `{value}`")

    lines.extend(["", "## Chars", ""])
    for key, value in chars_stats.items():
        if key in {"total", "lv1", "lv2", "lv3"}:
            continue
        lines.append(f"- {key}: `{value}`")

    META_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
