---
name: napcat-api-dev
description: 查阅 NapCatQQ 官方 API 与开发文档，开发和调试 OneBot 11 HTTP/WebSocket 对接、消息事件与文件处理、NapCat TypeScript/JavaScript 插件和 WebUI 扩展，以及定位 NapCat 源码接口。用于明确以 NapCat 为协议端或插件宿主的任务；普通 AstrBot Python 插件逻辑不属于此技能。
license: AGPL-3.0-or-later
metadata:
  version: "1.0.0"
  documentation_snapshot: "2026-11-12"
---

# NapCat API 与开发文档

按目标 NapCat 版本查证接口，再完成对接、开发或诊断。保持调用方现有框架与语言；外部 OneBot 客户端和运行在 NapCat 内的插件是不同部署方式，不为了调用 API 把应用改成插件。

## 定位任务与版本

- 从现有配置、依赖、启动日志和代码确定：NapCat 版本、QQ 版本、Shell / Framework、操作系统、容器边界，以及 HTTP / 正向 WS / 反向 WS / 内嵌插件。
- 已有实例以实际运行版本为准，可用已授权的只读 `get_version_info` 查询。不要从仓库根 `package.json` 的 `0.0.1` 推断 NapCat 发布版本。
- 文档快照固定于 NapCatDocs `90399c46`；源码核对固定于 NapCatQQ `72912f29`。这两个提交与文档中的版本化 OpenAPI 各有版本边界，不能视为同一个 release。完整提交、来源和刷新方法见 [sources.md](references/sources.md)。
- 用户问最新接口或遇到快照差异时，查官方目标版本的 OpenAPI、类型定义及实现。没有联网或目标环境时明确证据范围，不补造参数和支持状态。

## 按任务读取

| 任务 | 资料 |
| --- | --- |
| 安装方式选择、端口、鉴权、正反向连接、容器连接失败 | [connection.md](references/connection.md) |
| 查询 action、HTTP / WS 请求响应、版本化 OpenAPI、错误排查 | [api.md](references/api.md) |
| 消息段、事件分流、请求处理、文件与流式传输 | [messages-files.md](references/messages-files.md) |
| NapCat 插件生命周期、配置、WebUI、热重载与发布准备 | [plugins.md](references/plugins.md) |
| 修改 NapCat 本体、追踪 action 到底层、构建与回归 | [source-development.md](references/source-development.md) |

只读取当前任务需要的资料。原始全站文档和上游源码不随技能分发。

## 接口查证与实现

1. 明确调用所在层：外部 OneBot API、插件 `ctx.actions`、插件 WebUI 路由或 NapCat 内部 API。不要混用它们的鉴权、地址或返回类型。
2. 从 [官方 API 版本入口](https://napneko.github.io/api/) 选择目标版本；查询 action 的参数、必填字段、消息段和返回 schema，并展开用到的 `$ref`。只有功能名时先找候选 action，再读定义。
3. 文档不一致时追踪该版本 action 的注册、`payloadSchema`、校验及 `_handle`。记录差异和证据；当前主分支只能说明当前主分支。未知扩展接口不要按 go-cqhttp 同名方法推测。
4. 外部调用检查传输状态和 OneBot `status` / `retcode`；WS 通过唯一 `echo` 关联响应，事件单独分发。发送超时属于结果未知，先核实再决定是否重试，避免重复发送。
5. 优先使用结构化消息段，保留接收字段的类型信息。远程文件路径在 NapCat 所在主机或容器解析；不要把客户端本地路径当成服务端可访问路径。

## 验证与交付

- API 查询给出 action、连接方式、请求示例、关键响应字段、版本依据及来源链接；明确这是示例还是实测结果。
- 对接先验证只读 API、鉴权失败处理、响应与事件混合、断线后的 pending 请求清理；涉及消息发送的功能再按用户授权在指定会话验证。
- 插件完成项目类型检查和构建后，验证目标 NapCat 的加载、事件触发、配置重载与卸载清理。构建成功不等于 QQ 侧可用。
- 修改本体时检查受影响构建和运行路径，区分静态签名核对、模拟测试与真实 QQ 验证；没有实例时列明未验证项。
- 输出修改文件、验证结果和剩余限制。开发、发布和部署分别按用户请求的范围执行。
