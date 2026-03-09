from __future__ import annotations

import json
import os
import time
import urllib.request
from pathlib import Path

from .groups import ROOT, SOURCE_DIR


SOURCES = [
    {
        "name": "hanzi-words-cycb",
        "repo": "zispace/hanzi-words-cycb",
        "license": "unknown",
        "files": {
            "现代汉语常用词表（第2版）.tsv": "https://raw.githubusercontent.com/zispace/hanzi-words-cycb/main/%E7%8E%B0%E4%BB%A3%E6%B1%89%E8%AF%AD%E5%B8%B8%E7%94%A8%E8%AF%8D%E8%A1%A8%EF%BC%88%E7%AC%AC2%E7%89%88%EF%BC%89.tsv",
        },
    },
    {
        "name": "general-standard-chars",
        "repo": "iDvel/The-Table-of-General-Standard-Chinese-Characters",
        "license": "unknown",
        "files": {
            "1-8105纯汉字（按顺序排列）.txt": "https://raw.githubusercontent.com/iDvel/The-Table-of-General-Standard-Chinese-Characters/master/1-8105%E7%BA%AF%E6%B1%89%E5%AD%97%EF%BC%88%E6%8C%89%E9%A1%BA%E5%BA%8F%E6%8E%92%E5%88%97%EF%BC%89.txt",
            "3-单个汉字+发音（带声调）.txt": "https://raw.githubusercontent.com/iDvel/The-Table-of-General-Standard-Chinese-Characters/master/3-%E5%8D%95%E4%B8%AA%E6%B1%89%E5%AD%97%2B%E5%8F%91%E9%9F%B3%EF%BC%88%E5%B8%A6%E5%A3%B0%E8%B0%83%EF%BC%89.txt",
        },
    },
    {
        "name": "python-pinyin",
        "repo": "mozillazg/python-pinyin",
        "license": "MIT",
        "files": {
            "phrases_dict.json": "https://raw.githubusercontent.com/mozillazg/python-pinyin/master/pypinyin/phrases_dict.json",
        },
    },
]


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    last_error = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(url) as response:
                dest.write_bytes(response.read())
            return
        except Exception as exc:  # pragma: no cover
            last_error = exc
            time.sleep(1 + attempt)
    raise last_error


def fetch_sources() -> list[dict]:
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    manifest = []
    for source in SOURCES:
        source_dir = SOURCE_DIR / source["name"]
        source_dir.mkdir(parents=True, exist_ok=True)
        for filename, url in source["files"].items():
            dest = source_dir / filename
            if dest.exists() and dest.stat().st_size > 0:
                print(f"skip {source['name']}/{filename}")
            else:
                print(f"fetch {source['name']}/{filename}")
                download(url, dest)
            manifest.append(
                {
                    "source": source["name"],
                    "repo": source["repo"],
                    "license": source["license"],
                    "filename": filename,
                    "url": url,
                    "size": dest.stat().st_size,
                    "path": os.path.relpath(dest, ROOT),
                }
            )
    manifest_path = SOURCE_DIR / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {manifest_path}")
    return manifest
