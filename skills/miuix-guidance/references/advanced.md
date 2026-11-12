# 按需进阶

仅阅读任务涉及的小节。以下描述来自 [固定主分支快照](sources.md)，导航与特效尤其需要检查消费方版本。

## 大标题与滚动

`TopAppBar` 与滚动容器共享一个 `MiuixScrollBehavior()`；将其传给标题栏的 `scrollBehavior`，再把 `scrollBehavior.nestedScrollConnection` 连接到滚动容器的 `Modifier.nestedScroll(...)`。只创建行为而不绑定内容不会产生联动。

使用 `LazyColumn(contentPadding = paddingValues)` 等方式处理 Scaffold 内容边距；根据是否需要滚动内容穿过透明顶栏决定 padding 放在内容还是容器上。不要同时重复应用同一 Insets。若另用官方 `overScrollVertical()`，官方示例要求它位于 nested scroll 绑定之前；同时核对所用版本的默认 overscroll，避免重复效果。

来源：[TopAppBar](https://compose-miuix-ui.github.io/miuix/zh_CN/components/basic/topappbar)。

## 图标

基础 UI 仅附带少量图标。扩展集合添加 `miuix-icons`，同时导入 `top.yukonga.miuix.kmp.icon.MiuixIcons` 和所选图标的扩展属性，例如 `top.yukonga.miuix.kmp.icon.extended.Settings`。仅导入 `MiuixIcons` 不会自动引入所有扩展属性。

当前文档支持 Light / Normal / Regular / Medium / Demibold；不要为只有某一种粗细的基础图标猜出其他变体。Glass 集合来自 `miuix-glass-icons` 和 `icon.glass`，使用 `MiuixIcons.Glass.*`。本次快照普通图标画布为 24 dp、Glass 为 28 dp，实际布局依目标版本核对。交互图标提供有意义的 `contentDescription`，装饰图标可为 null。

来源：[图标系统](https://compose-miuix-ui.github.io/miuix/zh_CN/guide/icons)。

## 导航

使用 Miuix 组件并不要求引入 `miuix-nav`。保留现有 Navigation / Decompose / 自建路由，除非用户需要 Miuix 导航或特定转场能力。

本次快照的 `miuix-nav` 是独立导航运行时，不是 `androidx.navigation3` 包的别名。选择它时：

- 路由实现 `top.yukonga.miuix.kmp.nav.core.NavKey`，使用可序列化的路由层级；按项目方式启用 Kotlin serialization 插件与依赖。
- 显式指定超类型，如 `rememberNavBackStack<Route>(Route.Home)`；只用具体 Home 类型推断可能导致整个路由层级的序列化不正确。
- 使用同包的 `NavDisplay` 和其 `entry<RouteType>` DSL。不要混入另一导航库的同名类型。
- 返回动作明确处理根路由策略；UI 自定义返回按钮不应随意弹空根栈。验证配置变更、恢复、重复 push/pop、返回取消和确认。
- 本次快照页面内 swipe dismiss 默认为关闭，预设转场也不自动开启。需要时按路由配置 `NavSwipeDirection`；它表示物理屏幕方向，不自动随 RTL 镜像。系统返回与页面内滑动是不同输入来源，分别验证。

复杂转场、导航栏状态同步、生命周期 / ViewModel 作用域等按目标版本查官方导航页及 `miuix-nav` 源码，不复制旧版 Navigation3 集成教程。

来源：[导航支持](https://compose-miuix-ui.github.io/miuix/zh_CN/guide/miuix-nav)。

## 模糊与玻璃

本次快照 `miuix-blur` / `miuix-glass` 的 Android 构件最低 API 为 33。`if (SDK_INT >= 33)` 不会解决更低 minSdk 应用的 manifest 合并问题。若项目必须继续支持更低版本，选择兼容版本 / 不含该依赖的方案，或讨论功能与最低版本要求，不使用 manifest override 假装兼容。

正确采样关系：

1. 用 `rememberLayerBackdrop()` 创建背景记录对象。
2. 在真正的背景内容上用 `Modifier.layerBackdrop(backdrop)` 捕获绘制。
3. 在独立叠加表面上用 `textureBlur` 或 `glassPanel` 消费同一个 backdrop。

采样仅包含所在 composable 自身的绘制，不自动包含父级背景。背景区域应包含不透明底色，排除玻璃表面及其遮罩，防止透明色块与自采样。先验证普通不透明表面布局，再定位采样或 GPU 问题。

本次快照 `GlassStyle`、`GlassMaterial`、`GlassShape` 等定义在 `top.yukonga.miuix.kmp.material`；不要按旧 `miuix-shader` 名称生成新代码。`glassPanel(backdrop = null)` 的默认 fallback 只裁剪，不自动填充背景，需要时显式提供可读的回退表面。

大面积渐进模糊和多重离屏层有 GPU 成本，按实际滚动帧表现调整面积和层数。不要把不同效果的半径单位混用；查具体参数的 `Dp` / 像素类型。

来源：[模糊](https://compose-miuix-ui.github.io/miuix/zh_CN/guide/blur)、[玻璃](https://compose-miuix-ui.github.io/miuix/zh_CN/guide/glass)、[材质](https://compose-miuix-ui.github.io/miuix/zh_CN/guide/material)。

## 连续圆角

`squircleBackground` 只填充，`squircleClip` 只裁剪，`squircleSurface` 组合填充与裁剪。按需要选择，不为同一表面叠加不必要的离屏裁剪层。

本次快照基于 shader 的圆角 modifier 在低于 Android API 33 时自动回退普通圆角；这与 blur / glass 模块自身的最低 API 33 是两回事。Path API 与 shader API 的能力也不同，具体版本中查对应实现。RTL 逻辑圆角使用 start/end；需要固定物理角时查 `absoluteSquircle*`。

来源：[平滑圆角](https://compose-miuix-ui.github.io/miuix/zh_CN/guide/squircle)。
