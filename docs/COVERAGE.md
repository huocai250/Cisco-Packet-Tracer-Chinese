# 翻译覆盖率与未翻译内容

## 统计口径

以官方安装目录下的 `languages\default.ts` 为基准（Packet Tracer 9.0.1）：

| 指标 | 数量 |
| --- | --- |
| 模板中的界面文本条目（含重复出现的同一个字符串） | 10603 |
| 去重后的独立字符串 | 7048 |
| 已翻译并编译进语言包的条目 | **9154**（约 86.3%） |
| 已翻译的独立字符串 | **6613** |
| 仍未翻译的独立字符串 | 717 |

未翻译的部分不会是“漏翻”：它们都是刻意保留英文的内容（见下节）。
可以用 `python tools/remaining.py` 随时查看当前剩余清单。

## 刻意保留英文的内容

1. **协议与技术缩写**：IP、ACL、ARP、OSPF、EIGRP、BGP、NAT、VLAN、DHCP、WPA2、TKIP、TKIP…；
   MIB 数据类型（`Counter32`、`Counter64`、`Integer32`、`OctetString`、`TimeTicks`、`TruthValue`）；
   分层名称（`Layer1`–`Layer7`）、`IP MTU`、`TCP MSS` 等。
2. **IOS 命令与终端输出**：CLI 里出现的 `permit` / `deny` / `show` / `Router#` 提示符等。
   这些字符串会出现在设备的命令行窗口中，翻译会与真实 IOS 不一致。
3. **产品名、型号、字体、报文类型**：`Packet Tracer`、`Cisco IP Communicator`、`Meraki`、
   `GigabitEthernet0/0`、`Arial`、`Verdana`、`Courier New`、`.rtf` 等。
4. **程序内部标识**：`MainWindow`、`CBaseSimulationToolbar`、`textLabel1`、
   `IO_RULES_PLACEHOLDER`、`TRDB-NO-TEXT` 等，仅在调试或日志中出现。
5. **纯符号 / 编号 / 示例数据**：`MAC 01:`–`MAC 50:`、`5G(1)`、`802.1Q`、信道频率表、
   示例电话号码等。
6. **拼句片段与状态关键字**：`The `、` of `、`by ` 以及接口状态 `up` / `down`
   —— 它们由程序动态拼接或作为状态值使用，单独翻译会得到病句或与 IOS 显示不符。

## 尚未覆盖的区域

| 区域 | 说明 |
| --- | --- |
| `help\default\` 下的 HTML 帮助与教程 | 与语言包是两套文件，本次未翻译（Cisco 官方翻译流程中属于 Part 2）。 |
| 设备箱（Network Devices 分类名与提示） | 不走语言文件，见 [`../devicebox/`](../devicebox) 提供的补丁。 |
| 脚本模块自带的 HTML 界面 | 内置脚本模块是加密包，其界面文字不在 `default.ts` 中，无法通过语言包覆盖。 |
| `.pkt` / `.pka` 文件内部文字 | 设备名、活动说明等写在存档文件里，需要在 Packet Tracer 中单独编辑。 |

## 质量检查

`tools/validate.py` 会逐条比对原文与译文的占位符和 HTML 标签：

```
messages=10603 translated=9149 placeholder-mismatch=0 tag-mismatch=0
```

（`<not set>` → `<未设置>` 这类“看起来像标签”的字符串会被单独列出，属正常情况。）
