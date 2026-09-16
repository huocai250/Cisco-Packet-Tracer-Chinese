"""Extract zlib-compressed JSON resources embedded in PacketTracer.exe.

用法：
    python dump_resources.py [--exe "D:\\...\\bin\\PacketTracer.exe"]

结果写入 out/（例如 out/DeviceTypesConfig.json），用于对照或重新生成中文版。
注意：这里抽取的是 Cisco 的原始数据，请勿将其提交到公开仓库（.gitignore 已忽略 out/）。
"""

import argparse
import json
import re
import sys
import zlib
from pathlib import Path

WORK = Path(__file__).resolve().parent
DEFAULT_EXE = Path(r"D:\Program Files\Cisco Packet Tracer 9.0.1\bin\PacketTracer.exe")
OUT = WORK / "out"

NAME_RE = re.compile(rb"@:(/[A-Za-z0-9_./-]+\.json)")


def main() -> None:
    parser = argparse.ArgumentParser(description="从 PacketTracer.exe 抽取内置 JSON 资源")
    parser.add_argument("--exe", default=str(DEFAULT_EXE), help="PacketTracer.exe 路径")
    args = parser.parse_args()

    sys.stdout.reconfigure(encoding="utf-8")
    OUT.mkdir(exist_ok=True)
    exe = Path(args.exe)
    if not exe.exists():
        raise SystemExit(f"找不到 {exe}")
    data = exe.read_bytes()

    names = {}
    for m in NAME_RE.finditer(data):
        names[m.start()] = m.group(1).decode()

    found = []
    for i in range(len(data) - 2):
        if data[i] != 0x78 or data[i + 1] not in (0x01, 0x9C, 0xDA, 0x5E):
            continue
        try:
            size = int.from_bytes(data[i - 4:i], "big")
            if size <= 0 or size > 8_000_000:
                continue
            obj = zlib.decompressobj()
            out = obj.decompress(data[i:i + size * 2 + 4096], size)
        except Exception:
            continue
        if len(out) != size or not obj.eof:
            continue
        if not out.lstrip().startswith(b"{"):
            continue
        try:
            json.loads(out.decode("utf-8"))
        except Exception:
            continue
        found.append((i, size, out))

    for i, size, out in found:
        # find a resource name whose declared blob is closest before this stream
        candidate = None
        for off, name in sorted(names.items()):
            if off < i and (candidate is None or off > candidate[0]):
                if i - off < 4096:
                    candidate = (off, name)
        if candidate:
            label = Path(candidate[1]).name
        else:
            label = f"unknown_{i}.json"
        path = OUT / label
        path.write_bytes(out)
        text = out.decode("utf-8", "replace")
        strings = re.findall(r'"(?:name|tooltip|accessibleName|title|label|text)"\s*:\s*"([^"]+)"', text)
        print(f"{i:>9} {size:>7} {label:<40} ui-strings={len(strings)}")
        for s in strings[:6]:
            print("            ", s)


if __name__ == "__main__":
    main()
