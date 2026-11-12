# NapCat 插件开发

插件是由 NapCat 加载的 JS / TS 模块，使用 `napcat-types` 提供的类型；不是 AstrBot 的 Python `Star` 插件，也不是独立 OneBot 服务。已有项目沿用其构建和目录；新项目参考 [官方模板](https://github.com/NapNeko/napcat-plugin-template)，先核对模板提交、类型包及宿主版本。

## 生命周期与上下文

| 导出 | 用途 |
| --- | --- |
| `plugin_init` | 必须导出；初始化资源、配置与路由 |
| `plugin_onmessage` | 消息处理；区分消息类型和自身消息 |
| `plugin_onevent` | OneBot 事件处理；按事件类型分流 |
| `plugin_cleanup` | 卸载或重载清理 |
| `plugin_config_ui` / `plugin_config_schema` | 配置表单 schema |
| `plugin_get_config` / `plugin_set_config` | 需要自定义时接管配置读写 |
| `plugin_config_controller` / `plugin_on_config_change` | 动态配置界面及 reactive 字段变化 |

用 `PluginModule['plugin_init']` 等索引类型校验钩子签名，不另写一套可能漂移的接口。消息和通用事件钩子不要重复执行同一业务；具体分发条件以目标宿主为准。

`ctx.logger` 记录插件日志；`ctx.configPath` 和 `ctx.dataPath` 用于配置与持久数据；`ctx.pluginPath` 是插件安装目录。配置和业务状态不要只保存在模块变量中，热重载后要能恢复。

内部调用格式为 `ctx.actions.call(actionName, params, ctx.adapterName, ctx.pluginManager.config)`。这四个参数不是外部 HTTP 的 JSON 信封；当前 `call` 返回业务 `data`，错误会抛出，不返回完整的 HTTP `status/retcode/data` 包。当前 helper 还会把空 `data` 视为错误，因此无数据操作若异常，追踪 helper 和目标 handler，不能直接断定 QQ 操作未发生。

优先经 action 完成功能。`ctx.core` / `ctx.oneBot` 是内部对象，使用它们会加大版本耦合；需要时查对应源码，不根据名称猜测私有 API。`ctx.getPluginExports(id)` 可能返回 `undefined`，插件间依赖需处理对方尚未加载或已经卸载。

来源：[机制](https://napneko.github.io/develop/plugin/mechanism)、[开发入口](https://napneko.github.io/develop/plugin/index)、[PluginModule 与上下文类型](https://github.com/NapNeko/NapCatQQ/blob/72912f293924f43463b5976b01fc094a8ae11481/packages/napcat-onebot/network/plugin/types.ts)、[action helper](https://github.com/NapNeko/NapCatQQ/blob/72912f293924f43463b5976b01fc094a8ae11481/packages/napcat-onebot/action/index.ts)。

## 配置与 WebUI

先使用 schema 表单，只有需要独立交互页面才构建 WebUI。配置控件类型、默认值和真实保存逻辑保持一致；`plugin_on_config_change` 用于界面响应式变化，不把它当成所有配置写入的持久化钩子。

| 路由用途 | 入口 / 前缀 |
| --- | --- |
| 需要鉴权的 API | `ctx.router.get/post/...` → `/api/Plugin/ext/<plugin-id>/` |
| 无鉴权 API | `ctx.router.getNoAuth/postNoAuth/...` → `/plugin/<plugin-id>/api/` |
| 静态资源 | `ctx.router.static` → `/plugin/<plugin-id>/files/<urlPath>/` |
| 内存资源 | `ctx.router.staticOnMem` → `/plugin/<plugin-id>/mem/<urlPath>/` |
| 页面入口 | `ctx.router.page` → `/plugin/<plugin-id>/page/<path>` |

管理数据、配置修改使用鉴权 API。不要因官方演示方便而把管理接口改成 `NoAuth`；确需公开的 webhook 自行验证其调用方。前端基路径与构建产物位置、插件 ID 保持一致，不能把开发服务器 URL 硬编码进发布包。

来源：[配置与 WebUI](https://napneko.github.io/develop/plugin/start-webui)、[项目结构](https://napneko.github.io/develop/plugin/structure)。

## 构建、热重载和发布准备

检查项目实际脚本、lockfile 和构建配置。模板通常输出 ESM `index.mjs`、`package.json` 及可选 `webui/`；确认 `main` 指向确实存在的产物，类型包不会变成缺失的运行时依赖，安装后的相对资源路径有效。

热重载通过 `napcat-plugin-debug` 与 `napcat-plugin-debug-cli/vite` 的 `napcatHmrPlugin` 协作。构建钩子可能连接调试服务并自动复制、加载或重载插件，因此 `build` 不一定只有本地副作用。只想编译验证时先检查并禁用该自动部署行为；开发部署需要指向用户指定的实例。

文档中的调试服务默认是本机 `127.0.0.1:8998` 且不启用认证。需要远程调试时配置 token 和受限连接，不直接公开无鉴权管理端口。`plugin_cleanup` 释放计时器、事件订阅、连接与自己注册的外部资源，并处理仍在执行的任务；连续重载后不应出现重复回复或重复定时任务。

发布前核对包名、版本、最低 NapCat 版本、入口、前端文件及插件索引当前规则。官方模板 CI 可能自动创建 release、fork 索引并提 PR，推送 tag 前理解这些动作；仅编写插件不代表已请求发布。不要为本地开发预先要求用户配置发布 PAT。

验证至少覆盖：加载成功、目标事件只处理一次、无关事件忽略、配置保存后重载可恢复、卸载后停止处理。未连接真实宿主时明确只有类型 / 构建验证。

来源：[热重载](https://napneko.github.io/develop/plugin/hot-reload)、[发布流程](https://napneko.github.io/develop/plugin/publish)。
