# 来源与快照维护

本技能首次于 **2026-10-23** 从 [AstrBot 官方插件开发文档](https://docs.astrbot.app/dev/star/plugin-new.html) 及其导航中的新开发指南整理，最新核对日期为 **2026-11-04**。开发文档入口使用 `.html` 地址。

文档的“在 GitHub 上编辑”链接指向 `AstrBotDevs/AstrBot` 仓库的 `docs/zh/`，因此使用该官方仓库的 Markdown 原文核对代码和版本。当前固定到主分支提交 [f926af99ec5f8bd85b64413f8bfad55da76ef73b](https://github.com/AstrBotDevs/AstrBot/commit/f926af99ec5f8bd85b64413f8bfad55da76ef73b)，其项目版本字段为 **4.29.4**，Python 要求为 **>=3.12**。

快照包含正式版之后的文档更新，不能据项目版本字段推定所有接口均在正式版存在。对照发布标签 [v4.29.4（61335414）](https://github.com/AstrBotDevs/AstrBot/tree/61335414433db721b3f7ecc93f90deafe0a59d78)，按钮、判断提供商与选择器已出现在该标签文档中；SSE `onClose` 来自发布后的 [15e1b999](https://github.com/AstrBotDevs/AstrBot/commit/15e1b9996e94fad780bc207393ea13506d64b49e)，需目标实例包含这一后续实现。面向旧版插件时以用户实际环境为准。

## 覆盖

共提炼 14 篇开发相关文档：入门、最小实例、接收消息、发送消息、配置、可视化视图、国际化、AI、存储、文转图、会话控制、杂项、插件发布及市场规范。另核对 `pyproject.toml` 与 `LICENSE`。

相较初始的 `0cd42bd4` 快照，4 篇文档变化已同步到 `messaging.md`、`ai-tools.md`、`config-storage.md` 和 `web-views.md`；其余 10 篇文档内容未变化。

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
