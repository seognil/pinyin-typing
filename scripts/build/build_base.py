from __future__ import annotations

import csv
from collections import Counter

from .groups import (
    BASE_MODERN_PATH,
    CHINESE_RE,
    WORD_LENGTHS,
    encode_groups,
    level_bitmap,
)


def _parse_pm_candidates(text: str, pm_raw: str) -> list[list[str]]:
    candidates = []
    for raw_candidate in pm_raw.split("、"):
        pm = [item.strip() for item in raw_candidate.split() if item.strip()]
        if len(pm) == len(text):
            candidates.append(pm)
    return candidates


def _choose_candidate(entry: dict) -> list[str] | None:
    counts = Counter(tuple(candidate) for candidate in entry["candidates"])
    if not counts:
        return None
    best, _ = counts.most_common(1)[0]
    return list(best)


def build_base(char_levels: dict[str, int]) -> dict:
    entries: dict[str, dict] = {}
    filters = {
        "invalid_text": 0,
        "invalid_pm": 0,
        "invalid_length": 0,
        "non_8105": 0,
        "no_valid_candidate": 0,
    }
    excludes = []
    invalid_pm_texts: set[str] = set()

    with BASE_MODERN_PATH.open("r", encoding="utf-8") as f:
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
                text, {"text": text, "fr": row_index, "candidates": []}
            )
            candidates = _parse_pm_candidates(text, pm_raw)
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

    rows = []
    texts = set()
    for text in sorted(entries):
        entry = entries[text]
        pm_list = _choose_candidate(entry)
        if pm_list is None:
            filters["no_valid_candidate"] += 1
            if text not in invalid_pm_texts:
                excludes.append(
                    {
                        "t": text,
                        "pm_raw": "",
                        "fr": entry["fr"],
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
                    "fr": entry["fr"],
                    "reason": "non_8105",
                }
            )
            continue
        rows.append(
            {
                "t": text,
                "pm": " ".join(pm_list),
                "fr": entry["fr"],
                "g": encode_groups(pm_list),
                "l": level_bitmap(text, char_levels),
            }
        )
        texts.add(text)

    rows.sort(key=lambda item: (item["fr"], item["t"]))
    return {
        "rows": rows,
        "texts": texts,
        "stats": {
            "total": len(rows),
            "filters": filters,
        },
        "exclude_rows": excludes,
    }
