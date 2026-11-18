# 来源与快照维护

本技能首次于 **2026-10-23** 从 AstrBot 官方插件开发文档整理，最新核对日期为 **2026-11-18**。文档站和代码仓库的发布时间有差异，新增的 AI 子页和视图指南可直接查固定提交的 Markdown。 [官方文档入口](https://docs.astrbot.app/dev/star/plugin-new.html)

固定参考为 `AstrBotDevs/AstrBot` 主分支提交 `06fc50b43ea1c13093c91762f3b9361911362f9a`。项目版本字段为 **4.30.0-alpha.1**，Python 要求为 **>=3.12**。 [固定提交](https://github.com/AstrBotDevs/AstrBot/commit/06fc50b43ea1c13093c91762f3b9361911362f9a)

| 上游版本 | 插件能力 |
| --- | --- |
| [v4.29.4](https://github.com/AstrBotDevs/AstrBot/releases/tag/v4.29.4) | 已有消息按钮、判断提供商和用户/会话选择器 |
| [v4.30.0-alpha.1](https://github.com/AstrBotDevs/AstrBot/releases/tag/v4.30.0-alpha.1) | 包含 Agent Runtime、对话事件存储、新公开导入、分组默认折叠、SSE `onClose` 与主题色 |
| [Alpha 标签后的快照](https://github.com/AstrBotDevs/AstrBot/compare/v4.30.0-alpha.1...06fc50b43ea1c13093c91762f3b9361911362f9a) | 增加 `view_result`、`ui_action`、消息卡片及工作台。项目版本字段沿用 Alpha 的值 |

## 覆盖

官方 AI 指南已拆分为模型、工具、Agent、对话和人格。原可视化视图入口已拆分为独立页面、消息组件、工作台、共享 Bridge 和 Web API。清单记录新旧入口、公开模块与实现路径，便于核对兼容性。

旧的单篇 `plugin.md` 仅作为历史兼容入口，不将其过时示例混入新 API 指导。没有抓取部署、模型接入、HTTP OpenAPI 或平台适配器开发的整站文档；需要这些任务时查看对应官方资料。

[sources.json](sources.json) 逐项记录原文路径、网页 URL、固定提交源码 URL、Git blob SHA 以及对应参考文件。参考文件是面向开发任务的摘要与改写，包含必要的代码示例，不是原文镜像。阅读某一个参考文件即可追溯到其页首列出的官方来源。

## 更新

在技能的 GitHub 源码仓库中，维护者可以运行：

```bash
python scripts/fetch_sources.py --output .cache/current-sources
python scripts/fetch_sources.py --ref master --output .cache/latest-sources
```

第一条按本技能的固定提交抓取并校验 Git blob；第二条将分支解析为提交后抓取同一组来源。脚本只写入指定的新缓存目录，不覆盖本技能参考资料。缓存中包含原始文件与新的来源清单，便于比较。

确认 API 变化后手工更新相关摘要、最低版本和示例，再同步来源清单、日期及技能版本，运行仓库检查。新增官方章节时也更新来源清单及路由；不要机械追加整本手册到 `SKILL.md`。

分发许可见 [LICENSE.txt](../LICENSE.txt) 和 [NOTICE.txt](../NOTICE.txt)。
