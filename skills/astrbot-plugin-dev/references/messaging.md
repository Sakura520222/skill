# 回复、主动消息与媒体

来源：[消息的发送](https://docs.astrbot.app/dev/star/guides/send-message.html)。

## 回复当前事件

在普通消息 handler 中：

```python
yield event.plain_result("处理完成")
yield event.image_result("https://example.com/result.png")
```

本地图片也可传文件路径；URL 必须以 `http://` 或 `https://` 开头。钩子/等待回调中改用 `await event.send(result)`。多次 `yield` 是多条消息；要保留一条消息内部的段顺序则构建消息链。

```python
import astrbot.api.message_components as Comp

chain = [
    Comp.Plain("结果："),
    Comp.Image.fromURL("https://example.com/result.png"),
    Comp.Plain("处理完毕。"),
]
yield event.chain_result(chain)
```

按实际平台确认 @ 和媒体支持；`Comp.At(qq=event.get_sender_id())` 是官方示例中的提及写法，不能据此保证所有平台行为一致。

## 主动推送

```python
from astrbot.api.event import MessageChain

origin = event.unified_msg_origin
message = MessageChain().message("任务完成")
await self.context.send_message(origin, message)
```

延迟/定时推送时保存完整 `unified_msg_origin`，执行时重新构造消息链，避免长期持有整份事件对象。部分平台限制主动消息；方法返回或请求成功也不一定等于平台已送达，应按适配器验证。跨平台群号可能重复，不要自行拼接/截断来源字符串。

## 交互按钮

按钮 API 已在 `v4.29.4` 标签文档中确认；旧版本先核对消息组件及 `filter.button_action` 是否存在。`ActionRow` 是独立消息组件，使用 `buttons` 包装 `Button`，不能把按钮当作普通文本段或命令参数。

以下三个方法放在 `Star` 子类中：

```python
from astrbot.api.event import AstrMessageEvent, filter
import astrbot.api.message_components as Comp


@filter.command("example_buttons")
async def example_buttons(self, event: AstrMessageEvent):
    yield event.chain_result([
        Comp.Plain("请选择操作："),
        Comp.ActionRow(
            buttons=[
                Comp.Button(
                    id="astrbot_plugin_example:confirm",
                    label="确认",
                    action=Comp.Button.CallbackAction(data={"item_id": 42}),
                    style=Comp.Button.Style.PRIMARY,
                ),
                Comp.Button(
                    id="astrbot_plugin_example:docs",
                    label="文档",
                    action=Comp.Button.UrlAction(url="https://docs.astrbot.app"),
                ),
            ],
            action_timeout=60,
            fallback_text="当前平台不支持按钮，请使用 /example_confirm 42。",
        ),
    ])


@filter.button_action("astrbot_plugin_example:confirm")
async def confirm(self, event: AstrMessageEvent):
    interaction = event.get_button_interaction()
    if interaction is None:
        return
    yield event.plain_result(f"收到确认：{interaction.data['item_id']}")


@filter.command("example_confirm")
async def confirm_text(self, event: AstrMessageEvent, item_id: int):
    yield event.plain_result(f"收到确认：{item_id}")
```

按钮 ID 使用插件名前缀以避免冲突；未指定 ID 的 `@filter.button_action()` 会匹配全部按钮回调。回调动作的 `data` 必须能 JSON 序列化，通过 `interaction.data` 读取，动作 ID 为 `interaction.action_id`。链接动作仅打开 URL，不进入回调。

`action_timeout` 是一行回调按钮的有效秒数，必须为有限正数；`None` 表示不限时。计时从首次渲染发送开始，同一行共享截止时间，重启保留截止时间。复用同一个 `ActionRow` 实例不会续期，重新计时应创建新实例。过期点击不执行插件 handler；已受理的操作仍可完成，原消息中的按钮也可能继续显示。URL 动作不受此超时限制，`fallback_text` 不是过期提示。

| 支持情况 | 平台 |
| --- | --- |
| 回调和链接按钮 | QQ 官方、Telegram、Discord、Slack、飞书、钉钉、LINE、KOOK、Satori、企业微信（含微信客服及 AI Bot）、WebChat |
| 回调按钮；URL 显示为普通链接 | Mattermost，需要协议端可访问的回调地址 |
| 仅文字/链接回退，不触发按钮回调 | OneBot v11（NapCat/aiocqhttp）、Misskey、微信公众号、微信个人号（weixin_oc） |

Satori 还受下游平台和客户端能力限制。需要兼容回退平台时，将同一业务能力接入 `fallback_text` 中可用的文字指令，如示例中的 `/example_confirm 42`。回调修改业务数据前按需求核验操作者和对象，处理重复点击；有效期不等于一次性执行保证。

QQ 官方按钮回调回复含媒体时，`v4.30.0-alpha.1` 已包含适配器的媒体保留修复。旧实例出现纯文本回复时，先核对该修复是否存在，并分别验证群聊、私聊或频道等实际场景。 [上游修复 #10903](https://github.com/AstrBotDevs/AstrBot/pull/10903)

## 媒体构造

| 内容 | 构造方式与限制 |
| --- | --- |
| 本地图片 | `Comp.Image.fromFileSystem("/absolute/path/result.png")` |
| 文件 | `Comp.File(file="/absolute/path/report.txt", name="report.txt")`；部分平台不支持 |
| 语音 | `Comp.Record(file=path, url=path)`；文档示例要求 WAV，其他格式先核对/转换 |
| 本地视频 | `Comp.Video.fromFileSystem(path=path)` |
| 远程视频 | `Comp.Video.fromURL(url="https://example.com/video.mp4")` |
| 合并转发 | `Comp.Node(uin=123456, name="示例", content=[Comp.Plain("内容")])`；文档标注 OneBot v11 |

本地媒体路径必须对协议端可见。AstrBot 和 NapCat 位于不同容器/机器时不能假定文件共享；使用双方可访问的 URL 或按部署设计共享路径，并实际验证收发。

aiocqhttp 对纯文本发送会去除首尾空白；仅在排版确实依赖这些空白时考虑文档的零宽空格方案。不要把平台差异做成所有消息都加特殊字符的通用规则。
