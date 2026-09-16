"""List source strings that are still untranslated, to review coverage."""

import json
import re
import sys
from pathlib import Path

WORK = Path(__file__).resolve().parent


def load_parts() -> set[int]:
    ids = set()
    for path in sorted((WORK / "tr").glob("part_*.txt")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                ids.add(int(line.split("\t", 1)[0]))
    return ids


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    manifest = json.loads((WORK / "manifest.json").read_text(encoding="utf-8"))
    done = load_parts()
    left = [(int(k), v["src"]) for k, v in manifest.items() if int(k) not in done]

    text_like = [item for item in left if re.search(r"[A-Za-z]{2,}", item[1])]
    text_like.sort(key=lambda item: -len(item[1]))
    print(f"remaining total={len(left)} with-letters={len(text_like)}")
    print("--- longest 60 remaining ---")
    for idx, src in text_like[:60]:
        print(f"{idx}\t{src[:150]!r}")
    print("--- shortest 40 remaining ---")
    for idx, src in sorted(text_like, key=lambda item: len(item[1]))[:40]:
        print(f"{idx}\t{src!r}")


if __name__ == "__main__":
    main()
