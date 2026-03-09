from __future__ import annotations


def assign_word_fr(
    edu_rows: list[dict],
    modern_rows: list[dict],
    modern_rank: dict[str, int],
    phrase_rows: list[dict],
) -> dict:
    modern_texts = {row["t"] for row in modern_rows}

    ordered_edu = []
    word_buckets = []
    next_fr = 1
    for edu_level in (1, 2, 3, 4):
        bucket_rows = [row for row in edu_rows if row["edu_level"] == edu_level]
        bucket_rows.sort(
            key=lambda row: (
                modern_rank.get(row["t"]) is None,
                modern_rank.get(row["t"], 10**12),
                row["source_fr"],
                row["t"],
            )
        )
        for row in bucket_rows:
            ordered_edu.append(dict(row))
        if bucket_rows:
            start = next_fr
            end = next_fr + len(bucket_rows) - 1
            word_buckets.append(
                {
                    "id": f"edu-{edu_level}",
                    "tier": "edu",
                    "edu_level": edu_level,
                    "rows": len(bucket_rows),
                    "fr_start": start,
                    "fr_end": end,
                }
            )
            next_fr = end + 1

    ordered_modern = [dict(row) for row in modern_rows]
    if ordered_modern:
        start = next_fr
        end = next_fr + len(ordered_modern) - 1
        word_buckets.append(
            {
                "id": "modern",
                "tier": "modern",
                "rows": len(ordered_modern),
                "fr_start": start,
                "fr_end": end,
            }
        )
        next_fr = end + 1

    ordered_phrase = [dict(row) for row in phrase_rows]
    if ordered_phrase:
        start = next_fr
        end = next_fr + len(ordered_phrase) - 1
        word_buckets.append(
            {
                "id": "phrase",
                "tier": "phrase",
                "rows": len(ordered_phrase),
                "fr_start": start,
                "fr_end": end,
            }
        )
        next_fr = end + 1

    ordered_rows = []
    word_fr = 1
    for row in [*ordered_edu, *ordered_modern, *ordered_phrase]:
        row["fr"] = word_fr
        ordered_rows.append(row)
        word_fr += 1

    rows_by_tier = {"edu": [], "modern": [], "phrase": []}
    for row in ordered_rows:
        if "edu_level" in row:
            rows_by_tier["edu"].append(row)
        elif row["t"] in modern_texts:
            rows_by_tier["modern"].append(row)
        else:
            rows_by_tier["phrase"].append(row)

    return {
        "edu": rows_by_tier["edu"],
        "modern": rows_by_tier["modern"],
        "phrase": rows_by_tier["phrase"],
        "word_buckets": word_buckets,
        "word_total": len(ordered_rows),
    }
