# Cisco Packet Tracer 简体中文汉化包（非官方）

适用于 **Cisco Packet Tracer 9.0.1** 的简体中文语言包，另附一个可选的设备箱（Device Box）中文补丁。

- 语言包编译产物：`dist/Chinese_chi.ptl`（复制进 `languages\` 即生效）
- 翻译工程源文件：`dist/Chinese_chi.ts`（可用 Qt Linguist 继续修改）
- 覆盖率：官方模板 **10603** 条界面文本，已翻译 **9154** 条（约 **86.3%**）
- 未翻译的 14% 都是刻意保留的：协议缩写、IOS 命令与终端输出、型号/字体/内部标识、纯符号

> 本项目与 Cisco Systems, Inc. 无任何关联，仅为学习与个人使用目的的非官方汉化。

## 特性

- 覆盖主菜单、工具栏、首选项、各设备配置窗口（Config / CLI / 桌面 / 服务等选项卡）、活动向导（Activity Wizard）、模拟模式与逐层 PDU 解释、无线与工业 IoT 界面、登录与证书提示、各类错误对话框。
- 保留快捷键：菜单项写作 `文件(&F)`，`&` 加速键与原文一一对应。
- 变量占位符（`%1`、`%2`、`%n`、`[[VAR]]`）与 HTML 富文本标签全部原样保留，已用脚本自动校验（占位符/标签不一致数为 0）。
- 上下文区分：同一个英文词在不同界面按上下文翻译，例如 `Fire` 在 PDU 列表里是「发射」、在环境面板里是「火焰」。
- 术语统一（见 [`docs/GLOSSARY.md`](docs/GLOSSARY.md)）：Router→路由器、Switch→交换机、Config→配置、Preferences→首选项、Wizard→向导、Score→得分 等。

## 安装

1. 找到 Packet Tracer 的 `languages` 目录，默认是：
   `D:\Program Files\Cisco Packet Tracer 9.0.1\languages\`
2. 把 `dist\Chinese_chi.ptl`（可选再加 `dist\Chinese_chi.ts`）复制进去，需要管理员权限。
3. 完全退出并重启 Packet Tracer。
4. `Options → Preferences → Interface → Language` 选择 **Chinese**，确定后**再重启一次**（PT 提示“下次启动生效”）。

也可以用仓库里的脚本（会请求管理员权限）：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install.ps1
```

macOS / Linux：

```bash
sudo bash scripts/install.sh "/path/to/Packet Tracer 9.0.1/languages"
```

### 卸载

删除 `languages\Chinese_chi.ptl`，或在首选项里把语言改回英文即可。原版文件（`default.ptl` / `default.ts` / `template.ts`）不会被修改。

## 目录结构

```
packet-tracer-zh/
├── dist/                    # 编译好的语言包（安装这个）
│   ├── Chinese_chi.ptl
│   └── Chinese_chi.ts
├── devicebox/               # 可选：设备箱中文补丁
│   ├── patch_device_box.py
│   └── DeviceTypesConfig.zh.json
├── scripts/                 # 一键安装脚本
├── tools/                   # 可复现的翻译流水线（见 docs/BUILD.md）
│   ├── build_chunks.py      # 抽取待翻译字符串 -> chunks
│   ├── apply.py             # 合并译文 -> .ts -> 用 lrelease 编译 .ptl
│   ├── validate.py          # 校验占位符/标签一致性
│   ├── tr/part_*.txt        # 真正的译文数据（41 个分片，纯文本，便于 PR）
│   └── ...
└── docs/
    ├── BUILD.md             # 如何重建 / 如何继续翻译
    ├── COVERAGE.md          # 覆盖率与未翻译内容说明
    └── GLOSSARY.md          # 术语表
```

## 可选：设备箱（Network Devices 那一排）中文化

PT 9 的新设备箱不再读取语言文件，而是读 exe 内置资源
`:/Resources/DeviceTypesConfig.json`（zlib 压缩）里的 `name` / `tooltip` / `accessibleName`
字段，所以 `languages\*.ptl` 无法覆盖它 —— 你会看到
`Network Devices Ctrl+Alt+R`、`Routers Ctrl+Alt+S` 之类的英文提示。

