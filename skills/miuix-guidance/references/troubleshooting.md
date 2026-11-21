# 排障与迁移

先记录实际解析版本、平台、复现步骤和首个相关错误，再按下表定位。事实依据见 [sources.md](sources.md)；排查顺序是本技能的实践建议。

| 现象 | 优先核查 | 处理方向 |
| --- | --- | --- |
| 找不到构件 / 无匹配变体 | 坐标、已发布版本、source set 与目标平台 | KMP 共享代码用多平台坐标；单平台后缀核对 Maven；桌面 window 不放 commonMain |
| Kotlin 元数据或 Compose 编译错误 | 实际解析版本及项目插件兼容性 | 查看依赖报告和对应 release 要求，避免复制主分支整套工具链 |
| `SwitchPreference` 无法解析 | 是否有 preference 模块与正确 import | 查 `top.yukonga.miuix.kmp.preference`；不要只加 ui 或盲改成旧 `Super*` |
| `TextButton` / `Scaffold` 参数不匹配 | import 是否误指向 Material；文档版本 | 显式 import / 别名，再核对该版本真实函数签名 |
| Overlay 状态为 true 却不显示 | 是否处于 Miuix Scaffold 下；默认 popupHost 是否被替换 | 修复宿主层级；Material Scaffold 不提供 MiuixPopupHost |
| 弹窗瞬间消失、关闭回调异常 | 外部 if 是否提前移除；show 与 dismiss 更新 | 保留 Composable，让 show 驱动；区分请求关闭与动画结束 |
| 顶栏不折叠 / 内容被栏遮挡 | 共享 scroll behavior、nestedScroll、padding | 将同一行为接到列表；只应用一次需要的 Insets |
| 切换主题后无变化 | ThemeController 的 remember keys；实际读取哪套主题 | 重建带新输入的 controller；核对 Miuix / Material 主题边界 |
| 扩展图标无法解析 | 图标模块、扩展属性 import、版本中的图标名称 | 查该版本图标定义，不靠名称自动补全猜测 |
| 加 Blur 或 Glass 后 manifest 合并失败 | Android AAR 与传递依赖的 minSdk | Beta 的 Glass 自身是 24，传递 Blur 是 33。按 [接入指南](setup.md) 选择 Android 回退方案 |
| 从旧快照升级后 Glass 顶栏参数失效 | `titleBlurRadius`、滚动行为及越界 API | 核对 [顶栏联动](advanced.md) 的新参数及位移来源 |
| 模糊出现色块 / 玻璃看不到背景 | 捕获背景是否不透明、是否采样了自身 | 将背景与效果表面分离，检查 modifier 绘制顺序 |
| 导航恢复失败 / 子路由无法序列化 | serialization 配置、路由层级、泛型推断 | 用超类型 `rememberNavBackStack<Route>`，验证实际恢复 |

## 从旧版迁移

先锁定迁移起点和目标 release，只修改目标变更涉及的部分。逐项核查依赖拆分、包路径、`Super*` 等组件命名、弹层 `show` 参数类型、主题 Controller、导航 DSL 与视觉效果模块；这些是核查点，不是跨所有版本统一的一键替换规则。

从 `0.9.4` 迁到 `0.9.5` 系列 Beta 时，使用 `miuix-shader` 的项目应核查 `miuix-material` 及包名变更。iOS 在移动内容和 Scaffold 嵌套时出现 Insets 崩溃，可对照 Beta 中 [Scaffold 的修复](https://github.com/compose-miuix-ui/miuix/commit/95948685)，并用目标导航路径复现验证。

从 `beta01` 升到 `beta02` 或 `beta03` 时，检查以下调用点。 [beta02 迁移说明](https://github.com/compose-miuix-ui/miuix/releases/tag/v0.9.5-beta02)

- Compose Multiplatform 依赖对齐 `1.13.0-rc01` 系列，再重新编译。
- 自定义滚动条从按状态类型区分的旧适配器迁移到统一的 `rememberScrollBarAdapter`，或使用 [滚动条修饰符](advanced.md#大标题与滚动)。旧的 `LazyLineContentAdapter` 和拖拽辅助方法已移除。
- Desktop 的 `MiuixWindowProperties` 移除了窗口类型参数。将 `onVisibleChange` 和 `onResizeEdgeChange` 传给 `MiuixWindow` 或 `MiuixDialogWindow`，属性对象继续存放窗口配置。

每完成一个相对独立的迁移，运行受影响模块编译。删除旧依赖之前检查剩余调用者；项目同时需要旧组件或 Material 组件时，保留必要边界。

## 验证层级

源码签名核对能发现错误导入或参数；Gradle 编译能发现目标依赖和 Kotlin 兼容问题；实际运行才能确认弹层宿主、手势、平台窗口和 GPU 效果。交付时分别说明这些验证的完成情况。

Windows 上可用项目的 `gradlew.bat tasks --all` 查看任务，类 Unix 环境用 `./gradlew tasks --all`。按实际模块选择编译任务，不为文档示例额外宣称 Android / iOS / Desktop 全平台通过。
