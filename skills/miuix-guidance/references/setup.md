# 接入与版本选择

本页以 `0.9.5-beta03` 发布构件为参考，来源与复核方法见 [sources.md](sources.md)。

## 依赖位置

保留项目已有仓库管理方式，确保依赖解析仓库包含 `mavenCentral()`。通常在 `settings.gradle.kts` 的 `dependencyResolutionManagement.repositories` 配置，不要在禁止项目级仓库的工程中另加项目仓库。

KMP：在使用 UI 的共享 source set 中声明无平台后缀的模块，由 Gradle 选择目标变体。以下 `miuixVersion` 是需要绑定到项目已确认版本的变量，可替换为版本目录别名：

```kotlin
kotlin {
    sourceSets {
        commonMain.dependencies {
            implementation("top.yukonga.miuix.kmp:miuix-ui:$miuixVersion")
            implementation("top.yukonga.miuix.kmp:miuix-preference:$miuixVersion")
        }
    }
}
```

Android-only：官方快速开始使用 Android 构件，放入应用 / 库模块的 `dependencies`：

```kotlin
dependencies {
    implementation("top.yukonga.miuix.kmp:miuix-ui-android:$miuixVersion")
    implementation("top.yukonga.miuix.kmp:miuix-preference-android:$miuixVersion")
}
```

第二项仅在需要 Preference 时添加。相关 Miuix 模块通常采用同一已发布版本。其他单平台坐标从 Maven 发布物确认，例如该 Beta 的 Wasm UI 为 `miuix-ui-wasm-js`。KMP 优先使用无后缀坐标。

## 按需求选择模块

| 需求 | 模块 | 约束 / 传递依赖 |
| --- | --- | --- |
| 主题、基础控件、Scaffold、普通弹层 | `miuix-ui` | 包含 `miuix-core` 和 `miuix-squircle` |
| 设置项、带标题摘要的开关 / 选择器 | `miuix-preference` | 依赖 `miuix-ui`，包名为 `preference` |
| 扩展图标 | `miuix-icons` | 基础 UI 仅含少量核心图标 |
| Glass 图标 | `miuix-glass-icons` | 自 `0.9.5-beta01` 发布，可独立使用 |
| 背景采样与模糊 | `miuix-blur` | Android AAR 最低 API 33 |
| 连续圆角 | `miuix-squircle` | UI 已传递包含；低 API 有相应降级路径 |
| 运行时着色器和材质定义 | `miuix-material` | Beta 中取代 `miuix-shader`。Android AAR 最低 API 24 |
| 玻璃表面与组件 | `miuix-glass` | Beta 的 AAR 自身最低 API 24，传递引入 material、blur、ui |
| Miuix 自有导航 | `miuix-nav` | 可独立使用，不要求替换项目现有导航 |
| 桌面窗口与标题栏 | `miuix-window` | Beta 新模块，仅 Desktop JVM。放在对应桌面 source set |

稳定版 `0.9.4` 已提供 `miuix-nav`。需要 Glass、Material 或 Desktop Window 时，先确认项目可以接受 Beta，再选已发布的对应构件。旧版的 `Super*`、着色器和导航模块迁移按起点版本核对。

## Android Glass 与 Blur 的最低版本

已发布的 `miuix-glass-android:0.9.5-beta03` 声明 API 24，仍传递依赖声明 API 33 的 `miuix-blur-android`。应用的 `minSdk` 为 24–32 时，正常合并清单依然会因 Blur 失败。Android API 31 起提供 RenderEffect，API 33 起提供 RuntimeShader，后者才是玻璃和纹理模糊所需能力。

需要在 API 24–32 保留 Glass 组件的纯色回退时，上游文档给出在 app 清单的 `<uses-sdk>` 上添加 `tools:overrideLibrary="top.yukonga.miuix.kmp.blur"` 的做法（清单根节点声明 `xmlns:tools="http://schemas.android.com/tools"`）。这个做法只跳过该库的合并检查。避免在低 API 上直接调用 Blur 路径，并在实际最低 API 检查启动、纯色回退和受影响的组件。在 API 33+ 检查背景采样和模糊。若只需要常规 UI，可使用 `miuix-ui` 的不透明表面。

来源：[Beta Glass 文档](https://github.com/compose-miuix-ui/miuix/blob/3526cfe2ca0779c5a2eab99af8737a96c9a8a885/docs/zh_CN/guide/glass.md)、[Glass Android 发布构件](https://central.sonatype.com/artifact/top.yukonga.miuix.kmp/miuix-glass-android/0.9.5-beta03)、[Blur Android 发布构件](https://central.sonatype.com/artifact/top.yukonga.miuix.kmp/miuix-blur-android/0.9.5-beta03)。

## 工具链兼容性

该标签的 `BuildConfig.LIBRARY_VERSION` 为 `0.9.5`，发布脚本附加 `-beta03` 得到发布坐标。自 `0.9.5-beta02` 起，上游使用 Compose Multiplatform `1.13.0-rc01` 的 API。从 `beta01` 升级时，对齐实际解析的 Compose 依赖，并重新编译受影响的目标。上游自身的 compileSdk、JDK 和 Gradle 插件配置可用来排查问题，消费方要求以实际构件元数据和编译结果为准。 [上游版本目录](https://github.com/compose-miuix-ui/miuix/blob/3526cfe2ca0779c5a2eab99af8737a96c9a8a885/gradle/libs.versions.toml)

版本不匹配时检查实际依赖解析、Kotlin 元数据 / Compose 编译器兼容性、模块发布目标和最低 SDK。先解决具体冲突，再做必要升级。离线时保留已知可用版本并说明不能确认新发布物。

## 官方入口

- [快速开始](https://compose-miuix-ui.github.io/miuix/zh_CN/guide/getting-started)
- [平台支持](https://compose-miuix-ui.github.io/miuix/zh_CN/guide/multiplatform)
- [发布记录](https://github.com/compose-miuix-ui/miuix/releases)
- [Maven Central 模块检索](https://search.maven.org/search?q=g:top.yukonga.miuix.kmp)
