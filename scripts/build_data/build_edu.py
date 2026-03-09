from __future__ import annotations

import csv

from .groups import (
    CHINESE_RE,
    EDU_SOURCE_PATH,
    WORD_LENGTHS,
    encode_groups,
    level_bitmap,
)
from .word_pinyin import parse_edu_pinyin


def build_edu(char_levels: dict[str, int]) -> dict:
    filters = {
        "invalid_text": 0,
        "invalid_pm": 0,
        "invalid_length": 0,
        "non_8105": 0,
    }
    excludes = []
    rows = []
    seen_texts: set[str] = set()

    with EDU_SOURCE_PATH.open("r", encoding="utf-8") as f:
        for row_index, row in enumerate(csv.DictReader(f, delimiter="\t"), start=1):
            text = (row.get("词语") or "").strip()
            pm_raw = (row.get("拼音") or "").strip()
            level_raw = (row.get("分级") or "").strip()
            if not text or not CHINESE_RE.fullmatch(text):
                filters["invalid_text"] += 1
                continue
            if len(text) not in WORD_LENGTHS:
                filters["invalid_length"] += 1
                continue
            if text in seen_texts:
                continue
            seen_texts.add(text)
            if any(char not in char_levels for char in text):
                filters["non_8105"] += 1
                excludes.append(
                    {
                        "t": text,
                        "pm_raw": pm_raw,
                        "fr": row_index,
                        "reason": "non_8105",
                    }
                )
                continue
            pm_list = parse_edu_pinyin(text, pm_raw)
            if pm_list is None:
                filters["invalid_pm"] += 1
                excludes.append(
                    {
                        "t": text,
                        "pm_raw": pm_raw,
                        "fr": row_index,
                        "reason": "invalid_pm",
                    }
                )
                continue
            edu_level = int(level_raw) if level_raw.isdigit() else 4
            rows.append(
                {
                    "t": text,
                    "pm": " ".join(pm_list),
                    "source_fr": row_index,
                    "edu_level": edu_level,
                    "g": encode_groups(pm_list),
                    "l": level_bitmap(text, char_levels),
                }
            )

    rows.sort(key=lambda item: (item["edu_level"], item["source_fr"], item["t"]))
    return {
        "rows": rows,
        "texts": {row["t"] for row in rows},
        "stats": {
            "total": len(rows),
            "filters": filters,
        },
        "exclude_rows": excludes,
    }
