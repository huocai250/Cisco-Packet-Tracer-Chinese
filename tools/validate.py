"""Sanity-check the generated translation file."""

import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

WORK = Path(__file__).resolve().parent
OUT = WORK / "out" / "chinese_chi.ts"

PLACEHOLDER_RE = re.compile(r"%\d+|%n|\[\[[^\]]+\]\]")
TAG_RE = re.compile(r"</?[a-zA-Z][^>]*>")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    root = ET.parse(OUT).getroot()
    bad_placeholders = []
    bad_tags = []
    translated = 0
    total = 0
    for ctx in root.findall("context"):
        for msg in ctx.findall("message"):
            total += 1
            src = msg.find("source").text or ""
            node = msg.find("translation")
            if node is None:
                continue
            # 复数消息（numerusform）的译文在内层节点里
            forms = node.findall("numerusform")
            zh = "".join(form.text or "" for form in forms) if forms else (node.text or "")
            if not zh:
                continue
            translated += 1
            if Counter(PLACEHOLDER_RE.findall(src)) != Counter(PLACEHOLDER_RE.findall(zh)):
                bad_placeholders.append((src, zh))
            src_tags = Counter(TAG_RE.findall(src))
            zh_tags = Counter(TAG_RE.findall(zh))
            if src_tags != zh_tags and src:
                bad_tags.append((src, zh))

    print(f"messages={total} translated={translated} "
          f"placeholder-mismatch={len(bad_placeholders)} tag-mismatch={len(bad_tags)}")
    for src, zh in bad_placeholders[:25]:
        print("PLACEHOLDER", repr(src[:90]), "->", repr(zh[:90]))
    for src, zh in bad_tags[:15]:
        print("TAG", repr(src[:90]), "->", repr(zh[:90]))


if __name__ == "__main__":
    main()
