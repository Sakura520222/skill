# skill

面向 Claude Code、Codex 等编码 Agent 的通用技能仓库，用于收集、维护和分发不同领域的可复用 Skill。

仓库地址：[sakura520222/skill](https://github.com/sakura520222/skill)。每个技能独立存放在 `skills/<技能名>/` 中，可按需安装和使用；后续新增技能也沿用这一结构。

## 技能目录

| 技能 | 用途 | 入口 |
| --- | --- | --- |
| `astrbot-plugin-dev` | 开发、修改和调试 AstrBot Python 插件 | [SKILL.md](skills/astrbot-plugin-dev/SKILL.md) |

当前收录上述技能。仓库可继续加入开发、工具使用及其他工作流相关技能。

## 一键安装到 Claude Code 和 Codex

需要 **Node.js >=22.20**、npm/npx 和 Git。先查看可安装的技能：

```bash
npx --yes skills add sakura520222/skill --list
```

按名称安装所需技能，以下以 `astrbot-plugin-dev` 为例；安装其他技能时，将 `--skill` 后的名称替换为技能目录中的对应名称：

```bash
npx --yes skills add sakura520222/skill --skill astrbot-plugin-dev --agent claude-code codex --global --copy --yes
```

一条命令为两个客户端安装用户级技能。`--copy` 使用复制模式，Windows 无需开启符号链接权限。安装器是 [Vercel Skills CLI](https://github.com/vercel-labs/skills)，技能内容直接从本 GitHub 仓库取得，无需单独发布 npm 包。

Skills CLI 的默认安装位置（`<技能名>` 对应所选技能）：

| 客户端 | 用户级（`--global`） | 项目级（省略 `--global`） |
| --- | --- | --- |
| Claude Code | `~/.claude/skills/<技能名>/` | `.claude/skills/<技能名>/` |
| Codex | `~/.agents/skills/<技能名>/` | `.agents/skills/<技能名>/` |

`~` 指当前用户目录；具体路径遵循安装器与客户端的配置。规则参考 [Skills CLI 支持的 Agent](https://github.com/vercel-labs/skills/blob/main/docs/agents.md)、[Claude Code Skills](https://code.claude.com/docs/en/skills) 和 [Codex Skills](https://learn.chatgpt.com/docs/build-skills)。

仅为当前项目安装两个客户端：

```bash
npx --yes skills add sakura520222/skill --skill astrbot-plugin-dev --agent claude-code codex --copy --yes
```

只装一个客户端时，`--agent` 后保留 `claude-code` 或 `codex`。

## 使用

在请求中指定技能名称，或描述任务让 Agent 按技能描述选择。以 `astrbot-plugin-dev` 为例，Claude Code 中输入：

```text
/astrbot-plugin-dev 为 AstrBot 开发一个带配置项的群聊指令插件。
```

Codex 中输入：

```text
使用 $astrbot-plugin-dev，修复当前插件的 LLM 工具参数解析，并验证兼容性。
```

各技能的适用任务、使用步骤和限制见对应 `SKILL.md`。安装后如客户端尚未刷新技能列表，重新打开会话。

## astrbot-plugin-dev

基于 [AstrBot 官方插件开发文档](https://docs.astrbot.app/dev/star/plugin-new.html)，附带按需读取的参考资料、最小插件示例、固定来源提交和可复现打包工具。技能版本：**1.1.0**；文档快照：**2026-11-04**，固定到 [上游 f926af99](https://github.com/AstrBotDevs/AstrBot/commit/f926af99ec5f8bd85b64413f8bfad55da76ef73b)。

快照的 AstrBot 版本字段为 **4.29.4**，但包含该正式版发布后的主分支变化：SSE `onClose` 需包含 2026-11-01 的 bridge 更新；各项适用范围见参考资料，开发旧版插件时核对实际 API。

覆盖内容：

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

以 `astrbot-plugin-dev` 为例，更新已安装的技能（用户级）：

```bash
npx --yes skills update astrbot-plugin-dev --global --yes
```

卸载两个客户端中的指定技能（用户级）：

```bash
npx --yes skills remove astrbot-plugin-dev --agent claude-code codex --global --yes
```

其他技能使用对应名称替换命令中的 `astrbot-plugin-dev`。

## 仓库结构与新增技能

```text
skills/
  <技能名>/
    SKILL.md       # 技能入口：名称、描述和操作指导
    agents/        # 可选的 Agent 元数据
    references/    # 可选的按需读取资料
    scripts/       # 可选的技能辅助脚本
    assets/        # 可选的模板、示例和其他资源
scripts/           # 仓库维护与分发工具
tests/             # 维护工具的测试
```

新增技能时：

1. 在 `skills/` 下创建独立目录，目录名使用小写字母、数字和连字符。
2. 编写 `SKILL.md`，在 YAML frontmatter 中设置与目录名一致的 `name`，并通过 `description` 说明何时使用该技能。
3. 将该技能所需的参考资料、脚本和资产放在自身目录内，使用可移植的相对路径，记录来源和许可。
4. 更新本 README 的技能目录，补充必要的验证，并检查技能发现和安装结果。

## 源码维护与分发包

现有维护脚本和 CI 针对 `astrbot-plugin-dev`，包含其上游文档来源及示例校验。新增技能时应按自身需求扩展验证与打包流程。

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

当前打包命令在 `dist/` 生成带单一 `astrbot-plugin-dev/` 顶层目录的 ZIP、同内容的 `.skill` 文件和 `SHA256SUMS.txt`，包含技能正文、参考资料、示例资产及许可声明。GitHub Actions 在 Windows 和 Linux 校验及安装，校验成功后提供分发包 artifact。直接克隆此仓库也可以使用 Skills CLI 从本地路径安装。

原始文档抓取和快照更新步骤见 [sources.md](skills/astrbot-plugin-dev/references/sources.md)，逐项来源与 Git blob SHA 见 [sources.json](skills/astrbot-plugin-dev/references/sources.json)。缓存不进入仓库或技能包；本仓库分发经过提炼的开发指导。

## 许可与来源

本仓库采用 **AGPL-3.0-or-later**，许可正文见 [LICENSE](LICENSE)。各技能引用或改写第三方资料时须保留原有来源归属和许可声明。

`astrbot-plugin-dev` 保留 AstrBot 原文及示例的来源归属，改写说明见 [NOTICE.txt](skills/astrbot-plugin-dev/NOTICE.txt)。这是社区整理的独立技能。
