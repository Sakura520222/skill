# LLM、工具与对话

来源：[调用 AI](https://docs.astrbot.app/dev/star/guides/ai.html)。整理日期：2026-11-04。聊天模型与 Agent 调用优先使用 `>=4.5.7` 的新接口；下方新增的判断提供商需单独确认目标版本支持。

## 按当前会话选择模型

```python
provider_id = await self.context.get_current_chat_provider_id(
    umo=event.unified_msg_origin
)
response = await self.context.llm_generate(
    chat_provider_id=provider_id,
    prompt="用一句话概括这项任务。",
)
yield event.plain_result(response.completion_text)
```

不要硬编码用户的 provider ID 或自行复制 AstrBot 已管理的密钥。没有可用模型、服务超时或请求失败时给出可操作的错误；不要记录完整密钥和私密对话。

`llm_generate()` 也可传 `contexts`。同时指定 `prompt` 时，它会追加到输入最后。单次调用不等同于已经更新 AstrBot 的持久化会话历史。

## 结构化判断（Decision Provider）

该能力已在 `v4.29.4` 标签文档中确认；面向更早版本时先核对 `context.decision` 和相关公开类型。先在 WebUI 的“模型提供商 → 判断”配置独立的判断提供商，它不使用上文的聊天模型 ID。

`self.context.decision` 适合判断是否回复、选择处理分支或给条件评分。`state` 接收 `str | list | dict`，会原样传给判断模型；只传本次判断所需的上下文。

```python
from astrbot.api.provider import (
    DecisionChoiceAnswer,
    DecisionChoiceQuestion,
    DecisionError,
)

try:
    answers = await self.context.decision.ask(
        {
            "strategy": DecisionChoiceQuestion(
                instructions="选择适合这条消息的回复策略。",
                criteria={"brief": "简短回复", "detailed": "详细说明"},
            )
        },
        state={"message": event.message_str},
    )
except DecisionError:
    yield event.plain_result("判断服务暂不可用，请稍后重试。")
    return

answer = answers["strategy"]
if isinstance(answer, DecisionChoiceAnswer):
    yield event.plain_result(f"选择：{answer.choice}，概率：{answer.probability:.2f}")
```

以上片段放在普通消息 handler 内；钩子中仍需使用 `await event.send(...)`。提供商缺失、超时、连接/HTTP 错误、非法 JSON 或不符合选项与概率契约的响应统一抛出 `DecisionError`。捕获后按业务选择反馈、跳过或降级，不要把失败当成有效判断结果。

| 接口/题型 | 返回值和约束 |
| --- | --- |
| `ask(questions, state=...)` | 按问题名返回结果字典，可混合多种题型；读取字段前按类型判断 |
| `choose(question=..., criteria=..., state=...)` | 返回 `DecisionChoiceAnswer`，`criteria` 为至少两个选项 ID 到说明的映射 |
| `yes_no(question=..., state=..., threshold=0.7)` | 返回 `bool`，阈值由业务决定 |
| `DecisionBooleanQuestion(instructions=...)` | 结果为 `DecisionBooleanAnswer`，`probability` 表示陈述为真的概率 |
| `DecisionChoiceQuestion(instructions=..., criteria=...)` | 结果包含 `choice`、选中项 `probability`、完整 `probabilities` 和 `confidence` |
| `DecisionScoreQuestion(instructions=..., criteria=...)` | `criteria` 为从低到高的 2～10 个等级；结果 `score` 可为小数，范围为 0 到等级数减 1 |

评分类结果 `DecisionScoreAnswer` 仅含 `score`、`legend`、`probabilities`、`confidence`，其中 `legend` 和 `probabilities` 的等级编号使用字符串（如 `"0"`）；不要按选择题结果读取 `choice` 或 `probability`。三个 Answer 类型互相独立，`DecisionAnswer` 是其联合类型。相关类型可从 `astrbot.api.provider` 导入。

需要指定判断提供商时，给调用传入已配置的 `provider_id`；省略则使用默认判断提供商。它不替代有工具循环的 Agent，也不自动修改用户的聊天模型或会话历史。

## 装饰器工具

放在插件类内：

```python
@filter.llm_tool(name="add_numbers")
async def add_numbers(self, event: AstrMessageEvent, a: int, b: int) -> str:
    """计算两个整数的和。

    Args:
        a(number): 第一个整数。
        b(number): 第二个整数。
    """
    return str(a + b)
```

工具输出可返回给模型；若需求是向用户直接发送，按普通工具 handler 支持的消息结果方式处理。不要让同一路径既无条件主动发送，又让模型重复发送相同内容。

参数 schema **取自 docstring**，不是函数类型注解。`Args:` 中每个参数必须采用 `name(type): 描述`；支持 `string`、`number`、`object`、`boolean`、`array`，`>=4.5.7` 支持 `array[string]` 等子类型。缺少正确说明可能生成空 schema、静默丢参，最终调用失败。不要给装饰器传 `parameters=...`，该写法不会定义 schema。

## 显式 FunctionTool

需要精确 schema 或供局部 Agent 使用时：

```python
from pydantic import Field
from pydantic.dataclasses import dataclass

from astrbot.core.agent.run_context import ContextWrapper
from astrbot.core.agent.tool import FunctionTool, ToolExecResult, ToolSet
from astrbot.core.astr_agent_context import AstrAgentContext


@dataclass
class AddTool(FunctionTool[AstrAgentContext]):
    name: str = "add_numbers"
    description: str = "计算两个整数的和。"
    parameters: dict = Field(default_factory=lambda: {
        "type": "object",
        "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}},
        "required": ["a", "b"],
    })

    async def call(
        self, context: ContextWrapper[AstrAgentContext], **kwargs
    ) -> ToolExecResult:
        return str(kwargs["a"] + kwargs["b"])
```

让常规对话使用工具时在插件构造函数调用 `self.context.add_llm_tools(AddTool())`（>=4.5.1）。不要用已弃用的 `register_llm_tool()`。只有用户要修复旧接口时才处理其 `func_args` 字典列表兼容格式。

注册后还需核对模型工具调用能力、当前人格允许的工具和插件启用状态。

## Agent 循环（>=4.5.7）

```python
response = await self.context.tool_loop_agent(
    event=event,
    chat_provider_id=provider_id,
    prompt="计算 17 加 25。",
    tools=ToolSet([AddTool()]),
    max_steps=5,
    tool_call_timeout=20,
)
yield event.plain_result(response.completion_text)
```

显式设置与任务相称的步数和工具超时。确有多智能体需求时可把子 Agent 包装成 `FunctionTool`，在 `call()` 中通过 `context.context.context` 获取 AstrBot Context、`context.context.event` 获取事件，再调用自己的 `tool_loop_agent`。避免无界递归和重复使用不需要的工具。

## 对话和人格

`self.context.conversation_manager` 的常用异步方法：

- `get_curr_conversation_id(umo)` 返回当前 ID 或 `None`。
- `get_conversation(umo, cid, create_if_not_exists=False)` 返回对象或 `None`，历史字段为 JSON 字符串。
- `new_conversation(umo, ...)` 创建并切换；`switch_conversation(umo, cid)` 显式切换。
- `update_conversation(umo, cid, history=..., title=..., persona_id=...)` 更新指定字段。
- `add_message_pair(cid=..., user_message=..., assistant_message=...)` 追加成对消息。
- `delete_conversation(umo, cid)` 删除目标，`cid=None` 表示当前对话。

使用前处理不存在的当前对话和返回 `None`；不要为一次无状态模型调用意外新建、切换或清空用户对话。需要持久化模型输入输出时，按目标版本使用 `UserMessageSegment`、`AssistantMessageSegment`、`TextPart`，并验证写入范围。

`self.context.persona_manager` 提供 `get_persona`、`get_all_personas`、`create_persona`、`update_persona`、`delete_persona`。`tools=None` 表示全部工具，`tools=[]` 表示禁用全部，不能混淆。人格不存在时的返回/异常细节文档有不一致，调用前核对目标实现。不要为了临时请求修改用户的全局人格。