`devicebox/patch_device_box.py` 可以把这 53 条界面文字替换成中文：它把中文 JSON
重新压缩到**与原始数据完全相同的 1919 字节**，因此 exe 总长度与其它资源偏移都不变。

```powershell
# 管理员 PowerShell
python .\devicebox\patch_device_box.py --check    # 只检测，不写文件
python .\devicebox\patch_device_box.py --apply    # 自动备份 + 打补丁 + 回读校验
python .\devicebox\patch_device_box.py --restore  # 还原英文
```

说明与风险：

- 该补丁已在 Windows 版 Packet Tracer 9.0.1 上实际应用并生效（设备箱分类与提示均变为中文）。
- 会**破坏 `PacketTracer.exe` 的 Cisco 数字签名**（一般不影响运行，个别安全软件可能提示）。
- 只修改那 1909 字节的设备箱配置，其它字节不变；补丁前自动备份为 `PacketTracer.exe.bak`，校验失败会自动还原。
- 升级或重装 Packet Tracer 后补丁会被覆盖，需要重新执行。
- 不想改 exe 就跳过这一节，其余界面照常是中文。

## 贡献 / 继续完善翻译

译文以纯文本分片的形式存放在 `tools/tr/part_*.txt`（格式：`字符串编号<TAB>译文`，
`\n` 表示换行、`{BS}` 表示反斜杠）。想补翻或修正：

1. 阅读 [`docs/BUILD.md`](docs/BUILD.md) 了解流水线；
2. 修改/新增 `tools/tr/part_0XX.txt`；
3. 运行 `python tools/apply.py` 重新生成 `dist/Chinese_chi.ts` 与 `dist/Chinese_chi.ptl`；
4. 运行 `python tools/validate.py` 确认没有破坏 `%1` 之类的占位符；
5. 提交 PR，说明修改了哪些界面。

也欢迎直接用 Qt Linguist 编辑 `dist/Chinese_chi.ts` 后提交（Packet Tracer 自带
`bin\linguist.exe`）。

## 常见问题

**Q：为什么还有英文？**
剩下的基本都是协议缩写（OSPF、NAT、WPA2…）、IOS 命令和终端输出（`permit`、`show`）、
产品型号与字体名、程序内部标识，以及极少数由程序拼接的句子片段（`The `、` of `）和
接口状态关键字 `up` / `down`。这些翻译反而会出错或违背惯例，详见
[`docs/COVERAGE.md`](docs/COVERAGE.md)。

**Q：语言下拉框里出现了多个中文条目？**
`languages` 目录里每个 `.ptl` 都会成为一个条目，请只保留一个中文 `.ptl`。

**Q：文件名必须是 `Chinese_chi` 吗？**
PT 的官方建议是 `<语言名>_<ISO 639-2 alpha-3>`（例如 `English_eng`、`Chinese_chi`）。
不同版本解析略有差异时，可尝试改名为 `Chinese_zho.ptl`。

**Q：会影响 .pkt / .pka 文件里的内容吗？**
不会。存档里的设备名、说明文字写在文件内部，需要各自在 Packet Tracer 里编辑。

## 免责声明

- 本项目为个人学习用途的**非官方汉化**，与 Cisco Systems, Inc. 无任何关联。
- Packet Tracer、Cisco 及相关名称、界面文本的版权归 Cisco Systems, Inc. 所有。
- 请确保你拥有合法的 Packet Tracer 使用授权后再使用本项目；请勿用于商业用途。
- 使用设备箱补丁会修改 `PacketTracer.exe` 并使其数字签名失效，请自行评估风险，务必保留备份。

*This is an unofficial Simplified-Chinese localization pack for Cisco Packet Tracer.
Packet Tracer and Cisco are trademarks of Cisco Systems, Inc. Use at your own risk.*

## 更新日志

见 [`CHANGELOG.md`](CHANGELOG.md)。
