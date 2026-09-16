# 构建与继续翻译指南

## 环境要求

- Windows 上的 Cisco Packet Tracer 9.0.1（提供 `bin\lrelease.exe` 与 `languages\default.ts`）
- Python 3.9+（脚本只用到标准库）
- 可选：`bin\linguist.exe`（Qt Linguist，用于图形化校对）

以下命令默认假定 Packet Tracer 装在
`D:\Program Files\Cisco Packet Tracer 9.0.1`，其他路径请用对应的参数覆盖。

## 一、重建语言包

```powershell
# 1) 从官方模板抽取待翻译字符串，生成分片与 manifest.json
python tools\build_chunks.py --ts "D:\Program Files\Cisco Packet Tracer 9.0.1\languages\default.ts"

# 2) 合并 tools\tr\part_*.txt 里的译文，生成 .ts 并用自带 lrelease 编译成 .ptl
python tools\apply.py `
  --ts       "D:\Program Files\Cisco Packet Tracer 9.0.1\languages\default.ts" `
  --lrelease "D:\Program Files\Cisco Packet Tracer 9.0.1\bin\lrelease.exe"

# 3) 校验占位符（%1/%n/[[VAR]]）与 HTML 标签是否与原文一致
python tools\validate.py

# 4) 查看还有哪些字符串没翻
python tools\remaining.py
```

产物写在 `tools/out/`：

| 文件 | 说明 |
| --- | --- |
| `chinese_chi.ts` | 合并后的翻译工程（含全部上下文与已完成译文） |
| `chinese_chi.ptl` | `lrelease` 编译出的语言包，改名 `Chinese_chi.ptl` 后放入 `languages\` |

发布时把这两个文件复制到 `dist/`（重命名为 `Chinese_chi.ts` / `Chinese_chi.ptl`）。

## 二、译文数据格式

`tools/tr/part_XXX.txt`，每行一条，`编号 <TAB> 中文`：

```
219	端口
969	下一\n跳
1641	IP{BS}n地址
```

- `编号` 来自 `tools/manifest.json`（由 `build_chunks.py` 从官方模板生成，
  按字符串长度排序，编号越小越短）。
- `\n` 表示换行，`\t` 表示制表符，`{BS}` 表示一个反斜杠。
- 文件按编号递增、可以随意拆分或新增分片，`apply.py` 会自动合并。
- 没有出现在 part 文件里的字符串保持英文（回落到原文），所以可以随时增量补充。

## 三、上下文相关的词

同一个英文词在不同界面可能需要不同译法（例如 `Fire`：PDU 列表是「发射」，
环境面板是「火焰」）。这类情况写在 `tools/tr_ctx.json`：

```json
{
  "CPDUListWindow": { "Fire": "发射" },
  "CUserCreatedPDU": { "Fire": "发射" }
}
```

键是 `.ts` 里的 `<context>` 名称（也就是 C++ 类名或 `QObject`），
值是该上下文下的「原文 -> 译文」，优先级高于 `tr/part_*.txt` 的全局译法。

## 四、设备箱（Device Box）中文补丁

设备箱的文字不在语言文件里，而在 exe 内置资源 `:/Resources/DeviceTypesConfig.json`。
相关脚本：

```powershell
# 从本机 exe 中抽取原始 JSON（写入 tools\out\，版权属 Cisco，请勿提交到公开仓库）
python tools\dump_resources.py --exe "D:\Program Files\Cisco Packet Tracer 9.0.1\bin\PacketTracer.exe"

# 依据脚本内置术语表生成中文版 JSON（写入 tools\out\DeviceTypesConfig.zh.json）
python tools\make_devicebox_json.py

# 检查 / 打补丁 / 还原
python devicebox\patch_device_box.py --check
python devicebox\patch_device_box.py --apply
python devicebox\patch_device_box.py --restore
```

要点：

- 该资源在 exe 中只占 **1919** 字节压缩空间，所以中文 JSON 必须压缩到同样大小：
  `make_devicebox_json.py` 会把设备类型工具提示里的快捷键后缀去掉、并精简若干译名来腾出空间，
  `patch_device_box.py` 再通过补空格把压缩结果**精确压到 1919 字节**，从而做到原地替换、
  不改变 exe 长度与其它资源偏移。
- 如果目标版本的资源布局不同，补丁脚本会提示“没有找到 DeviceTypesConfig.json 资源”并放弃写入。
- 改了译名之后要重新跑一次 `make_devicebox_json.py`，并确认压缩后仍能塞进 1919 字节。

## 五、提交 PR 的建议

1. 只改 `tools/tr/part_*.txt`（或 `tools/tr_ctx.json`），不要手工改 `dist/*.ts`；
2. 运行 `apply.py` + `validate.py`，确认输出是 `placeholder-mismatch=0`；
3. 把重新生成的 `dist/Chinese_chi.ts`、`dist/Chinese_chi.ptl` 一起提交；
4. PR 描述里贴出改动前后的界面位置（截图最好），方便核对。
