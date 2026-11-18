# 配置与持久化

来源：[插件配置](https://docs.astrbot.app/dev/star/guides/plugin-config.html)、[插件存储](https://docs.astrbot.app/dev/star/guides/storage.html)。

## 自定义配置 Schema

插件根目录的 `_conf_schema.json` 是配置字段名到字段定义的映射，不是带 `properties` 的标准 JSON Schema：

```json
{
  "enabled": {"type": "bool", "description": "启用功能", "default": true},
  "api_key": {"type": "string", "description": "API Key", "default": "", "secret": true},
  "provider_id": {"type": "string", "description": "模型", "_special": "select_provider"},
  "connection": {
    "type": "object",
    "description": "连接配置",
    "items": {"timeout": {"type": "int", "description": "超时秒数", "default": 20}}
  }
}
```

每个字段必须有 `type`。文档支持 `string`、`text`、`int`、`float`、`bool`、`object`、`list`、`dict`、`template_list`；另有 `>=4.13.0` 的 `file`。

- `description`/`hint` 提供文案，`obvious_hint` 强调提示，`invisible` 隐藏字段。
- 配置保存 `options` 中的选项值，`labels`、`subtitles` 按索引提供展示名与说明。`list` 搭配 `options` 为多选，添加 `render_type: "checkbox"` 可显示复选框组。
- `slider` 仅用于 int/float，例如 `{"min": 1, "max": 60, "step": 1}`。
- `object.items` 为嵌套字段。自 `v4.30.0-alpha.1` 可给分组配置 `collapsed: true`，使 WebUI 默认收起，根对象不能折叠。`dict.template_schema` 提供可选的编辑模板。
- `template_list.templates` 为模板名到 `{name, items}` 的映射。保存后是对象列表，每个对象携带 `__template_key`。`display_item` 可指定列表标题使用的字符串字段（支持点号路径），`hide_hint_in_list` 控制折叠列表提示。
- `file` 配置使用 `default: []` 和 `file_types` 扩展名列表。JSON 不能携带文档示例中的 `//` 注释。
- `secret: true` 适用于字符串和字符串列表，只有 UI 遮罩效果，配置文件仍保存原值。不要打印整个配置或回显密钥。

可公开使用的 `_special`：`select_provider`、`select_provider_tts`、`select_provider_stt`、`select_persona` 返回字符串；`select_knowledgebase` 为多选，应配 `type: list`、`default: []`。用户和会话选择器见下节。不要把核心内部的 provider_pool 等选项当成插件稳定接口。

### 用户和会话来源选择器

以下选择器已在 `v4.29.4` 标签文档中确认；旧版本先核对支持情况：

```json
{
  "users": {
    "type": "list",
    "description": "指定用户",
    "default": [],
    "_special": "sender_id"
  },
  "source": {
    "type": "string",
    "description": "单个会话来源",
    "default": "",
    "_special": "umo"
  },
  "sources": {
    "type": "list",
    "description": "多个会话来源",
    "default": [],
    "_special": "umo"
  }
}
```

- `sender_id` 搜索已记录的用户，保存的只有用户 ID 列表，不含昵称或平台实例。候选按平台实例 ID 与用户 ID 去重；不要把列表值当成完整 UMO。
- `umo` 支持字符串单选、列表多选，保存完整会话来源，可用于主动推送和会话匹配。
- 用户候选在消息唤醒机器人时记录，不会补扫历史消息；可手动添加未记录的 ID 或 UMO。
- 两个选择器均支持 `readonly`。机器人页面组件的 `platformId` 过滤参数尚未向插件配置 schema 提供，不要自行添加该参数并假定它有效。

需要按平台或会话授权时，在业务处理处结合实际来源判断，不能因为用户选择器展示了平台，就假定保存值已经包含平台信息。

## 读取和保存

```python
from astrbot.api import AstrBotConfig
from astrbot.api.star import Context, Star


class ConfiguredPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config
```

存在 Schema 时，AstrBot 注入字典式 `AstrBotConfig`。读取例如 `self.config.get("enabled", True)`；必要的程序内配置修改可调用 `self.config.save_config()`。配置实体由 AstrBot 管理，文档给出的路径为 `data/config/<plugin_name>_config.json`，不要自行改写路径来绕过配置系统。

升级 Schema 时框架会递归补入缺失项、移除不存在的项。因此字段改名/删除可能丢失旧值；需要迁移时明确处理，不能假定旧字段永远保留。不要把持续增长的业务数据塞进配置。

## KV 存储（>=4.9.2）

插件继承的异步方法：

```python
await self.put_kv_data("enabled", True)
enabled = await self.get_kv_data("enabled", False)
await self.delete_kv_data("enabled")
```

KV 空间按插件隔离。会话/用户数据仍需在 key 中包含相应来源，例如 `f"preferences:{event.unified_msg_origin}"`，否则同插件的各会话会共享同一个值。读改写计数等操作需要考虑并发，不能假定三个独立异步调用组成事务。

## 文件

```python
from pathlib import Path
from astrbot.api.util import get_astrbot_plugin_data_path

data_dir = Path(get_astrbot_plugin_data_path()) / self.name
data_dir.mkdir(parents=True, exist_ok=True)
```

`v4.30.0-alpha.1` 提供上面的公开导入。`v4.29.4` 可从 `astrbot.core.utils.astrbot_path` 导入同名函数，更旧版本按其源码核对。`self.name` 要求 `>=4.9.2`，更早版本使用插件稳定名称。业务文件保存在该目录，插件自带静态模板可以留在代码目录。校验用户提供的文件名，并按并发需求选择锁、原子替换或数据库。
