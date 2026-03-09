from __future__ import annotations

import json

from .groups import (
    CHINESE_RE,
    PHRASE_SOURCE_PATH,
    WORD_LENGTHS,
    encode_groups,
    level_bitmap,
)


def build_phrase(skip_texts: set[str], char_levels: dict[str, int]) -> dict:
    phrase_map = json.loads(PHRASE_SOURCE_PATH.read_text(encoding="utf-8"))
    filters = {
        "invalid_text": 0,
        "invalid_pm": 0,
        "invalid_length": 0,
        "non_8105": 0,
        "duplicate_by_previous": 0,
    }
    excludes = []
    rows = []
    seen_texts: set[str] = set()
    for row_index, (text, value) in enumerate(phrase_map.items(), start=1):
        if not text or not CHINESE_RE.fullmatch(text):
            filters["invalid_text"] += 1
            continue
        if len(text) not in WORD_LENGTHS:
            filters["invalid_length"] += 1
            continue
        if text in skip_texts:
            filters["duplicate_by_previous"] += 1
            continue
        if any(char not in char_levels for char in text):
            filters["non_8105"] += 1
            excludes.append(
                {
                    "t": text,
                    "pm_raw": json.dumps(value, ensure_ascii=False),
                    "fr": row_index,
                    "reason": "non_8105",
                }
            )
            continue
        if not isinstance(value, list) or not value:
            filters["invalid_pm"] += 1
            excludes.append(
                {
                    "t": text,
                    "pm_raw": json.dumps(value, ensure_ascii=False),
                    "fr": row_index,
                    "reason": "invalid_pm",
                }
            )
            continue
        if any(not isinstance(item, list) or len(item) != 1 for item in value):
            filters["invalid_pm"] += 1
            excludes.append(
                {
                    "t": text,
                    "pm_raw": json.dumps(value, ensure_ascii=False),
                    "fr": row_index,
                    "reason": "invalid_pm",
                }
            )
            continue
        pm_list = [item[0].strip() for item in value if item and item[0].strip()]
        if len(pm_list) != len(text):
            filters["invalid_pm"] += 1
            excludes.append(
                {
                    "t": text,
                    "pm_raw": json.dumps(value, ensure_ascii=False),
                    "fr": row_index,
                    "reason": "invalid_pm",
                }
            )
            continue
        if text in seen_texts:
            continue
        seen_texts.add(text)
        rows.append(
            {
                "t": text,
                "pm": " ".join(pm_list),
                "source_fr": row_index,
                "g": encode_groups(pm_list),
                "l": level_bitmap(text, char_levels),
            }
        )

    rows.sort(key=lambda item: (item["source_fr"], item["t"]))
    return {
        "rows": rows,
        "texts": {row["t"] for row in rows},
        "stats": {
            "total": len(rows),
            "filters": filters,
        },
        "exclude_rows": excludes,
    }
