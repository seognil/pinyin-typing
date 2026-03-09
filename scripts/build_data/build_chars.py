from __future__ import annotations

from .groups import CHAR_PINYIN_PATH, OFFICIAL_CHARS_PATH, char_level_bit, encode_groups


def _load_official_chars() -> list[str]:
    chars = [
        char
        for char in OFFICIAL_CHARS_PATH.read_text(encoding="utf-8")
        if not char.isspace()
    ]
    if len(chars) != 8105:
        raise ValueError(f"expected 8105 official chars, got {len(chars)}")
    if len(set(chars)) != 8105:
        raise ValueError("official char list contains duplicates")
    return chars


def _load_first_pinyin() -> tuple[dict[str, str], list[str], int]:
    first_pinyin: dict[str, str] = {}
    ordered_chars: list[str] = []
    duplicate_rows = 0
    for raw in CHAR_PINYIN_PATH.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or "\t" not in line:
            continue
        text, marked = line.split("\t", 1)
        text = text.strip()
        marked = marked.strip()
        if len(text) != 1 or not marked:
            continue
        pm = [item.strip() for item in marked.split() if item.strip()]
        if not pm:
            continue
        if text in first_pinyin:
            duplicate_rows += 1
            continue
        first_pinyin[text] = " ".join(pm)
        ordered_chars.append(text)
    return first_pinyin, ordered_chars, duplicate_rows


def build_chars() -> dict:
    official_chars = _load_official_chars()
    first_pinyin, deduped_order, duplicate_rows = _load_first_pinyin()
    if deduped_order != official_chars:
        raise ValueError(
            "deduped character pronunciation order does not match official 8105 order"
        )

    rows = []
    missing_pinyin = 0
    char_levels: dict[str, int] = {}
    for fr, text in enumerate(official_chars, start=1):
        pm = first_pinyin.get(text)
        if pm is None:
            missing_pinyin += 1
            continue
        level = char_level_bit(fr)
        char_levels[text] = level
        rows.append(
            {"t": text, "pm": pm, "fr": fr, "g": encode_groups([pm]), "l": level}
        )

    if missing_pinyin:
        raise ValueError(f"missing pinyin for {missing_pinyin} official chars")

    return {
        "rows": rows,
        "char_levels": char_levels,
        "stats": {
            "total": len(rows),
            "lv1": 3500,
            "lv2": 3000,
            "lv3": 1605,
            "duplicate_pronunciation_rows": duplicate_rows,
            "missing_pinyin": missing_pinyin,
        },
    }
