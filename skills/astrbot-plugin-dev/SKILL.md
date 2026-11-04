---
name: astrbot-plugin-dev
description: 开发、修改和调试 AstrBot Python 插件（Star），处理消息指令、事件钩子、插件配置、LLM 工具、存储及 WebUI 视图，并准备插件发布。Use for AstrBot plugin development; 不用于普通机器人使用问答或独立的 NapCat/OneBot 服务开发。
license: AGPL-3.0-or-later
metadata:
  version: "1.1.0"
  documentation_snapshot: "2026-11-04"
---

# AstrBot 插件开发

根据用户目标，在已有插件中完成改动，或创建可被 AstrBot 加载的新插件。先确认项目的 AstrBot 版本、目标消息平台、已有代码和依赖；只读取本次功能涉及的参考文件。

本技能基于官方中文开发文档整理，来源、固定提交和更新方式见 [references/sources.md](references/sources.md)。快照来自版本字段为 4.29.4 的上游主分支，也包含该正式版发布后的文档变化；例如 SSE `onClose` 需要后续主分支实现，不能仅凭版本号判断可用。涉及版本敏感 API 时，优先核对目标环境的公开 API 或对应版本源码；联网不可用时说明尚未验证的兼容性。

## 按任务选读

| 任务 | 参考文件 |
| --- | --- |
| 新插件、目录、metadata、生命周期、开发环境 | [quick-start.md](references/quick-start.md) |
| 命令、参数、指令组、权限、事件钩子、阻止传播 | [events.md](references/events.md) |
| 被动回复、主动推送、消息链、媒体和交互按钮 | [messaging.md](references/messaging.md) |
| 配置 Schema、用户/会话选择器、KV 和持久化文件 | [config-storage.md](references/config-storage.md) |
| 调用 LLM、结构化判断、注册工具、Agent、对话和人格 | [ai-tools.md](references/ai-tools.md) |
| 多轮交互、等待下一条消息、超时和会话隔离 | [session-control.md](references/session-control.md) |
| 插件自定义页面、bridge、Web API、上传及 SSE | [web-views.md](references/web-views.md) |
| 插件元数据、配置及页面的多语言展示 | [i18n.md](references/i18n.md) |
| 文转图、HTML 渲染、平台实例及 OneBot 专用 API | [rendering-platform.md](references/rendering-platform.md) |
| 插件打包、版本声明、GitHub 和插件市场 | [publishing.md](references/publishing.md) |

## 实现约束

- 插件入口是 `main.py` 中继承 `Star` 的类，元数据使用 `metadata.yaml`；handler 放在插件类内。新项目可从 [assets/astrbot_plugin_example/](assets/astrbot_plugin_example/) 复制最小实例，按 quick-start 中的说明改名和填写元数据。
- 优先使用 `astrbot.api`。参考文件明确使用的 `astrbot.core` 接口存在版本耦合，按目标版本核对，不凭空替换成猜测的 API。
- 普通消息 handler 可以 `yield event.*_result(...)`。事件钩子和 session waiter 回调需要发送消息时使用 `await event.send(...)`，不要把它们改成异步生成器。调用 `event.stop_event()` 会阻止后续插件和 LLM 流程，只在确实需要接管消息时使用。
- 网络 I/O 使用异步客户端（如 `aiohttp`、`httpx`），配置超时；释放插件持有的客户端和后台任务。用户数据放在 `data/plugin_data/<plugin_name>/` 或插件 KV 中，避免更新插件时丢失。
- AstrBot 的 `_conf_schema.json` 是其自定义配置格式，不能直接套用通用 JSON Schema。敏感值设 `secret: true`；该属性仅遮罩 UI，不能作为加密保证。
- `@filter.llm_tool` 的参数 schema 来自 docstring 的 `Args:` 段，格式为 `参数名(string): 描述`，仅写 Python 类型注解不够。需要手写 schema 时用 `FunctionTool` 和 `context.add_llm_tools()`。
- 复用当前会话的模型和 `unified_msg_origin`，保留用户现有配置、平台与插件身份。仅在功能明确依赖协议端时调用 OneBot/NapCat 专用 API，并加平台判断。

## 完成与验证

1. 实现用户要求的最小完整行为，补齐实际需要的依赖、配置和版本声明。不要为了套模板覆盖现有插件结构。
2. 运行项目已有检查；新插件至少验证 Python 语法、YAML/JSON、`ruff check` 和 `ruff format --check`，并测试实际业务逻辑。外部服务、并发或持久化改动应有相应的可观察验证。
3. 在可用的 AstrBot 开发实例中重载插件，检查加载日志并验证指令/工具/页面。覆盖适用的权限、平台限制、无效输入、超时和卸载清理；没有实例时明确区分静态检查与未完成的运行验证。
4. 交付改动、使用方式、依赖/最低版本和已执行的验证。准备可发布文件不等于已获准推送 GitHub、提交市场或部署到用户机器人；按用户本次授权执行相应操作。
