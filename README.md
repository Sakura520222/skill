# AstrBot Plugin Development Skill

帮助 Claude Code、Codex 等编码 Agent 开发、修改和调试 AstrBot Python 插件的可分发技能。

基于 [AstrBot 官方插件开发文档](https://docs.astrbot.app/dev/star/plugin-new.html)，将 14 篇开发相关文档提炼为 10 份按需读取的参考资料，附带最小插件示例、固定来源提交和可复现打包工具。技能版本：**1.1.0**；文档快照：**2026-11-04**，固定到 [上游 f926af99](https://github.com/AstrBotDevs/AstrBot/commit/f926af99ec5f8bd85b64413f8bfad55da76ef73b)。

本轮补充交互按钮、Decision Provider 结构化判断、用户/会话选择器及 SSE 关闭通知。快照的 AstrBot 版本字段为 **4.29.4**，但包含该正式版发布后的主分支变化：SSE `onClose` 需包含 2026-11-01 的 bridge 更新；各项适用范围见参考资料，开发旧版插件时核对实际 API。

## 一键安装到 Claude Code 和 Codex

需要 **Node.js >=22.20**、npm/npx 和 Git。在终端运行：

```bash
npx --yes skills add Sakura520222/Astrbot-Skill --skill astrbot-plugin-dev --agent claude-code codex --global --copy --yes
```

一条命令为两个客户端安装用户级技能。`--copy` 使用复制模式，Windows 无需开启符号链接权限。安装器是 [Vercel Skills CLI](https://github.com/vercel-labs/skills)，技能内容直接从本 GitHub 仓库取得，无需单独发布 npm 包。

当前 Skills CLI 的默认安装位置：

| 客户端 | 用户级（`--global`） | 项目级（省略 `--global`） |
| --- | --- | --- |
| Claude Code | `~/.claude/skills/astrbot-plugin-dev/` | `.claude/skills/astrbot-plugin-dev/` |
| Codex | `~/.agents/skills/astrbot-plugin-dev/` | `.agents/skills/astrbot-plugin-dev/` |

`~` 指当前用户目录；具体路径遵循安装器与客户端的配置。规则参考 [Skills CLI 支持的 Agent](https://github.com/vercel-labs/skills/blob/main/docs/agents.md)、[Claude Code Skills](https://code.claude.com/docs/en/skills) 和 [Codex Skills](https://learn.chatgpt.com/docs/build-skills)。

仅为当前项目安装两个客户端：

```bash
npx --yes skills add Sakura520222/Astrbot-Skill --skill astrbot-plugin-dev --agent claude-code codex --copy --yes
```

只装一个客户端时，`--agent` 后保留 `claude-code` 或 `codex`。若想先查看仓库提供的技能：

```bash
npx --yes skills add Sakura520222/Astrbot-Skill --list
```

## 使用

Claude Code 中输入：

```text
/astrbot-plugin-dev 为 AstrBot 开发一个带配置项的群聊指令插件。
```

Codex 中输入：

```text
使用 $astrbot-plugin-dev，修复当前插件的 LLM 工具参数解析，并验证兼容性。
```

也可以直接描述 AstrBot 插件开发需求，由 Agent 按技能描述自动选择。安装后如客户端尚未刷新技能列表，重新打开会话。

## 覆盖内容

- 插件结构、metadata、开发环境与重载。
- 命令/指令组、事件过滤、权限和生命周期钩子。
- 被动回复、主动推送、富媒体、交互按钮与平台差异。
- 配置 Schema、用户/会话选择器、敏感字段、KV 和持久化文件。
- LLM 调用、Decision Provider、工具 schema、Agent、对话与人格。
- 多轮会话等待、取消、超时及会话隔离。
- 插件可视化视图、bridge、Web API、SSE 和国际化。
- 文转图、平台专用接口及插件发布。

入口见 [SKILL.md](skills/astrbot-plugin-dev/SKILL.md)。资料包含 API 的版本边界、官方来源和运行验证要求；技能不会安装 AstrBot 本体或模型服务。

## 更新与卸载

更新本技能（用户级）：

```bash
npx --yes skills update astrbot-plugin-dev --global --yes
```

卸载两个客户端中的本技能（用户级）：

```bash
npx --yes skills remove astrbot-plugin-dev --agent claude-code codex --global --yes
```

## 源码维护与分发包

```bash
python -m pip install -r requirements-dev.txt
python scripts/validate_skill.py
ruff check scripts tests skills/astrbot-plugin-dev/assets
ruff format --check scripts tests skills/astrbot-plugin-dev/assets
python -m unittest discover -s tests -v
python scripts/build.py
python scripts/smoke_install.py
```

维护脚本要求 Python >=3.12。最后一条在临时项目中执行真实的 npx 安装，再比对两个客户端目录的全部文件，不改动用户级技能。CI 固定使用 Skills CLI 1.7.4 进行安装回归验证；日常安装命令使用 npm 当前版本。

`dist/` 生成带单一 `astrbot-plugin-dev/` 顶层目录的 ZIP、同内容的 `.skill` 文件和 `SHA256SUMS.txt`，包含技能正文、参考资料、示例资产及许可声明。GitHub Actions 在 Windows 和 Linux 校验及安装，校验成功后提供分发包 artifact。直接克隆此仓库也可以使用 Skills CLI 从本地路径安装。

原始文档抓取和快照更新步骤见 [sources.md](skills/astrbot-plugin-dev/references/sources.md)，逐项来源与 Git blob SHA 见 [sources.json](skills/astrbot-plugin-dev/references/sources.json)。缓存不进入仓库或技能包；本仓库分发经过提炼的开发指导。

## 许可与来源

采用 **AGPL-3.0-or-later**，保留 AstrBot 原文及示例的来源归属。许可正文见 [LICENSE](LICENSE)，改写说明见 [NOTICE.txt](skills/astrbot-plugin-dev/NOTICE.txt)。这是社区整理的独立技能。
