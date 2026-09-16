# 版权与第三方声明

## 本项目

- 脚本与文档：MIT，见 `LICENSE`。
- 译文内容（`tools/tr/part_*.txt`、`dist/Chinese_chi.ts` 中的 `<translation>` 部分、
  `devicebox/DeviceTypesConfig.zh.json` 中的中文取值）：由本项目作者翻译。

## 第三方

- **Cisco Packet Tracer**：`dist/Chinese_chi.ts` 是以 Cisco Packet Tracer 官方安装目录下
  `languages\template.ts` / `default.ts` 为模板制作的翻译工程文件，其中的 `<source>`
  条目、上下文名称、图标与产品名称版权归 **Cisco Systems, Inc.** 所有。
  本项目仅为按 Cisco 官方文档所述流程（Qt Linguist 翻译 -> lrelease 编译 -> 放入
  `languages`）制作的非官方汉化包，与 Cisco 无隶属或合作关系。
- **Qt / Qt Linguist / lrelease**：编译工具与 `.qm`/`.ptl` 文件格式版权归
  The Qt Company 所有（LGPL/GPL 等）。本项目通过调用 Packet Tracer 自带的
  `bin\lrelease.exe` 生成语言包，未重新分发 Qt 组件。
- `devicebox/patch_device_box.py` 不包含、也不分发 Cisco 的原始二进制内容：
  它在你本机的 `PacketTracer.exe` 上就地替换设备箱配置数据，并在替换前自动备份。

## 使用建议

- 请仅在**你本人拥有合法授权**的 Packet Tracer 安装上使用本项目。
- 请勿将本项目用于商业用途，也不要移除本文件与 README 中的声明。
- 如需在本项目基础上发布二次汉化，请保留本声明，并同样标注为非官方版本。
