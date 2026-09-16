"""Extract unique source strings from default.ts and split into translation chunks.

Outputs:
  work/src/chunk_XXX.txt  ->  "ID<TAB>source-with-\\n-escapes" lines
  work/manifest.json      ->  id -> {src, contexts}
"""

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

WORK = Path(__file__).resolve().parent
DEFAULT_TS = Path(r"D:\Program Files\Cisco Packet Tracer 9.0.1\languages\default.ts")
CHUNK_SIZE = 200

# Strings that are pure numbers / punctuation / placeholders: nothing to translate.
SKIP_RE = re.compile(r"^[\s0-9.,:;!?%()\[\]{}<>=+\-*/\\|~`'\"#@$^&_]*$")


def main() -> None:
    parser = argparse.ArgumentParser(description="从官方 default.ts 抽取待翻译字符串并分片")
    parser.add_argument("--ts", default=str(DEFAULT_TS),
                        help="官方模板 default.ts 的路径（默认取 PT 9.0.1 安装目录）")
    args = parser.parse_args()
    src_ts = Path(args.ts)
    if not src_ts.exists():
        raise SystemExit(f"找不到模板文件：{src_ts}\n请用 --ts 指定你的 Packet Tracer "
                         f"languages\\default.ts 路径")

    root = ET.parse(src_ts).getroot()
    order: dict[str, dict] = {}
    for ctx in root.findall("context"):
        name = ctx.find("name").text or ""
        for msg in ctx.findall("message"):
            src = msg.find("source").text or ""
            entry = order.setdefault(src, {"src": src, "contexts": []})
            if name not in entry["contexts"]:
                entry["contexts"].append(name)

    todo = []
    skipped = []
    for src, entry in order.items():
        if SKIP_RE.match(src) or not src.strip():
            skipped.append(src)
        else:
            todo.append(entry)

    # Priority: shorter strings first (UI chrome before help paragraphs),
    # ties broken by source text for stable ordering.
    todo.sort(key=lambda e: (len(e["src"]), e["src"]))

    src_dir = WORK / "src"
    src_dir.mkdir(parents=True, exist_ok=True)
    for old in src_dir.glob("chunk_*.txt"):
        old.unlink()

    manifest = {}
    for idx, entry in enumerate(todo, start=1):
        entry["id"] = idx
        manifest[str(idx)] = {"src": entry["src"], "contexts": entry["contexts"]}

    for start in range(0, len(todo), CHUNK_SIZE):
        part = todo[start:start + CHUNK_SIZE]
        num = start // CHUNK_SIZE + 1
        lines = []
        for entry in part:
            src = entry["src"].replace("\\", "\\\\").replace("\n", "\\n").replace("\t", "\\t")
            lines.append(f"{entry['id']}\t{src}")
        (src_dir / f"chunk_{num:03d}.txt").write_text("\n".join(lines), encoding="utf-8")

    (WORK / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=0), encoding="utf-8"
    )

    total_chars = sum(len(e["src"]) for e in todo)
    print(f"todo={len(todo)} chunks={(len(todo) + CHUNK_SIZE - 1) // CHUNK_SIZE} "
          f"chars={total_chars} skipped={len(skipped)}")


if __name__ == "__main__":
    sys.exit(main())
