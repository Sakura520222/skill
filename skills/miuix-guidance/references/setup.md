# 接入与版本选择

本页基于固定主分支快照；来源、适用边界及复核方法见 [sources.md](sources.md)。

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

第二项仅在需要 Preference 时添加。相关 Miuix 模块通常采用同一已发布版本；若某模块尚未发布该版本，应重新核对发布记录，不拼接猜测的版本。其他单平台构件后缀从实际 Maven 发布物确认；本次线上站点与主分支的 Wasm 后缀写法已有差异，不手工推导。

## 按需求选择模块

| 需求 | 模块 | 约束 / 传递依赖 |
| --- | --- | --- |
| 主题、基础控件、Scaffold、普通弹层 | `miuix-ui` | 包含 `miuix-core` 和 `miuix-squircle` |
| 设置项、带标题摘要的开关 / 选择器 | `miuix-preference` | 依赖 `miuix-ui`，包名为 `preference` |
| 扩展图标 | `miuix-icons` | 基础 UI 仅含少量核心图标 |
| Glass 图标 | `miuix-glass-icons` | 可选独立模块，先确认目标版本是否有发布 |
| 背景采样与模糊 | `miuix-blur` | 本次快照 Android 最低 API 33 |
| 连续圆角 | `miuix-squircle` | UI 已传递包含；低 API 有相应降级路径 |
| 运行时着色器和材质定义 | `miuix-material` | 本次快照最低 API 24，具体绘制能力另判定 |
| 玻璃表面与组件 | `miuix-glass` | Android 最低 API 33；传递引入 material、blur、ui |
| Miuix 自有导航 | `miuix-nav` | 可独立使用，不要求替换项目现有导航 |
| 桌面窗口与标题栏 | `miuix-window` | 仅 Desktop JVM；放在对应桌面 source set |

这里的模块清单反映固定主分支。旧版文档可能使用不同坐标、`Super*` 组件或不同包结构；维护旧版时遵循该版本，不进行无关迁移。

## 不照搬上游构建环境

固定快照 `BuildConfig.kt` 的库版本字段是 `0.9.4`，但这不能证明主分支新增 API 已包含在 Maven 的 `0.9.4` 中。它也不能证明该版本仍是最新发布。该文件的 compileSdk、JDK、Gradle 插件等配置属于上游开发工程，不等于所有消费方都必须复制。

版本不匹配时检查实际依赖解析、Kotlin 元数据 / Compose 编译器兼容性、模块发布目标和最低 SDK。先解决具体冲突，再做必要升级。离线时保留已知可用版本并说明不能确认新发布物。

## 官方入口

- [快速开始](https://compose-miuix-ui.github.io/miuix/zh_CN/guide/getting-started)
- [平台支持](https://compose-miuix-ui.github.io/miuix/zh_CN/guide/multiplatform)
- [发布记录](https://github.com/compose-miuix-ui/miuix/releases)
- [Maven Central 模块检索](https://search.maven.org/search?q=g:top.yukonga.miuix.kmp)
