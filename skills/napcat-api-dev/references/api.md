# API 查阅与调用

## 按版本定位接口

优先使用 [官方版本入口](https://napneko.github.io/api/)。文档仓库的版本化定义位于 `src/api/<版本>/openapi.json`；本技能核对了 [4.18.42 OpenAPI](https://github.com/NapNeko/NapCatDocs/blob/90399c468599fb28fe4c426e4444844ba9f89548/src/api/4.18.42/openapi.json)，它不是源码快照或运行实例版本的替代品。[Apifox](https://napcat.apifox.cn/) 也由官方插件文档链接，可作为查询入口，仍需核对版本。

读取 `paths["/<action>"]` 下的方法，继续展开 `requestBody`、`responses` 和用到的 `components.schemas`。检查 `required`、联合类型和示例，示例有额外字段并不代表它是必填参数。schema 也可能缺少业务条件：例如发送群消息仍需提供实际目标群，即使通用 schema 只把 `message` 标为必填。

| 需求 | 首先查询的 action |
| --- | --- |
| 连接和版本 | `get_version_info`、`get_status`、`get_login_info` |
| 发送、引用或撤回 | `send_msg`、`send_group_msg`、`send_private_msg`、`get_msg`、`delete_msg` |
| 群与成员 | `get_group_list`、`get_group_info`、`get_group_member_list` |
| 合并转发 | `send_forward_msg`、`send_group_forward_msg`、`get_forward_msg` |
| 文件和媒体 | `get_file`、`get_image`、`get_record`、`get_group_file_url`、`upload_group_file` |
| 请求处理 | `set_friend_add_request`、`set_group_add_request` |

这些是查询起点，不是全版本可用清单。扩展 action、管理员权限、PacketBackend 或 QQ 版本要求需逐项核对。

## HTTP 与 WS 的不同封装

HTTP POST 的路径包含 action，JSON body 直接放参数。以只读版本查询为例：

```http
POST /get_version_info
Authorization: Bearer <ONEBOT_TOKEN>
Content-Type: application/json

{}
```

发送群消息时，HTTP 路径为 `/send_group_msg`，以下仅为请求体结构示例，群号须替换为用户指定的目标：

```json
{
  "group_id": "123456789",
  "message": [{"type": "text", "data": {"text": "连接测试"}}]
}
```

WS 请求在连接内传输 action、params、echo：

```json
{
  "action": "get_login_info",
  "params": {},
  "echo": "login-check-0001"
}
```

普通成功响应示意：

```json
{
  "status": "ok",
  "retcode": 0,
  "data": {"user_id": 123456789, "nickname": "示例账号"},
  "echo": "login-check-0001"
}
```

HTTP 2xx 只是传输成功。普通同步 action 要检查业务 `status` / `retcode`，再读 `data`；失败记录 action、echo、retcode 和脱敏后的 `message` / `wording`。不要把任意 `data: null` 当成失败，一些无返回数据的操作需要按其契约判断。不同传输和版本的错误码可能不同，不能只硬编码一个失败码。

## WS 客户端实现要点

- 只有一个读取连接的循环，先按事件 `post_type` 与响应结构分流，不能每次调用都单独 `recv()` 并把下一帧认作自己的响应。
- 每个并发请求使用唯一 `echo`，维护 pending 映射。事件、心跳和其他 action 响应可以插队；未知 echo 不应唤醒别的请求。
- 普通 action 的匹配响应结束该请求；流式 action 按 [文件流规则](messages-files.md) 等待终态，不在第一个数据块就删除 pending。
- 超时、取消、断线时清理 pending；重连恢复事件消费，但不要自动重放发送、撤回、踢人等结果未知的操作。超时不能证明 NapCat 没有执行。
- 不把 `_async` 或 `_rate_limited` 后缀当成任务队列和限流保证。当前源码将它们映射到同一 handler，具体行为需查看目标版本实现。

## 从文档追踪实现

在 NapCatQQ 的 `packages/napcat-onebot/action/` 中：

1. `router.ts` 定义 action 名称；`index.ts` / `auto-register.ts` 决定注册关系。
2. 找到对应 action 类，检查 `payloadSchema`、`returnSchema`、`check` / `checkBasic`、`_handle`。处理继承的 schema 和校验，不能只读叶子类。
3. `OneBotAction.ts` 处理通用校验与响应；`network/http-server.ts`、`websocket-server.ts`、`websocket-client.ts` 决定传输层差异。

例如旧 [文件指南](https://napneko.github.io/develop/file) 的群文件直链参数写作 `group`，已核对的 OpenAPI 与 [GetGroupFileUrl 实现](https://github.com/NapNeko/NapCatQQ/blob/72912f293924f43463b5976b01fc094a8ae11481/packages/napcat-onebot/action/file/GetGroupFileUrl.ts) 使用 `group_id` 和 `file_id` 字符串。向用户解释这种差异并给出版本依据，不照抄旧片段。

来源：[Action 注册与插件调用](https://github.com/NapNeko/NapCatQQ/blob/72912f293924f43463b5976b01fc094a8ae11481/packages/napcat-onebot/action/index.ts)、[公共 action 基类](https://github.com/NapNeko/NapCatQQ/blob/72912f293924f43463b5976b01fc094a8ae11481/packages/napcat-onebot/action/OneBotAction.ts)。
