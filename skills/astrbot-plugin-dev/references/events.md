# 指令、事件与钩子

来源：[处理消息事件](https://docs.astrbot.app/dev/star/guides/listen-message-event.html)。

## 读取消息

`event.message_str` 是文本段拼接后的纯文本，不包含图片等完整内容；`event.message_obj.message` 是有序消息段列表，`event.message_obj.raw_message` 是适配器原始对象。

常用方法：`get_sender_id()`、`get_sender_name()`、`get_group_id()`、`get_platform_name()`、`get_platform_id()`。跨平台定位会话保存 `event.unified_msg_origin`，不要仅用群号/用户号替代它。

## 命令与过滤

以下片段放在 `Star` 子类内：

```python
@filter.command("add", alias={"加法"})
async def add(self, event: AstrMessageEvent, a: int, b: int):
    """相加两个整数，例如 /add 1 2。"""
    yield event.plain_result(str(a + b))


@filter.command_group("math")
def math(self):
    pass


@math.command("sub")
async def subtract(self, event: AstrMessageEvent, a: int, b: int):
    yield event.plain_result(str(a - b))
```

框架按 handler 参数解析命令参数。命令名不要包含空格；多级命令用 `@math.group("calc")`，不是 `@math.command_group(...)`。指令组函数只需占位，不承担消息处理。

过滤器叠加为 AND：

```python
@filter.permission_type(filter.PermissionType.ADMIN)
@filter.command("admin_status")
@filter.event_message_type(filter.EventMessageType.PRIVATE_MESSAGE)
async def admin_status(self, event: AstrMessageEvent):
    yield event.plain_result("就绪")
```

这里的 `ADMIN` 指 AstrBot 管理员，不等同于群管理员。群/私聊过滤使用 `GROUP_MESSAGE`、`PRIVATE_MESSAGE` 或 `ALL`；平台过滤使用 `@filter.platform_adapter_type(filter.PlatformAdapterType.AIOCQHTTP)` 等枚举，多个平台可按位或。

命令、普通监听器和钩子支持 `priority`，默认 0，较大的值更早执行。通用全消息监听器会收到大量事件，不要无条件回复导致刷屏。

## 钩子签名

钩子不能和命令、事件类型、平台、权限等过滤装饰器混用。表中的函数均有 `self`，名称以装饰器为准：

| 装饰器 | 除 self 外的参数 | 用途 |
| --- | --- | --- |
| `on_astrbot_loaded()` | 无 | AstrBot 初始化完成 |
| `on_waiting_llm_request()` | `event` | 获取 LLM 会话锁之前反馈等待状态 |
| `on_llm_request()` | `event, req: ProviderRequest` | 修改请求 |
| `on_llm_response()` | `event, resp: LLMResponse` | 修改模型结果 |
| `on_decorating_result()` | `event` | 修改 `event.get_result().chain` |
| `after_message_sent()` | `event` | 消息发送之后 |
| `on_agent_begin()` | `event, run_context` | Agent 开始 |
| `on_using_llm_tool()` | `event, tool, tool_args` | 调用工具之前 |
| `on_llm_tool_respond()` | `event, tool, tool_args, tool_result` | 工具调用之后 |
| `on_agent_done()` | `event, run_context, resp` | 内置 Agent 退出时执行清理 |

旧版的 Agent 钩子支持范围按目标版本确认。请求与响应类型从 `astrbot.api.provider` 导入，Agent 类型导入见 [ai-tools.md](ai-tools.md)。

在 `v4.30.0-alpha.1` 的内置 runner 中，`on_agent_done` 覆盖正常完成、异常、取消及步数耗尽。检查 `run_context.run_end_reason`、`run_context.run_error`，并允许 `resp` 为 `None`。需要在发送之前修改模型回复时用 `on_llm_response`，等待历史与输出处理完成时用 [run.result()](agent-runtime.md)。

钩子需要回复时用 `await event.send(event.plain_result("..."))`，不使用 `yield`。装饰结果前检查 `event.get_result()` 是否存在，避免假定每个处理分支都有消息结果。

## 动态上下文

稳定的长期角色规则可以修改 `req.system_prompt`。每轮变化的时间、检索摘要、临时状态放进用户内容，减少反复改写系统提示造成的缓存失效：

```python
from astrbot.api.provider import ProviderRequest
from astrbot.api.agents import TextPart


@filter.on_llm_request()
async def add_context(self, event: AstrMessageEvent, req: ProviderRequest):
    req.extra_user_content_parts.append(
        TextPart(text="本轮相关上下文：用户请求处理待办事项。")
    )
```

示例使用 `v4.30.0-alpha.1` 的公开导入，旧版从 `astrbot.core.agent.message` 导入 `TextPart`。`TextPart(...).mark_as_temp()` 自 `v4.24.0` 起可标记临时内容。使用新版事件存储时，该标记排除后续模型上下文，原文仍可能被持久化。较大的外部数据可按需检索或通过工具读取。

## 传播

`event.stop_event()` 会停止后续插件 handler 和 LLM 请求。适用于明确接管的消息，例如完成了某个交互流程；它不是 Python 的 `return`，需要时两者分别处理。一般日志监听不应终止传播。
