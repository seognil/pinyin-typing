from __future__ import annotations

import csv

from .groups import (
    MODERN_SOURCE_PATH,
    CHINESE_RE,
    WORD_LENGTHS,
    encode_groups,
    level_bitmap,
)
from .word_pinyin import choose_candidate, parse_modern_candidates


def build_modern(skip_texts: set[str], char_levels: dict[str, int]) -> dict:
    entries: dict[str, dict] = {}
    filters = {
        "invalid_text": 0,
        "invalid_pm": 0,
        "invalid_length": 0,
        "non_8105": 0,
        "no_valid_candidate": 0,
        "duplicate_by_edu": 0,
    }
    excludes = []
    invalid_pm_texts: set[str] = set()

    with MODERN_SOURCE_PATH.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row_index, row in enumerate(reader, start=1):
            text = (row.get("词语") or "").strip()
            pm_raw = (row.get("拼音（列表）") or "").strip()
            if not text or not CHINESE_RE.fullmatch(text):
                filters["invalid_text"] += 1
                continue
            if len(text) not in WORD_LENGTHS:
                filters["invalid_length"] += 1
                continue
            if not pm_raw:
                filters["invalid_pm"] += 1
                excludes.append(
                    {
                        "t": text,
                        "pm_raw": pm_raw,
                        "fr": row_index,
                        "reason": "invalid_pm",
                    }
                )
                invalid_pm_texts.add(text)
                continue
            entry = entries.setdefault(
                text, {"text": text, "source_fr": row_index, "candidates": []}
            )
            candidates = parse_modern_candidates(text, pm_raw)
            if candidates:
                entry["candidates"].append(candidates[0])
            else:
                filters["invalid_pm"] += 1
                excludes.append(
                    {
                        "t": text,
                        "pm_raw": pm_raw,
                        "fr": row_index,
                        "reason": "invalid_pm",
                    }
                )
                invalid_pm_texts.add(text)

    all_rows = []
    delta_rows = []
    for text in sorted(entries):
        entry = entries[text]
        pm_list = choose_candidate(entry["candidates"])
        if pm_list is None:
            filters["no_valid_candidate"] += 1
            if text not in invalid_pm_texts:
                excludes.append(
                    {
                        "t": text,
                        "pm_raw": "",
                        "fr": entry["source_fr"],
                        "reason": "no_valid_candidate",
                    }
                )
            continue
        if any(char not in char_levels for char in text):
            filters["non_8105"] += 1
            excludes.append(
                {
                    "t": text,
                    "pm_raw": " ".join(pm_list),
                    "fr": entry["source_fr"],
                    "reason": "non_8105",
                }
            )
            continue
        row = {
            "t": text,
            "pm": " ".join(pm_list),
            "source_fr": entry["source_fr"],
            "g": encode_groups(pm_list),
            "l": level_bitmap(text, char_levels),
        }
        all_rows.append(row)
        if text in skip_texts:
            filters["duplicate_by_edu"] += 1
            continue
        delta_rows.append(dict(row))

    all_rows.sort(key=lambda item: (item["source_fr"], item["t"]))
    delta_rows.sort(key=lambda item: (item["source_fr"], item["t"]))
    return {
        "rows": delta_rows,
        "all_rows": all_rows,
        "texts": {row["t"] for row in delta_rows},
        "source_rank": {row["t"]: row["source_fr"] for row in all_rows},
        "stats": {
            "total": len(delta_rows),
            "all_total": len(all_rows),
            "filters": filters,
        },
        "exclude_rows": excludes,
    }
