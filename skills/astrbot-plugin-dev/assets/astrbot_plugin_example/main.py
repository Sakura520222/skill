"""Minimal configurable AstrBot plugin; replace its identity before publishing."""

from astrbot.api import AstrBotConfig
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star


class ExamplePlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config

    @filter.command("skill_ping")
    async def ping(self, event: AstrMessageEvent):
        """回复可配置的问候语，用于确认插件已加载。"""
        greeting = self.config.get("greeting", "你好")
        yield event.plain_result(f"{greeting}，{event.get_sender_name()}！")
