# 等待用户后续消息

来源：[会话控制](https://docs.astrbot.app/dev/star/guides/session-control.html)。整理日期：2026-10-23。基础接口要求 `>=3.4.36`。

`session_waiter` 适用于问答、确认、组队等需要接管下一条输入的流程。当前消息管道会在既有访问控制与预处理之后先分发给有效 waiter，被接管的消息不再进入普通插件和 Agent；不要为新版本重复实现旧的内置会话分发 handler。

## 最小交互

以下方法放在插件类内，并导入 `AstrMessageEvent`、`filter`：

```python
from astrbot.core.utils.session_waiter import SessionController, session_waiter


@filter.command("collect_name")
async def collect_name(self, event: AstrMessageEvent):
    """等待用户输入一个名称。"""
    @session_waiter(timeout=60, record_history_chains=False)
    async def receive(controller: SessionController, reply: AstrMessageEvent):
        text = reply.message_str.strip()
        if text == "取消":
            await reply.send(reply.plain_result("已取消。"))
            controller.stop()
            return
        if not text:
            await reply.send(reply.plain_result("请输入非空名称，或发送取消。"))
            controller.keep(timeout=60, reset_timeout=True)
            return
        await reply.send(reply.plain_result(f"已收到名称：{text}"))
        controller.stop()

    yield event.plain_result("请在 60 秒内发送名称，或发送取消。")
    try:
        await receive(event)
    except TimeoutError:
        yield event.plain_result("等待已超时。")
    finally:
        event.stop_event()
```

waiter 回调使用 `await reply.send(...)`，不可 `yield`。是否继续由 `controller.keep()`/`stop()` 控制；普通 `return` 只退出本次回调，不等于结束等待会话。

## 控制与隔离

- `controller.keep(timeout=60, reset_timeout=True)` 从当前时刻重新计时，timeout 必须大于 0。
- `reset_timeout=False` 在剩余时间上追加 timeout；不要误当成重新设置总时长。
- `controller.stop()` 立即结束等待；启用历史记录时可读 `get_history_chains()`。
- 默认会话区分依据为发送者 ID。涉及多平台、群与私聊同时交互时，按业务自定义 `SessionFilter`，避免串会话。

```python
from astrbot.core.utils.session_waiter import SessionFilter


class UserInSession(SessionFilter):
    def filter(self, event: AstrMessageEvent) -> str:
        return f"{event.unified_msg_origin}:{event.get_sender_id()}"
```

启动时传 `await receive(event, session_filter=UserInSession())`。如需求是整个群共享进度，使用当前平台会话来源作为标识，明确这是群体交互；不要仅以裸群号隔离多个机器人平台。

验证不同用户/群/平台、重复启动、取消、超时和插件停用。`stop_event()` 的影响见 [events.md](events.md)。
