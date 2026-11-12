# 消息、事件与文件

## 消息结构

优先使用 `messagePostFormat: "array"` 和消息段数组，逐段处理，不仅根据 `raw_message` 猜测图片、引用或 @。兼容字符串格式的项目应明确使用 CQ 解析与转义，不能把不可信文本直接拼进 CQ 码。

常见段的发送字段：

| type | 核心 data 字段 | 注意 |
| --- | --- | --- |
| `text` | `text` | 纯文本 |
| `at` | `qq` | QQ 号字符串；`all` 是特殊值 |
| `reply` | `id` | 目标消息 ID，不是 QQ 号 |
| `image` | `file` | NapCat 可读取的路径、URL 或支持的编码形式 |
| `record` | `file` | 语音通常还涉及格式转换 |
| `video` | `file` | 视频与群文件上传不是同一种能力 |
| `file` | 依目标 action / 段定义 | 收到的 `file_id` 不等于本地路径 |

发送与接收字段不完全对称；不要把整个收到的消息对象原样作为发送参数。合并转发的 `node`、嵌套 `content` 与外层 action 参数按目标版本展开查证，不用字符串拼装。

来源：[消息段](https://napneko.github.io/onebot/segment)、[事件基础](https://napneko.github.io/onebot/basic_event)、[版本化 schema](https://github.com/NapNeko/NapCatDocs/blob/90399c468599fb28fe4c426e4444844ba9f89548/src/api/4.18.42/openapi.json)。

## 事件分流和会话范围

- 先看 `post_type`：消息、通知、请求、元事件有不同字段；`message_sent` 与 `message` 也应分开。不要将心跳、连接事件送进指令处理器。
- 消息再按 `message_type` 区分群聊与私聊；只有群消息可直接使用 `group_id`，临时私聊还有独立来源字段。
- 通知依据 `notice_type` / `sub_type`；请求依据 `request_type` / `sub_type`。好友、加群请求的处理保留原事件 `flag` 等标识，不从显示文本重建。
- 根据业务过滤自身发送消息，防止自动回复循环。多账号状态至少按 `self_id` 隔离，再按群 / 私聊目标隔离；消息 ID 的去重键也应包含账号及必要会话范围。
- 把 QQ 号、群号、消息 ID 当标识符。按目标 schema 在边界转换，不把所有数字字段（如时间、时长）一律转成字符串，也不依赖 ID 连续递增。
- 未知事件或扩展字段保留可观测性，避免异常直接中断整个消费循环。必要的去重与持久化由应用承担，不能假设连接重建后恰好投递一次。

文档的缓存大小、ID 算法和资源有效期描述不保证跨版本不变。消息引用、文件标识、临时 URL 可能失效；需要持久使用的文件在取得后保存到应用管理的存储，并保留与原事件的关联，不能只保存短期下载链接。

## 文件在哪台机器上

传给 NapCat 的本地路径由 NapCat 进程读取。在远程或容器部署中，采用共享卷中服务端可见的路径、NapCat 可访问的 URL，或目标版本支持的上传方式。`base64://` 会增加体积及内存占用，按文件大小选择，不用于无限制大文件。

下载 action 返回服务端本地路径时，客户端不能直接打开它；先确认共享挂载或取得可访问的下载结果。图片 URL / rkey 可能失效；重新调用支持的文件、图片、消息查询获取可用资源，别把文档中的估计有效期写成硬性保证。

语音原始资源可能是 silk，通用播放器需要转换；按 `get_record` 的目标版本参数选择格式。视频、图片和普通文件的大小限制及参数分别查证，旧指南中的固定大小不作为全部版本约束。

## Stream API

[文件指南](https://napneko.github.io/develop/file) 将 Stream API 标注为 v4.8.115+。先核对目标传输和版本是否支持 `upload_file_stream`、`download_file_stream` 等接口，再读该 action 的分块请求、顺序、结束信号与返回路径；普通 HTTP 一次 JSON 解析不能替代流式消费者。

文档中的流式响应带 `stream: "stream-action"`，其 `data.type` 区分：

| 值 | 消费端行为 |
| --- | --- |
| `stream` | 累积或写入数据块，继续等待 |
| `response` | 结合业务状态确认完成，才提交完整结果 |
| `error` | 终止并标记失败，不交付半成品 |

同时检查连接关闭、取消和业务失败。保留 echo 关联，清理失败的临时资源。`clean_stream_temp_file` 属于与流有关的普通 action，不能仅凭名字含 `stream` 就将所有接口归为同一种响应。

实现入口为 `packages/napcat-onebot/action/stream/`，请求格式需要时查目标版本源文件。媒体示例只说明结构，真实收发、编解码和跨主机可达性需分别验证。
