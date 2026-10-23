# 回复、主动消息与媒体

来源：[消息的发送](https://docs.astrbot.app/dev/star/guides/send-message.html)。整理日期：2026-10-23。

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
