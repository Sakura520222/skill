# 插件交付和市场发布

来源：[插件开发](https://docs.astrbot.app/dev/star/plugin-new.html)、[发布插件](https://docs.astrbot.app/dev/star/plugin-publish.html)、[市场规范 2026-06-27](https://docs.astrbot.app/dev/plugin-market/2026-06-27.html)。整理日期：2026-10-23。

## 插件仓库

准备 `main.py`、`metadata.yaml`、必要的 `_conf_schema.json`、第三方依赖声明及 README。README 描述安装、指令/工具、配置、平台限制、版本要求和外部服务，引用借鉴的项目并保留代码/资源许可。

```yaml
name: astrbot_plugin_example
display_name: 示例插件
desc: 提供示例功能。
version: 1.0.0
author: example-author
repo: https://github.com/example-author/astrbot_plugin_example
astrbot_version: ">=4.9.2,<5"
support_platforms:
  - aiocqhttp
```

示例值需要替换，最低版本按实际使用 API 决定，平台按真实支持范围声明。`short_desc`、`social_link`、`tags` 等为可选项。多行描述用合法 YAML 的 `|` 或 `>`，不要照抄可能缩进不完整的网页片段。

当前市场规范以 `author/name` 标识插件，展示名、安装目录名、repo URL 都不能替代身份；发布更新时保持身份稳定。版本与市场记录应一致。

## 文件与验收

官方发布文档限制插件 ZIP 不超过 16MB。排除 `.git`、虚拟环境、`__pycache__`、node_modules、运行日志、用户配置和数据。需要大资源时优先按需下载并校验，不能把用户环境一起打包。

验证新安装与重载、依赖安装环境、配置默认值和升级行为，以及实际命令/工具/平台收发。LLM 工具确认参数 schema 和模型调用；页面确认 bridge 与路由。静态解析通过不等于 AstrBot 已加载。

## 提交市场

用户授权后将插件推送至 GitHub，并在 [AstrBot Cloud 发布页](https://cloud.astrbot.app/publish) 提交；需要 AstrBot Cloud 账号。技能本身不提供该账号或替用户推定发布权限。

本技能指导开发的是 AstrBot 插件。技能自身通过 Skills CLI 安装与 AstrBot 插件市场提交流程是两个不同的分发入口。

## 可选的插件内置 Skills

插件可提供 `skills/<skill-name>/SKILL.md`；只有一个技能时也可直接 `skills/SKILL.md`，此时技能名称采用插件目录名。它们由插件文件管理，在 WebUI 插件的技能页启用/停用，随插件更新或卸载。不要让插件技能修改成为本地 Skills 页面可写的假设。
