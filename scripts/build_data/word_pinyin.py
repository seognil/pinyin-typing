from __future__ import annotations

import re
from collections import Counter
from functools import lru_cache

from .groups import CHAR_PINYIN_PATH, MARKED_TO_PLAIN

PINYIN_SEPARATORS_RE = re.compile(r"[\-·'’/]+")
PINYIN_VOWELS = set("aeiouv")


def parse_modern_candidates(text: str, pm_raw: str) -> list[list[str]]:
    candidates = []
    for raw_candidate in pm_raw.split("、"):
        pm = [item.strip() for item in raw_candidate.split() if item.strip()]
        if len(pm) == len(text):
            candidates.append(pm)
    return candidates


def choose_candidate(candidates: list[list[str]]) -> list[str] | None:
    counts = Counter(tuple(candidate) for candidate in candidates)
    if not counts:
        return None
    best, _ = counts.most_common(1)[0]
    return list(best)


def _plain_syllable(syllable: str) -> str:
    plain_chars: list[str] = []
    for char in syllable.strip().lower():
        plain_chars.append(MARKED_TO_PLAIN.get(char, char))
    return "".join(plain_chars)


@lru_cache(maxsize=1)
def valid_plain_syllables() -> frozenset[str]:
    syllables: set[str] = set()
    for raw in CHAR_PINYIN_PATH.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or "\t" not in line:
            continue
        text, marked = line.split("\t", 1)
        if len(text.strip()) != 1:
            continue
        for item in marked.split():
            plain = _plain_syllable(item)
            if plain:
                syllables.add(plain)
    return frozenset(syllables)


def _parse_marked_chunks(compact: str, syllable_count: int) -> tuple[str, ...] | None:
    valid_syllables = valid_plain_syllables()

    @lru_cache(maxsize=None)
    def dfs(index: int, remain: int) -> tuple[str, ...] | None:
        if index == len(compact):
            return () if remain == 0 else None
        if remain <= 0:
            return None
        for end in range(index + 1, min(len(compact), index + 8) + 1):
            chunk = compact[index:end]
            plain = _plain_syllable(chunk)
            if plain not in valid_syllables:
                continue
            if not (set(plain) & PINYIN_VOWELS):
                continue
            rest = dfs(end, remain - 1)
            if rest is not None:
                return (chunk,) + rest
        return None

    return dfs(0, syllable_count)


def parse_edu_pinyin(text: str, pm_raw: str) -> list[str] | None:
    compact = PINYIN_SEPARATORS_RE.sub("", pm_raw.strip().replace(" ", ""))
    if not compact:
        return None

    direct = _parse_marked_chunks(compact, len(text))
    if direct is not None:
        return list(direct)

    # Edu source uses merged erhua such as "huar" for words ending in "儿".
    if text.endswith("儿") and compact.endswith("r") and len(text) >= 2:
        stem = _parse_marked_chunks(compact[:-1], len(text) - 1)
        if stem is not None:
            return [*stem, "ér"]
    return None
