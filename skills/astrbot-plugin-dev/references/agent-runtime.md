# 触发现有会话的 Agent

`v4.30.0-alpha.1` 已提供 `self.context.agent.run_turn()`。内置 runtime 会沿用目标会话的人格、历史、工具、skills 和 Agent hooks。插件自行配置模型和工具时，见 [自定义 Agent 循环](ai-tools.md)。来源：[上游 Agent 指南](https://github.com/AstrBotDevs/AstrBot/blob/06fc50b43ea1c13093c91762f3b9361911362f9a/docs/zh/dev/star/guides/ai/agent.md)、[Alpha 发布记录](https://github.com/AstrBotDevs/AstrBot/releases/tag/v4.30.0-alpha.1)。

## 提交、等待与取消

```python
from astrbot.api.agents import PlainInput

run = await self.context.agent.run_turn(
    umo=event.unified_msg_origin,
    input_message=[PlainInput(text="请向用户说明本次分析的结果。")],
    source_event=event,
)
result = await run.result()
```

- 提交后拿到 handle，同一 session 的 turn 串行。`run.result()` 等待执行、历史保存及输出处理结束。在工具内排队同 session 的下一轮时应先返回，避免等待自己占用的会话。
- 默认由 AstrBot 投递回复，无需再发 `result.text`。取消等待不会停止 turn，终止执行需 `await run.cancel()`。
- `source_event` 必须与目标 UMO 匹配。Core 也可从同 UMO 的活跃事件解析权限，后台无来源事件时按 member 权限执行。
- `metadata` 使用插件命名空间和 JSON 兼容值。hooks 从 `event.get_extra("agent_metadata", {})` 读取，框架不会自动加入提示词、历史或后续 turn。

## 由插件处理待发送输出

```python
from astrbot.api.agents import PlainInput, TurnStatus, chain_from_content

run = await self.context.agent.run_turn(
    umo=event.unified_msg_origin,
    input_message=[PlainInput(text="请生成本次分析的摘要。")],
    send_to_user=False,
)
outputs = [
    update.payload
    async for update in run.events()
    if update.type == "output.ready"
]
result = await run.result()
if result.status == TurnStatus.COMPLETED:
    for output in outputs:
        if output.source == "reply":
            await self.context.send_message(
                output.target_umo, chain_from_content(output.content)
            )
```

`output.ready` 表示待发送内容已准备，包含 `target_umo`、`source`（`reply` 或 `tool`）及有序多媒体 `content`。示例仅投递最终回复。若需要工具准备的消息，按同一输出流处理。累计用量来自 `usage.updated`，用新快照替换旧值。流式视图按 `message_id` 用 `message.completed` 的完整内容替换增量。旧 runtime 示例中的 `event.data` 和 `result.chain` 对应当前的 `event.payload` 与 `result.content`。

## 继续对话

`run.follow_up(input_message=...)` 在原 runtime 和 conversation 排队下一轮并继承投递策略。`run.steer(input_message=...)` 尝试给活跃 turn 追加输入，返回 `None` 表示拒绝，接受时等待回执可获知输入是否已被消费并保存。拒绝后由调用方决定是否排队。需要给后续轮设置 metadata 时，用目标 `session_id` 显式发起 `run_turn`。
