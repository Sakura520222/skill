# 连接、安装与配置

## 从 NapCat 的视角识别连接方向

| 配置数组 | NapCat 的角色 | 应用的角色 | 用途 |
| --- | --- | --- | --- |
| `network.httpServers` | HTTP 服务端 | 发起 API 请求 | 调用 action |
| `network.httpClients` | HTTP 客户端 | 接收上报的 HTTP 服务端 | 接收事件 |
| `network.websocketServers` | WS 服务端（正向 WS） | 连接 NapCat | 同一连接调用 API、接收事件 |
| `network.websocketClients` | WS 客户端（反向 WS） | 等待 NapCat 连接的 WS 服务端 | 同一连接调用 API、接收事件 |
| `network.httpSseServers` | HTTP / SSE 服务端 | 对应客户端 | 仅在目标版本支持并明确选择时使用 |

官方 `onebot/network` 页的 HTTP 角色描述与基础配置页、实现存在倒置；按本表和目标版本实现判断。HTTP API 可用并不表示已配置事件上报。不要同时建立多条事件链路后又把重复事件当作独立消息。

来源：[基础配置](https://napneko.github.io/config/basic)、[存在角色描述差异的网络页](https://napneko.github.io/onebot/network)、[配置 schema](https://github.com/NapNeko/NapCatQQ/blob/72912f293924f43463b5976b01fc094a8ae11481/packages/napcat-onebot/config/config.ts)。

## 安装与配置入口

- [安装导航](https://napneko.github.io/guide/start-install) 按 [Shell](https://napneko.github.io/guide/boot/Shell) 和 [Framework](https://napneko.github.io/guide/boot/Framework) 分流；先识别现有部署方式、操作系统及 QQ 兼容版本，再采用对应说明。查询 API 不需要安装 NapCat。
- WebUI 是管理入口。文档示例端口为 `6099`，实际端口以启动日志和当前配置为准；占用时可能递增。OneBot API 使用网络配置里单独启用的端口，不能把 WebUI 端口当作 API 端口。
- WebUI 登录凭据与 OneBot 网络条目的 token 分开配置。已有网络条目只做必要增量调整，保留其他账号、连接、token 和超时设置。
- 文件配置通常为 `config/onebot11_<QQ号>.json`；文档记录 v4.5.3 后支持 `onebot11.json` 默认配置。确认进程实际读取路径，尤其是容器卷和多账号环境；不要仅凭文件名猜测生效文件。
- `name` 要能唯一识别条目，`enable` 决定是否启用。消息格式 `messagePostFormat` 与消费端解析保持一致，通常使用 `array`。
- 当前实现的网络配置还包含 `httpSseServers` 和 `plugins`；旧文档片段不覆盖全部字段。基础配置页把 `enableWebsocket` 标作无效，但核对的 HTTP 实现已包含 WS 支持；不要把旧注释作为所有版本结论。

## 鉴权与跨主机

HTTP / 正向 WS 源码支持 `Authorization: Bearer <token>` 和 `access_token` 查询参数；优先用 header，避免 URL 被访问日志记录。反向 WS 由 NapCat 发起连接并带上配置的 Bearer token，接收端校验该值。不能由 OpenAPI 的空 `security` 数组推断部署不需要鉴权。

`127.0.0.1` 始终指当前进程所在网络命名空间：应用容器中的回环地址不是宿主机或 NapCat 容器。沿“发起方 → 监听方 → 端口映射 → 代理路径”检查，反向 WS 的 URL 填应用接收端。远程 WSS 保留证书验证；不要为绕过握手故障直接关闭验证。

来源：[HTTP 实现](https://github.com/NapNeko/NapCatQQ/blob/72912f293924f43463b5976b01fc094a8ae11481/packages/napcat-onebot/network/http-server.ts)、[正向 WS](https://github.com/NapNeko/NapCatQQ/blob/72912f293924f43463b5976b01fc094a8ae11481/packages/napcat-onebot/network/websocket-server.ts)、[反向 WS](https://github.com/NapNeko/NapCatQQ/blob/72912f293924f43463b5976b01fc094a8ae11481/packages/napcat-onebot/network/websocket-client.ts)。

## 排查顺序

| 现象 | 先验证 |
| --- | --- |
| 拒绝连接 | 实际监听端口、条目启用、容器映射和连接方向 |
| 401 / 403 或 WS 鉴权拒绝 | OneBot token、请求 header、代理转发，是否误用了 WebUI token |
| 收到 HTML 或 WebUI 登录页 | 是否误连管理端口或错误的代理路径 |
| API 正常但没有事件 | 是否启用事件传输；WS 路径角色、过滤条件、自己发送消息的上报开关 |
| 收到两次或回复循环 | 重复网络条目、重复订阅、自身消息、重连后的重复监听器 |
| 视频 / 语音失败 | NapCat 端文件可读性、QQ 支持格式及当前安装的编解码能力 |

音视频依赖随安装方式和版本变化，按 [高级配置](https://napneko.github.io/config/advanced) 核对，不因普通文本 API 任务额外安装 FFmpeg 或修改系统 PATH。
