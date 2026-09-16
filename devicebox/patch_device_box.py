#!/usr/bin/env python3
"""把 Packet Tracer 9.0.1 设备箱（Network Devices 那一排）的英文界面文字替换为中文。

原理：设备箱的分类名/工具提示来自 exe 内置资源 DeviceTypesConfig.json
（Qt 资源，zlib 压缩），它不在 languages\\*.ptl 语言文件里，所以语言包翻不到。
本脚本把这 1919 字节的压缩数据原地替换为压缩后的中文版 JSON，
文件总长度与其它字节保持完全不变。

用法（需要管理员权限，因为要写 Program Files）：
    python patch_device_box.py --check      # 只检测，不写文件（默认）
    python patch_device_box.py --apply      # 备份 + 打补丁 + 校验
    python patch_device_box.py --restore    # 用备份还原英文

备份文件：与 PacketTracer.exe 同目录的 PacketTracer.exe.bak
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import zlib
from pathlib import Path

DEFAULT_EXE = Path(r"D:\Program Files\Cisco Packet Tracer 9.0.1\bin\PacketTracer.exe")
SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_JSON = SCRIPT_DIR / "DeviceTypesConfig.zh.json"

MAGIC = (0x01, 0x9C, 0xDA, 0x5E)


def find_blob(data: bytes):
    """在 exe 中定位被压缩的 DeviceTypesConfig.json。"""
    for i in range(4, len(data) - 2):
        if data[i] != 0x78 or data[i + 1] not in MAGIC:
            continue
        size = int.from_bytes(data[i - 4:i], "big")
        if not (1_000 < size < 1_000_000):
            continue
        try:
            obj = zlib.decompressobj()
            probe = data[i:i + size * 2 + 4096]
            out = obj.decompress(probe, size)
        except Exception:
            continue
        if len(out) != size or not obj.eof:
            continue
        if b'"deviceTypesBox"' not in out:
            continue
        consumed = len(probe) - len(obj.unused_data)
        return i, size, consumed, out
    return None


def build_payload(text: bytes, target: int):
    """返回 (新 JSON 字节, 压缩数据)，压缩后的长度恰好等于 target。

    做法：在 JSON 末尾补空格（JSON 允许尾部空白），并尝试多个压缩级别，
    直到压缩结果正好命中原有字节数——这样 exe 的长度和后续数据偏移都不用动。
    """
    for level in (9, 8, 7, 6, 5, 4, 3, 2, 1):
        pad = 0
        while pad <= 120_000:
            blob = text + b" " * pad
            compressed = zlib.compress(blob, level)
            size = len(compressed)
            if size == target:
                return blob, compressed
            if size > target:
                break
            pad += 1
    return None, None


def region_hash(data: bytes, start: int, end: int) -> str:
    """对「挖掉补丁区间」后的文件求哈希，用于确认没有改到别处。"""
    h = hashlib.sha256()
    h.update(data[:start])
    h.update(data[end:])
    return h.hexdigest()


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--exe", default=str(DEFAULT_EXE), help="PacketTracer.exe 路径")
    parser.add_argument("--json", default=str(DEFAULT_JSON), help="中文 JSON 路径")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--apply", action="store_true", help="打补丁")
    group.add_argument("--restore", action="store_true", help="从 .bak 还原")
    parser.add_argument("--check", action="store_true", help="只检测（默认行为）")
    args = parser.parse_args()

    exe = Path(args.exe)
    backup = exe.with_suffix(exe.suffix + ".bak")

    if not exe.exists():
        print(f"找不到 {exe}")
        return 2

    if args.restore:
        if not backup.exists():
            print(f"没有备份文件 {backup}，无法还原")
            return 2
        shutil.copy2(backup, exe)
        print(f"已从备份还原：{exe}")
        return 0

    data = exe.read_bytes()
    found = find_blob(data)
    if not found:
        print("没有在 exe 里找到 DeviceTypesConfig.json 资源：")
        print("  · 可能已经打过补丁（那就无需再打），或")
        print("  · 这个 Packet Tracer 版本的资源布局与 9.0.1 不同。")
        return 3
    stream_start, unpacked_size, stream_len, original = found
    prefix_start = stream_start - 4
    region_end = stream_start + stream_len

    if "网络设备".encode() in original:
        print("这条资源已经是中文了，无需再打补丁。")
        return 0

    print(f"exe 大小            : {len(data):,} 字节")
    print(f"资源位置            : {prefix_start:,} – {region_end:,}（压缩数据 {stream_len} 字节）")
    print(f"原始 JSON           : {unpacked_size:,} 字节")

    zh_text = Path(args.json).read_bytes()
    new_text, payload = build_payload(zh_text, stream_len)
    if payload is None:
        print("中文 JSON 压不进原有的字节空间，已放弃（未做任何修改）。")
        return 4

    new_blob = len(new_text).to_bytes(4, "big") + payload
    assert len(new_blob) == 4 + stream_len

    print(f"中文 JSON           : {len(zh_text):,} 字节"
          f"（补 {len(new_text) - len(zh_text)} 个空格后 {len(new_text):,} 字节）")
    print(f"补丁后压缩长度      : {len(payload)} 字节（与原始一致）")

    if not args.apply:
        print("\n当前是检测模式，未修改任何文件。加 --apply 才会写入。")
        return 0

    if not backup.exists():
        shutil.copy2(exe, backup)
        print(f"已备份原文件 -> {backup}")
    else:
        print(f"备份已存在，保持不变：{backup}")

    before_hash = region_hash(data, prefix_start, region_end)
    patched = bytearray(data)
    patched[prefix_start:region_end] = new_blob
    after_hash = region_hash(bytes(patched), prefix_start, region_end)
    if before_hash != after_hash:
        print("内部校验失败：补丁影响了目标区间之外的字节，已放弃。")
        return 5
    if len(patched) != len(data):
        print("内部校验失败：文件长度发生变化，已放弃。")
        return 5

    exe.write_bytes(bytes(patched))

    verify = find_blob(exe.read_bytes())
    ok = bool(verify) and "网络设备".encode() in verify[3]
    print(f"写入完成，回读校验：{'成功' if ok else '失败'}")
    if not ok:
        print("校验失败，正在还原备份…")
        shutil.copy2(backup, exe)
        return 5

    print("\n完成！启动 Packet Tracer，设备箱里应显示中文。")
    print("如需还原英文：python patch_device_box.py --restore")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
