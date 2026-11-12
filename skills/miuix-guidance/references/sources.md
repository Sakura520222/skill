# 来源与版本边界

- 整理日期：2026-11-12；技能版本：1.0.0。
- 官方仓库：[compose-miuix-ui/miuix](https://github.com/compose-miuix-ui/miuix)。
- 固定参考：[96d613aa42c485463c596886a2433a61c1bd7d6f](https://github.com/compose-miuix-ui/miuix/tree/96d613aa42c485463c596886a2433a61c1bd7d6f)。
- 用户提供的入口：[中文快速开始](https://compose-miuix-ui.github.io/miuix/zh_CN/guide/getting-started)。
- 精确源文件、Git blob SHA 与参考资料映射见 [sources.json](sources.json)。

本技能是重新组织的使用指导，不是官方完整手册。基础 API 示例按固定源码核对，未建立独立 Kotlin 工程进行编译或设备测试。上游 `BuildConfig.kt` 的 `LIBRARY_VERSION = "0.9.4"` 仅记录快照中的字段，不代表所有快照功能都已发布到该版本。

本次读取发现在线文档与主分支存在差异：线上快速开始仍列出 `miuix-shader`，而固定主分支已包含 `miuix-material`、glass 相关模块和 Desktop window；Wasm 坐标后缀也有不同写法。因此消费方版本的源码与 Maven 发布物优先于不带版本的文档站。

## 资料更新

在维护仓库中，现有抓取工具支持此技能的 manifest。以下命令将固定源文件下载到新的缓存目录并验证 blob；缓存不分发：

```bash
python scripts/fetch_sources.py --manifest skills/miuix-guidance/references/sources.json --output .cache/miuix-sources-96d613a
```

更新快照时可追加 `--ref main`，但先使用新的输出目录，检查变更并重新核对指导与示例，再更新技能中的提交、日期与 manifest。不要只刷新哈希而保留旧指导。安装后的技能可直接按 manifest 的固定 URL 查阅来源，无需维护仓库脚本。

## 许可

Miuix 原始资料和源码采用 Apache-2.0，原始作者保留权利；许可正文见 [LICENSE-APACHE-2.0.txt](../LICENSE-APACHE-2.0.txt)。本仓库重新整理的技能采用 AGPL-3.0-or-later，见 [LICENSE.txt](../LICENSE.txt) 和 [NOTICE.txt](../NOTICE.txt)。本包不包含上游字体、图标二进制或完整源码快照。
