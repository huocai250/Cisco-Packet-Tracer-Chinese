"""Build the Simplified-Chinese version of the device box config.

Input : work/out/DeviceTypesConfig.json  (extracted from PacketTracer.exe)
Output: work/out/DeviceTypesConfig.zh.json
"""

import json
import sys
from pathlib import Path

WORK = Path(__file__).resolve().parent
SRC = WORK / "out" / "DeviceTypesConfig.json"
DST = WORK / "out" / "DeviceTypesConfig.zh.json"

# 只翻译展示用字段（name / tooltip / accessibleName），逻辑字段（id、deviceTypes、
# isConnection、shortcut 等）保持原样。
ZH = {
    "Network Devices": "网络设备",
    "End Devices": "终端设备",
    "Components": "组件",
    "Connections": "连接",
    "Miscellaneous": "杂项",
    "Multiuser Connection": "多用户",
    "Smart Home": "智能家居",
    "Home": "主页",
    "Smart City": "智慧城市",
    "Industrial": "工业",
    "Industrial - OT": "工业-OT",
    "Power Grid": "电网",
    "Security": "安全",
    "WAN Emulation": "WAN 仿真",
    "Structured Cabling": "布线",
    "Wireless Devices": "无线设备",
    "Routers": "路由器",
    "Switches": "交换机",
    "Hubs": "集线器",
    "Boards": "板卡",
    "Actuators": "执行器",
    "Sensors": "传感器",
    "Coaxial": "同轴",
    "Console": "控制台",
    "Copper Cross-Over": "交叉线",
    "Copper Straight-Through": "直通线",
    "IoT Custom Cable": "IoT 线缆",
    "Multi Mode Fiber": "多模光纤",
    "Single Mode Fiber": "单模光纤",
    "Octal": "八进制",
    "Phone": "电话",
    "Serial DCE": "串行 DCE",
    "Serial DTE": "串行 DTE",
    "USB": "USB",
    "Automatically Choose Connection Type": "自动选择",
}


def translate(value: str) -> str:
    # tooltip 形如 "Routers Ctrl+Alt+R"：翻译名称部分，快捷键原样保留
    for english, chinese in sorted(ZH.items(), key=lambda kv: -len(kv[0])):
        if value == english:
            return chinese
        if value.startswith(english + " "):
            return chinese + value[len(english):]
    return value


def walk(node):
    if isinstance(node, dict):
        return {
            key: (translate(val) if key in ("name", "tooltip", "accessibleName") and isinstance(val, str)
                  else walk(val))
            for key, val in node.items()
        }
    if isinstance(node, list):
        return [walk(item) for item in node]
    return node


def strip_type_shortcut(node: dict) -> None:
    """设备类型按钮的提示里去掉快捷键后缀，为中文译文腾出字节预算
    （exe 里这条资源只有 1919 字节的压缩空间，译文必须压得进去）。"""
    for group in node.get("deviceGroups", []):
        for device_type in group.get("deviceTypes", []):
            tip = device_type.get("tooltip")
            if isinstance(tip, str) and " Ctrl+Alt" in tip:
                device_type["tooltip"] = tip.rsplit(" Ctrl+Alt", 1)[0]


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    data = json.loads(SRC.read_text(encoding="utf-8-sig"))
    translated = walk(data)
    strip_type_shortcut(translated)
    text = json.dumps(translated, ensure_ascii=False, separators=(",", ":"))
    DST.write_text(text, encoding="utf-8")
    print(f"wrote {DST} ({len(text)} bytes)")


if __name__ == "__main__":
    main()
