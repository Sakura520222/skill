# 主题、设置页与弹层

下列设置页已在独立 Desktop JVM 工程中使用 `0.9.5-beta01` 的发布构件编译通过。Android、iOS 和实际交互效果仍需在消费项目中验证。示例使用 `miuix-ui`、`miuix-preference` 和 Compose runtime / foundation。 [版本与来源](sources.md)

## 一个可交互的设置页

设置值由外部传入，方便连接现有 ViewModel / 持久化层。仅把临时弹窗状态保存在页面中。

```kotlin
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.consumeWindowInsets
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import top.yukonga.miuix.kmp.basic.Scaffold
import top.yukonga.miuix.kmp.basic.SmallTopAppBar
import top.yukonga.miuix.kmp.basic.Text
import top.yukonga.miuix.kmp.basic.TextButton
import top.yukonga.miuix.kmp.overlay.OverlayDialog
import top.yukonga.miuix.kmp.preference.SwitchPreference
import top.yukonga.miuix.kmp.theme.ColorSchemeMode
import top.yukonga.miuix.kmp.theme.MiuixTheme
import top.yukonga.miuix.kmp.theme.ThemeController

@Composable
fun SettingsPage(
    notificationsEnabled: Boolean,
    onNotificationsChange: (Boolean) -> Unit,
    mode: ColorSchemeMode = ColorSchemeMode.System,
) {
    val controller = remember(mode) { ThemeController(mode) }
    var aboutVisible by rememberSaveable { mutableStateOf(false) }

    MiuixTheme(controller = controller) {
        Scaffold(topBar = { SmallTopAppBar(title = "设置") }) { padding ->
            Column(Modifier.fillMaxSize().padding(padding).consumeWindowInsets(padding)) {
                SwitchPreference(
                    title = "消息通知",
                    summary = "允许应用显示消息提醒",
                    checked = notificationsEnabled,
                    onCheckedChange = onNotificationsChange,
                )
                TextButton(text = "关于", onClick = { aboutVisible = true })
            }
            OverlayDialog(
                show = aboutVisible,
                title = "关于应用",
                onDismissRequest = { aboutVisible = false },
            ) {
                Text("使用 Miuix 构建的设置界面")
                TextButton(text = "关闭", onClick = { aboutVisible = false })
            }
        }
    }
}
```

已有应用级 `MiuixTheme` 时，通常复用它，把页面内容提取为主题内部的 Composable，不逐页新建主题控制器。系统通知权限仍由业务逻辑处理，这个开关只示范状态回调。

## 主题选择与更新

- `ColorSchemeMode.System` 跟随系统；`Light` / `Dark` 固定明暗；`MonetSystem` / `MonetLight` / `MonetDark` 启用动态配色。
- Monet 的 `keyColor` 可指定种子颜色；为空时走平台动态颜色实现。不要向非 Android 平台承诺 Android 壁纸取色行为。
- 当前源码中 `ThemeController` 的配置属性是只读 `val`。用户切换模式或种子色时，用 `remember(mode, keyColor, ...) { ThemeController(...) }` 包含相关输入；不要写 `controller.colorSchemeMode = ...`，也不要无 key 地 remember 后期待输入自动刷新。
- 使用 `MiuixTheme.colorScheme` 和 `MiuixTheme.textStyles`。自定义配色可由 `ThemeController(lightColors = ..., darkColors = ...)` 提供，或使用 `MiuixTheme(colors = ...)` 重载；直接 colors 重载的 `colorSchemeMode` 为 null。
- Material 3 的 `MaterialTheme.colorScheme` 与 Miuix 的 `Colors` 不是可互换类型。逐项选择实际存在的颜色角色，不套用另一库的 token 名称。

## 组件选择

| 场景 | 起点 | 注意 |
| --- | --- | --- |
| 文本、按钮、卡片、输入框 | `basic.Text` / `TextButton` / `Card` / `TextField` | 不照搬 Material 的参数；例如 Miuix `TextButton` 可直接传 `text` |
| 设置页开关 | `preference.SwitchPreference` | `checked` 与 `onCheckedChange` 由调用方传入 |
| 设置页导航 / 单选 / 滑块 | `ArrowPreference` / `RadioButtonPreference` / `SliderPreference` | 在目标版本文档中确认参数与包 |
| 大标题 / 固定小标题 | `TopAppBar` / `SmallTopAppBar` | 只有需要折叠联动时接 scroll behavior |
| 页面内弹窗 | `overlay.OverlayDialog` | 需要 Miuix Scaffold 的弹层宿主 |
| 窗口级弹窗 | `window.WindowDialog` | 无需 Scaffold；它不等同于 Desktop 专用 `miuix-window` 模块 |

## 弹层生命周期

- `OverlayDialog(show = ...)` 的 `show` 在当前快照是 `Boolean`，不是 `MutableState<Boolean>`。从旧版本迁移时核对签名。
- 保持弹层 Composable 存在，用 `show` 驱动显隐，避免外层 `if (show)` 提前移除它而截断关闭动画。
- 在 `onDismissRequest` 中更新状态；只在确实需要关闭动画结束后执行工作时使用 `onDismissFinished`，该回调在关闭取消时不会执行。
- 嵌套或并列的 Miuix Scaffold 各自管理弹层状态。`renderInRootScaffold` 决定相关 Overlay 是否在最外层展示；局部覆盖需求应核对该选项，避免随意新建全局 host。
- `WindowDialog` 基于平台窗口显示，检查目标平台、焦点、输入法和返回行为，不能仅因省掉 Scaffold 就无条件替换所有 Overlay。

来源：[主题](https://compose-miuix-ui.github.io/miuix/zh_CN/guide/theme)、[Scaffold](https://compose-miuix-ui.github.io/miuix/zh_CN/components/basic/scaffold)、[SwitchPreference](https://compose-miuix-ui.github.io/miuix/zh_CN/components/extended/switchpreference)、[OverlayDialog](https://compose-miuix-ui.github.io/miuix/zh_CN/components/basic/overlaydialog)、[WindowDialog](https://compose-miuix-ui.github.io/miuix/zh_CN/components/basic/windowdialog)。
