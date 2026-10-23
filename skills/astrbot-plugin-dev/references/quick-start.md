# 起步、结构和生命周期

来源：[开发指南](https://docs.astrbot.app/dev/star/plugin-new.html)、[最小实例](https://docs.astrbot.app/dev/star/guides/simple.html)。整理日期：2026-10-23。

## 项目与版本

官方模板为 [Soulter/helloworld](https://github.com/Soulter/helloworld)。插件推荐使用小写 `astrbot_plugin_` 前缀，名称不含空格。插件开发目录通常是 `AstrBot/data/plugins/<插件目录>/`；单独的插件仓库也可以作为该目录的工作副本。

先检查用户已有 AstrBot 部署与 Python 版本，再决定如何连接开发环境。快照中 AstrBot `pyproject.toml` 声明 Python `>=3.12`；这不是所有历史版本的要求。调试需要 AstrBot 本体的运行环境，直接执行插件 `main.py` 不能模拟运行时注入。

最小文件：

```text
astrbot_plugin_example/
  main.py
  metadata.yaml
  _conf_schema.json      # 需要可配置项时添加
  requirements.txt      # 有第三方依赖时添加
```

[示例资产](../assets/astrbot_plugin_example/) 可直接复制到开发实例的 `data/plugins/astrbot_plugin_example/`。其中 `/skill_ping` 回复配置中的问候语与发送者名称。使用前修改插件 `name`、`display_name`、作者、仓库地址以及类名/指令，避免与其他插件冲突；示例仓库地址是模板占位值。已有插件请只取需要的片段。

## 入口和 handler

```python
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star


class HelloPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    @filter.command("hello")
    async def hello(self, event: AstrMessageEvent):
        """向发送者问好。"""
        yield event.plain_result(f"你好，{event.get_sender_name()}！")
```

普通消息 handler 的前两个参数为 `self`、`event`；将业务服务拆到其他模块也应保留类内的注册入口。显式导入 `filter`，避免误用 Python 内置同名函数。当前官方最小实例不要求 `@register` 类装饰器，不要在新插件中凭旧教程添加冗余注册。

## 元数据

`metadata.yaml` 是插件识别依据。通常填写 `name`、`desc`、`version`、`author`、`repo`，可选 `display_name`、`short_desc`、`astrbot_version`、`support_platforms` 等。`version` 使用语义化版本；`astrbot_version` 使用不带 `v` 的 PEP 440 表达式，例如 `">=4.9.2,<5"`。

`name` 和 `author` 属于包身份，不随展示文案改变；多语言展示使用单独的 i18n 文件。平台声明使用适配器 key，例如 QQ 的 OneBot v11 是 `aiocqhttp`，不是 `napcat`。只声明真正测试/支持的平台。

可选 `logo.png` 保持 1:1，官方建议 256×256。第三方 Python 依赖放在插件根目录的 `requirements.txt` 中，必须安装到 AstrBot 实际运行环境。

## 生命周期与重载

构造函数调用 `super().__init__(context)`；有 `_conf_schema.json` 时接收 `config: AstrBotConfig`，见 [配置与存储](config-storage.md)。不要在构造函数内运行阻塞网络操作。

可实现 `async def terminate(self)` 清理插件创建的客户端、定时器和后台任务。创建任务时保留句柄，卸载时取消并等待结束；不要取消 AstrBot 或其他插件的任务。异步初始化入口按目标版本的 `Star` 类确认。

修改代码后在 WebUI 的插件卡片重载；加载失败时在失败插件列表中重载。确认配置更新与后台任务不会因反复重载而重复注册或遗留。发布要求另见 [publishing.md](publishing.md)。
