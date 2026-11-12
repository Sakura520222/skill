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
| 加 blur/glass 后 manifest 合并失败 | AAR minSdk 与应用 minSdk | 区分构件最低版本与运行时能力；选择兼容方案 |
| 模糊出现色块 / 玻璃看不到背景 | 捕获背景是否不透明、是否采样了自身 | 将背景与效果表面分离，检查 modifier 绘制顺序 |
| 导航恢复失败 / 子路由无法序列化 | serialization 配置、路由层级、泛型推断 | 用超类型 `rememberNavBackStack<Route>`，验证实际恢复 |

## 从旧版迁移

先锁定迁移起点和目标 release，只修改目标变更涉及的部分。逐项核查依赖拆分、包路径、`Super*` 等组件命名、弹层 `show` 参数类型、主题 Controller、导航 DSL 与视觉效果模块；这些是核查点，不是跨所有版本统一的一键替换规则。

每完成一个相对独立的迁移，运行受影响模块编译。删除旧依赖之前检查剩余调用者；项目同时需要旧组件或 Material 组件时，保留必要边界。

## 验证层级

源码签名核对能发现错误导入或参数；Gradle 编译能发现目标依赖和 Kotlin 兼容问题；实际运行才能确认弹层宿主、手势、平台窗口和 GPU 效果。交付时分别说明这些验证的完成情况。

Windows 上可用项目的 `gradlew.bat tasks --all` 查看任务，类 Unix 环境用 `./gradlew tasks --all`。按实际模块选择编译任务，不为文档示例额外宣称 Android / iOS / Desktop 全平台通过。
