"""Build the translated chinese_chi.ts from translation part files and release it.

Part files: work/tr/part_XXX.txt with lines:  <id><TAB><chinese text>
(use \\n for a newline inside the text, \\t for a tab)
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

WORK = Path(__file__).resolve().parent
DEFAULT_TS = Path(r"D:\Program Files\Cisco Packet Tracer 9.0.1\languages\default.ts")
DEFAULT_LRELEASE = Path(r"D:\Program Files\Cisco Packet Tracer 9.0.1\bin\lrelease.exe")
OUT_TS = WORK / "out" / "chinese_chi.ts"

MESSAGE_RE = re.compile(r"<message[^>]*>(.*?)</message>", re.S)
SOURCE_RE = re.compile(r"<source>(.*?)</source>", re.S)
TRANS_RE = re.compile(r"<translation[^>]*>(.*?)</translation>", re.S)
NUMERUS_RE = re.compile(r"<numerusform>.*?</numerusform>", re.S)
CONTEXT_RE = re.compile(r"<context>(.*?)</context>", re.S)
CONTEXT_NAME_RE = re.compile(r"<name>(.*?)</name>", re.S)
OVERRIDES_PATH = WORK / "tr_ctx.json"


def unescape(text: str) -> str:
    return (
        text.replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&quot;", '"')
        .replace("&apos;", "'")
        .replace("&amp;", "&")
    )


def escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def load_parts() -> dict[int, str]:
    table: dict[int, str] = {}
    for path in sorted((WORK / "tr").glob("part_*.txt")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            raw_id, _, text = line.partition("\t")
            table[int(raw_id)] = (
                text.replace("\\n", "\n").replace("\\t", "\t").replace("{BS}", "\\")
            )
    return table


def main() -> int:
    parser = argparse.ArgumentParser(description="合成中文 .ts 并编译成 .ptl")
    parser.add_argument("--ts", default=str(DEFAULT_TS), help="官方模板 default.ts 路径")
    parser.add_argument("--lrelease", default=str(DEFAULT_LRELEASE),
                        help="Packet Tracer 自带 lrelease.exe 路径")
    args = parser.parse_args()
    src_ts = Path(args.ts)
    lrelease = Path(args.lrelease)

    sys.stdout.reconfigure(encoding="utf-8")
    manifest_path = WORK / "manifest.json"
    if not manifest_path.exists():
        raise SystemExit("缺少 manifest.json，请先运行 build_chunks.py --ts <default.ts>")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    parts = load_parts()
    overrides = json.loads(OVERRIDES_PATH.read_text(encoding="utf-8")) if OVERRIDES_PATH.exists() else {}

    by_src: dict[str, str] = {}
    unknown = []
    for key, text in parts.items():
        entry = manifest.get(str(key))
        if entry is None:
            unknown.append(key)
            continue
        by_src[entry["src"]] = text

    raw = src_ts.read_text(encoding="utf-8")
    translated = 0
    missed: list[str] = []

    def repl_message(match: re.Match, context: str = "") -> str:
        nonlocal translated
        block = match.group(0)
        src_match = SOURCE_RE.search(block)
        if not src_match:
            return block
        src = unescape(src_match.group(1))
        zh = overrides.get(context, {}).get(src, by_src.get(src))
        if zh is None:
            missed.append(src)
            return block
        if NUMERUS_RE.search(block):
            # Qt plural message: Chinese has a single plural form.
            translated += 1
            updated = NUMERUS_RE.sub(
                lambda _m: "<numerusform>%s</numerusform>" % escape(zh), block, count=1
            )
            return updated.replace('<translation type="unfinished">', "<translation>", 1)
        if not TRANS_RE.search(block):
            return block
        translated += 1
        return TRANS_RE.sub(lambda _m: "<translation>%s</translation>" % escape(zh), block, count=1)

    def repl_context(match: re.Match) -> str:
        body = match.group(0)
        name_match = CONTEXT_NAME_RE.search(body)
        context = unescape(name_match.group(1)) if name_match else ""
        return MESSAGE_RE.sub(lambda m: repl_message(m, context), body)

    out = CONTEXT_RE.sub(repl_context, raw)
    out = out.replace('<TS version="2.1">', '<TS version="2.1" language="zh_CN" sourcelanguage="en_US">', 1)

    OUT_TS.parent.mkdir(parents=True, exist_ok=True)
    OUT_TS.write_text(out, encoding="utf-8")

    total_msgs = len(MESSAGE_RE.findall(raw))
    uniq_missed = {s for s in missed}
    print(f"unique translated: {len(by_src)}  message-level translated: {translated}/{total_msgs}")
    print(f"unknown ids in parts: {len(unknown)} {unknown[:10]}")
    print(f"untranslated unique sources: {len(uniq_missed)}")
    if uniq_missed:
        remaining_chars = sum(len(s) for s in uniq_missed)
        print(f"untranslated chars: {remaining_chars}")

    result = subprocess.run(
        [str(lrelease), str(OUT_TS), "-qm", str(WORK / "out" / "chinese_chi.ptl")],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    print("lrelease rc:", result.returncode)
    print((result.stdout or "").strip()[:2000])
    print((result.stderr or "").strip()[:2000])
    return 0


if __name__ == "__main__":
    sys.exit(main())
