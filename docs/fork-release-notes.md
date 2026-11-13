# Iride 0.23.2

合入上游的智能对象调整、Camera Raw 性能、画笔与修复工具、矢量路径及形状操作改进，并包含 Affinity/PSD 等导入、批处理，以及 CMYK 色彩配置下合并图层和栅格化的修复。迁移至固定版本 craft-i18n，保留原生菜单汉化，补充新增工具、对话框、提示和批处理复数文案。

保留独立分支的原创色带图标、原生深浅色/系统着色、旧系统 ICNS、透明三色色带共用 Logo、原作者与贡献者记录。应用名称为 Iride，自动更新与源码指向 `frangled123/photocraft`；命令名和文件格式保持兼容。支持 35 种界面语言（含英语）。

采用公开仓库的标准 macOS ARM runner 实际编译，目标为 `aarch64-apple-darwin`。DMG 与 CLI ZIP 使用 ad-hoc 签名，未公证；macOS 可能要求在系统设置中确认“仍要打开”。附件提供 `SHA256SUMS.txt`。发布流程核验所有随附 Mach-O 的单 ARM 架构、严格签名、版本与源码提交、原生图标、许可证和上传后的实际字节。

固定构建输入与逐文件图稿清单见 `packaging/fork/release-inputs.json`。上游历史通过合并保留，具体提交及本次构建运行链接见下方。

测试范围、Linux GUI 抽查及跳过项见仓库的 `docs/fork-validation.md`。
