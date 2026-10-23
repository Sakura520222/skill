# 文转图与平台专用接口

来源：[文转图](https://docs.astrbot.app/dev/star/guides/html-to-pic.html)、[杂项](https://docs.astrbot.app/dev/star/guides/other.html)。整理日期：2026-10-23。

## 文本与 HTML 渲染

在插件 handler 内：

```python
url = await self.text_to_image("需要渲染的文本")
yield event.image_result(url)
```

`return_url=False` 可请求本地结果。自定义样式用 HTML + Jinja2：

```python
template = "<h1>{{ title }}</h1><ul>{% for x in items %}<li>{{ x }}</li>{% endfor %}</ul>"
url = await self.html_render(
    template,
    {"title": "待办", "items": ["检查加载日志", "测试指令"]},
    options={"type": "png", "full_page": True},
)
yield event.image_result(url)
```

options 参考 Playwright screenshot 参数：`timeout`、`type`、`quality`、`omit_background`、`full_page`、`clip`、`animations`、`caret`、`scale`。`quality` 用于 JPEG，透明背景用于 PNG。不要把不可信用户文本拼接成可执行模板；作为数据传入，并按需求验证转义行为。

可用官方 [Text2Image Playground](https://t2i-playground.astrbot.app/) 编辑模板。运行验证需要目标实例的渲染服务；缺少渲染环境时不能只凭 HTML 语法保证效果。

## 当前平台实例

`>=4.0.0` 使用 `platform_id = event.get_platform_id()`，再 `self.context.get_platform_inst(platform_id)`。不要按适配器类型假定只存在一个连接；旧 `get_platform(...)` 是兼容路径。

加载的插件用 `self.context.get_all_stars()` 获取 `StarMetadata`；加载的平台可经 `self.context.platform_manager.get_insts()`，后者是较紧耦合的内部路径，先确认目标实现。

## OneBot / NapCat

先判断 `event.get_platform_name() == "aiocqhttp"`，再按需导入 `AiocqhttpMessageEvent` 并校验事件类型。文档给出的底层调用方式为：

```python
from astrbot.core.platform.sources.aiocqhttp.aiocqhttp_message_event import (
    AiocqhttpMessageEvent,
)

if isinstance(event, AiocqhttpMessageEvent):
    result = await event.bot.api.call_action(
        "delete_msg", message_id=event.message_obj.message_id
    )
```

这段展示的是删除当前消息的协议调用，只有用户确实要求删除消息时才执行。其他平台不支持该能力时应明确返回限制，而不是伪造成功。具体 action、参数、权限和返回值查用户实际协议端的当前文档，如 [NapCat API](https://napcat.apifox.cn/)；不要把 OneBot 标准和 NapCat 扩展混成一个稳定接口。
