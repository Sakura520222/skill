# 来源与版本边界

- 核对日期为 2026-11-21，技能版本为 1.2.0。
- 官方仓库：[compose-miuix-ui/miuix](https://github.com/compose-miuix-ui/miuix)。
- 固定参考 [v0.9.5-beta03 的提交 3526cfe2](https://github.com/compose-miuix-ui/miuix/tree/3526cfe2ca0779c5a2eab99af8737a96c9a8a885)。
- 官方 [中文快速开始](https://compose-miuix-ui.github.io/miuix/zh_CN/guide/getting-started)。
- 精确源文件、Git blob SHA 与参考资料映射见 [sources.json](sources.json)。

稳定版为 `0.9.4`。`BuildConfig.kt` 的基础版本字段为 `0.9.5`，发布脚本追加 `-beta03`。已在 Maven Central 核对 UI、Preference、Nav、Glass、Glass Icons、Material 和 Window 的 Beta 坐标，并检查 Glass、Blur 和 Material 的 Android AAR 清单与依赖元数据。 [稳定版](https://github.com/compose-miuix-ui/miuix/releases/tag/v0.9.4) · [Beta02 迁移说明](https://github.com/compose-miuix-ui/miuix/releases/tag/v0.9.5-beta02) · [Beta03 发布](https://github.com/compose-miuix-ui/miuix/releases/tag/v0.9.5-beta03) · [Maven Central](https://central.sonatype.com/artifact/top.yukonga.miuix.kmp/miuix-ui/0.9.5-beta03)

在线文档可能对应其他提交。进行迁移或查找缺失 API 时，通过来源清单打开固定源码，并用实际构件与目标平台的编译结果确认。

设置页示例已使用 Kotlin 2.4.21、Compose Multiplatform 1.13.0-rc01 与 Maven Central 的 `0.9.5-beta03` 构件完成 Desktop JVM 编译。Android、iOS 和实际交互尚未运行。

## 资料更新

在维护仓库中，现有抓取工具支持此技能的 manifest。以下命令将固定源文件下载到新的缓存目录并验证 blob；缓存不分发：

```bash
python scripts/fetch_sources.py --manifest skills/miuix-guidance/references/sources.json --output .cache/miuix-sources-3526cfe2
```

更新快照时用 `--ref` 指定发布标签或分支，并写入新的缓存目录。核对变更、实际发布坐标、Android AAR 和示例后，同步提交、日期与来源清单。安装后的技能可直接按清单访问固定源码。

## 许可

Miuix 原始资料和源码采用 Apache-2.0，原始作者保留权利；许可正文见 [LICENSE-APACHE-2.0.txt](../LICENSE-APACHE-2.0.txt)。本仓库重新整理的技能采用 AGPL-3.0-or-later，见 [LICENSE.txt](../LICENSE.txt) 和 [NOTICE.txt](../NOTICE.txt)。本包不包含上游字体、图标二进制或完整源码快照。
