# 按需进阶

以下描述来自 [固定发布快照](sources.md)，按任务选择相关小节并核对项目版本。

## 大标题与滚动

`TopAppBar` 与滚动容器共享一个 `MiuixScrollBehavior()`；将其传给标题栏的 `scrollBehavior`，再把 `scrollBehavior.nestedScrollConnection` 连接到滚动容器的 `Modifier.nestedScroll(...)`。只创建行为而不绑定内容不会产生联动。

使用 `LazyColumn(contentPadding = paddingValues)` 等方式处理 Scaffold 内容边距；根据是否需要滚动内容穿过透明顶栏决定 padding 放在内容还是容器上。不要同时重复应用同一 Insets。若另用官方 `overScrollVertical()`，官方示例要求它位于 nested scroll 绑定之前；同时核对所用版本的默认 overscroll，避免重复效果。

在 `0.9.5-beta03` 中，列表可向 `GlassTopAppBar` 传 `isContentScrolled = listState.canScrollBackward` 和共享的 `scrollBehavior`。负向越界也会触发玻璃材质与背景。需要显式越界联动时，将 `overScrollVertical(onOffsetChanged = ...)` 放在 `nestedScroll` 之前，由回调写入 `scrollBehavior.state.overscrollOffset`，`contentOffset` 记录实际滚动。列表已绑定该行为时，外层 `PullToRefresh` 无需再绑定。

迁移较早的 Glass 示例时，将 `largeTitleBlurRadius` 改为 `titleBlurRadius`。当前 `GlassTopAppBar` 通过滚动行为和 `isContentScrolled` 获取滚动状态，`visualContentOffset` 仍可用于 `GlassTopAppBarDefaults.collapseRamp`。

来源：[TopAppBar](https://compose-miuix-ui.github.io/miuix/zh_CN/components/basic/topappbar)、[Beta GlassTopAppBar](https://github.com/compose-miuix-ui/miuix/blob/3526cfe2ca0779c5a2eab99af8737a96c9a8a885/docs/zh_CN/components/glass/glasstopappbar.md)、[Beta 越界回弹](https://github.com/compose-miuix-ui/miuix/blob/3526cfe2ca0779c5a2eab99af8737a96c9a8a885/docs/zh_CN/guide/utils.md)。

`0.9.5-beta02` 起可给滚动容器加 `Modifier.verticalScrollBar(state = listState, topAppBarScrollBehavior = scrollBehavior)`，确保拖动滚动条时也联动顶栏。横向容器用 `Modifier.horizontalScrollBar(state = ...)`。迁移旧适配器时，使用接受 `ScrollableState` 的 `rememberScrollBarAdapter`。 [滚动条源码](https://github.com/compose-miuix-ui/miuix/blob/3526cfe2ca0779c5a2eab99af8737a96c9a8a885/miuix-ui/src/commonMain/kotlin/top/yukonga/miuix/kmp/basic/ScrollBar.kt)

## 图标

基础 UI 仅附带少量图标。扩展集合添加 `miuix-icons`，同时导入 `top.yukonga.miuix.kmp.icon.MiuixIcons` 和所选图标的扩展属性，例如 `top.yukonga.miuix.kmp.icon.extended.Settings`。仅导入 `MiuixIcons` 不会自动引入所有扩展属性。

当前文档列出 Light / Normal / Regular / Medium / Demibold，实际可用字重按对应图标表核对。Beta 的 Glass 集合来自 `miuix-glass-icons`，例如额外导入 `top.yukonga.miuix.kmp.icon.glass.Search` 后使用 `MiuixIcons.Glass.Search`。本次文档示例普通图标为 24 dp、Glass 为 28 dp。交互图标提供有意义的 `contentDescription`，装饰图标可为 null。

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

Android 实际玻璃和纹理模糊需要 API 33。Beta 的 Glass 支持低版本纯色回退，但传递依赖 Blur 仍触发 API 33 的清单合并检查。使用低版本回退前按 [接入指南](setup.md) 处理构件约束。

正确采样关系：

1. 用 `rememberLayerBackdrop()` 创建背景记录对象。
2. 在真正的背景内容上用 `Modifier.layerBackdrop(backdrop)` 捕获绘制。
3. 在独立叠加表面上用 `textureBlur` 或 `glassPanel` 消费同一个 backdrop。

采样仅包含所在 composable 自身的绘制，不自动包含父级背景。背景区域应包含不透明底色，排除玻璃表面及其遮罩，防止透明色块与自采样。先验证普通不透明表面布局，再定位采样或 GPU 问题。

Beta 将 `GlassStyle`、`GlassMaterial`、`GlassShape` 等定义放在 `top.yukonga.miuix.kmp.material`。`Modifier.glassPanel` 在 `fallback = null` 时只裁剪回退表面。需要纯色时显式传入填充；为 Overlay 的 `surface` 插槽提供玻璃表面时，可用 `glassSurface(backdrop, visuals)`，它从 `visuals.containerColor` 取回退色。

宽屏玻璃侧栏可用 `GlassNavigationRail`。父容器已处理安全区时，传 `defaultWindowInsetsPadding = false`。展开动画中可在布局阶段读取 `railState.progress` 给内容让出空间，同时保持采样背景铺满。工具栏和主操作分别见 `GlassFloatingToolbar` 与 `GlassFloatingActionButton`。这些组件属于 `top.yukonga.miuix.kmp.glass`。

`0.9.5-beta02` 起，玻璃弹层的输入框可使用 `GlassTextField`，支持 `TextFieldState` 和受控值重载。全屏搜索可用同属 `miuix-glass` 的 `GlassSearchOverlay`，在需要关闭模糊时传 `blurEnabled = false`。 [输入框](https://github.com/compose-miuix-ui/miuix/blob/3526cfe2ca0779c5a2eab99af8737a96c9a8a885/docs/zh_CN/components/glass/glasstextfield.md) · [搜索浮层](https://github.com/compose-miuix-ui/miuix/blob/3526cfe2ca0779c5a2eab99af8737a96c9a8a885/docs/zh_CN/components/glass/glasssearchoverlay.md)

按实际滚动表现调整渐进模糊面积和层数。Beta 的 `BlurDefaults.MaxBlurRadius` 是 `100f`（dp）。各接口参数仍要区分 `Dp` 与像素。

来源：[Beta 模糊、玻璃与材质指南](https://github.com/compose-miuix-ui/miuix/tree/3526cfe2ca0779c5a2eab99af8737a96c9a8a885/docs/zh_CN/guide)、[Beta Glass 组件](https://github.com/compose-miuix-ui/miuix/tree/3526cfe2ca0779c5a2eab99af8737a96c9a8a885/docs/zh_CN/components/glass)。

## 连续圆角

`squircleBackground` 只填充，`squircleClip` 只裁剪，`squircleSurface` 组合填充与裁剪。按需要选择，不为同一表面叠加不必要的离屏裁剪层。

本次快照基于 shader 的圆角 modifier 在低于 Android API 33 时自动回退普通圆角；这与 blur / glass 模块自身的最低 API 33 是两回事。Path API 与 shader API 的能力也不同，具体版本中查对应实现。RTL 逻辑圆角使用 start/end；需要固定物理角时查 `absoluteSquircle*`。

来源：[平滑圆角](https://compose-miuix-ui.github.io/miuix/zh_CN/guide/squircle)。
