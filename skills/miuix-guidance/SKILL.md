---
name: miuix-guidance
description: 为 Kotlin Jetpack Compose / Compose Multiplatform 项目接入、使用、迁移和调试 Miuix（compose-miuix-ui/miuix），涵盖主题、设置页、弹层、导航及视觉效果。用于明确使用 Miuix 的界面任务；不用于 MIUI 系统修改、XML View 或普通 Web UI。
license: AGPL-3.0-or-later
metadata:
  version: "1.1.0"
  documentation_snapshot: "2026-11-18"
---

# Miuix 使用指导

依据 Miuix 官方中文文档与源码实现符合目标版本的 Compose 界面。保留项目已有架构、导航和状态管理；仅为用户需要的能力引入模块。

## 先确定版本与平台

- 查看项目的 Gradle 配置、版本目录、Miuix 依赖和使用处，确定 Android-only 或 KMP、目标 source set、最低 Android API、Kotlin / Compose 版本。
- 已有项目以实际解析的 Miuix 版本为准。新项目或明确升级时，再检查官方发布和 Maven Central 中已发布的构件，不把 `main` 的版本字段当成已发布版本。
- 本技能固定参考已发布的 `v0.9.5-beta01`。截至本次核对，稳定版为 `v0.9.4`。Glass、Material 与 Desktop Window 相关示例按 Beta 边界使用。遇到在线站点与项目解析版本有差异时，以实际构件及同版本源码为准。来源见 [sources.md](references/sources.md)。

## 按任务读取

| 当前任务 | 参考资料 |
| --- | --- |
| 首次接入、依赖选择、版本或 source set 问题 | [setup.md](references/setup.md) |
| 主题切换、设置页、组件与弹层 | [ui-patterns.md](references/ui-patterns.md) |
| 大标题滚动、图标、导航、模糊、玻璃与圆角 | [advanced.md](references/advanced.md) 中对应小节 |
| 编译失败、弹窗不显示、主题或平台异常、旧版迁移 | [troubleshooting.md](references/troubleshooting.md) |

不要预先加载全部参考资料。组件参数不确定时，查对应版本的定义与示例，避免从 Material 3 的同名 API 猜测。

## 实现要点

1. 使用 `top.yukonga.miuix.kmp` 下所需的真实包路径。`basic`、`theme`、`overlay`、`window`、`preference` 属于不同包；混用 Material 组件时显式导入或使用别名。
2. 页面在 `MiuixTheme` 中获取颜色与文字样式。Miuix 和 Material 的主题不会自动相互同步，已有混合界面需要明确映射。
3. 需要 `Overlay*` 弹层的内容放在 Miuix `Scaffold` 下，保留其默认 popup host；Material `Scaffold` 不能提供它。`WindowDialog` 等窗口级组件有不同的宿主规则，按具体 API 选择。
4. 内容处理 `Scaffold` 给出的 padding / Insets，避免底栏、键盘、挖孔遮挡或重复补边。大标题滚动需要同一个 scroll behavior 连接标题栏与滚动内容。
5. 开关、输入框、选项索引和弹层显示状态由调用方管理。设置值接入项目持久化层；`remember` / `rememberSaveable` 不是设置存储服务。
6. 添加特效前检查 Android 构件及传递依赖的 `minSdk`。`0.9.5-beta01` 的 Glass 自身为 24，但依赖最低 API 33 的 Blur。低版本兼容方案与运行时回退见 [setup.md](references/setup.md)。

## 验证与交付

- 用项目 Gradle wrapper 查看可用任务，再运行受影响模块及目标平台的编译 / 检查任务；不要假定所有 KMP 项目都具有同名任务。
- 交互改动验证状态更新、禁用状态、弹层打开与关闭、系统返回；导航改动验证返回栈恢复与根页面行为。
- 视觉改动检查浅色 / 深色、长文本 / 大字体、Insets、目标窗口尺寸；特效在相应运行环境检查降级与滚动表现。
- 说明修改的依赖及版本、采用的组件、实际执行的验证。未编译的示例或未运行的平台明确标注，不把源码核对等同于运行验证。

官方入口：[GitHub](https://github.com/compose-miuix-ui/miuix)、[快速开始](https://compose-miuix-ui.github.io/miuix/zh_CN/guide/getting-started)、[组件文档](https://compose-miuix-ui.github.io/miuix/zh_CN/components/)、[Dokka API](https://compose-miuix-ui.github.io/miuix/dokka/index.html)。
