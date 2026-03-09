from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = ROOT / ".source"
DATA_DIR = ROOT / "data"
SHARDS_DIR = DATA_DIR / "shards"
EXCLUDE_DIR = SOURCE_DIR / "output-exclude"
MANIFEST_PATH = DATA_DIR / "manifest.json"
META_PATH = DATA_DIR / "meta.md"
WORD_LENGTHS = {2, 3, 4}
SHARD_TARGET_BYTES = 256 * 1024

OFFICIAL_CHARS_PATH = (
    SOURCE_DIR / "general-standard-chars" / "1-8105纯汉字（按顺序排列）.txt"
)
CHAR_PINYIN_PATH = (
    SOURCE_DIR / "general-standard-chars" / "3-单个汉字+发音（带声调）.txt"
)
BASE_MODERN_PATH = SOURCE_DIR / "hanzi-words-cycb" / "现代汉语常用词表（第2版）.tsv"
EXTEND_SOURCE_PATH = SOURCE_DIR / "python-pinyin" / "phrases_dict.json"

CHINESE_RE = re.compile(r"^[\u3400-\u4dbf\u4e00-\u9fff]+$")
INITIALS = [
    "zh",
    "ch",
    "sh",
    "b",
    "p",
    "m",
    "f",
    "d",
    "t",
    "n",
    "l",
    "g",
    "k",
    "h",
    "j",
    "q",
    "x",
    "r",
    "z",
    "c",
    "s",
    "y",
    "w",
]
FINAL_GROUPS = {
    "en-eng": {"en", "eng"},
    "in-ing": {"in", "ing"},
    "an-ang": {"an", "ang"},
    "ian-iang": {"ian", "iang"},
    "uan-uang": {"uan", "uang"},
    "ai-ei": {"ai", "ei"},
    "ao-ou": {"ao", "ou"},
    "ia-ie": {"ia", "ie"},
    "ua-uo": {"ua", "uo"},
}
INITIAL_GROUPS = {
    "z-zh": {"z", "zh"},
    "c-ch": {"c", "ch"},
    "s-sh": {"s", "sh"},
    "n-l": {"n", "l"},
    "h-f": {"h", "f"},
    "r-l": {"r", "l"},
    "j-q-x": {"j", "q", "x"},
}
GROUP_ORDER = [
    "en-eng",
    "in-ing",
    "an-ang",
    "ian-iang",
    "uan-uang",
    "ai-ei",
    "ao-ou",
    "ia-ie",
    "ua-uo",
    "z-zh",
    "c-ch",
    "s-sh",
    "n-l",
    "h-f",
    "r-l",
    "j-q-x",
    "rest",
]
MARKED_TO_PLAIN = {
    "a": "a",
    "ā": "a",
    "á": "a",
    "ǎ": "a",
    "à": "a",
    "e": "e",
    "ē": "e",
    "é": "e",
    "ě": "e",
    "è": "e",
    "i": "i",
    "ī": "i",
    "í": "i",
    "ǐ": "i",
    "ì": "i",
    "o": "o",
    "ō": "o",
    "ó": "o",
    "ǒ": "o",
    "ò": "o",
    "u": "u",
    "ū": "u",
    "ú": "u",
    "ǔ": "u",
    "ù": "u",
    "ǖ": "v",
    "ǘ": "v",
    "ǚ": "v",
    "ǜ": "v",
    "ü": "v",
    "ê": "e",
    "ń": "n",
    "ň": "n",
    "ǹ": "n",
    "ḿ": "m",
    "·": "",
}


def reset_data_dir() -> None:
    if DATA_DIR.exists():
        import shutil

        shutil.rmtree(DATA_DIR)
    if EXCLUDE_DIR.exists():
        import shutil

        shutil.rmtree(EXCLUDE_DIR)
    SHARDS_DIR.mkdir(parents=True, exist_ok=True)
    EXCLUDE_DIR.mkdir(parents=True, exist_ok=True)


def syllable_to_plain(syllable: str) -> str:
    plain_chars: list[str] = []
    for char in syllable.strip().lower():
        plain_chars.append(MARKED_TO_PLAIN.get(char, char))
    return "".join(plain_chars)


def split_initial_final(syllable: str) -> tuple[str, str]:
    plain = syllable_to_plain(syllable)
    for initial in INITIALS:
        if plain.startswith(initial):
            return initial, plain[len(initial) :]
    return "", plain


def resolve_groups(pm_list: list[str]) -> set[str]:
    initials = []
    finals = []
    for syllable in pm_list:
        initial, final = split_initial_final(syllable)
        initials.append(initial)
        finals.append(final)
    matched = {
        group
        for group, allowed in FINAL_GROUPS.items()
        if any(final in allowed for final in finals)
    }
    matched |= {
        group
        for group, allowed in INITIAL_GROUPS.items()
        if any(initial in allowed for initial in initials)
    }
    return matched or {"rest"}


def encode_groups(pm_list: list[str]) -> str:
    groups = sorted(resolve_groups(pm_list), key=GROUP_ORDER.index)
    if groups == ["rest"]:
        return ""
    return ",".join(groups)


def char_level_bit(fr: int) -> int:
    if 1 <= fr <= 3500:
        return 1
    if 3501 <= fr <= 6500:
        return 2
    if 6501 <= fr <= 8105:
        return 4
    raise ValueError(f"unexpected character rank: {fr}")


def level_bitmap(text: str, char_levels: dict[str, int]) -> int:
    bitmap = 0
    for char in text:
        bitmap |= char_levels[char]
    return bitmap
