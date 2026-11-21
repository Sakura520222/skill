# skill

面向 Claude Code、Codex 等编码 Agent 的通用技能仓库，用于收集、维护和分发不同领域的可复用 Skill。

仓库地址：[sakura520222/skill](https://github.com/sakura520222/skill)。每个技能独立存放在 `skills/<技能名>/` 中，可按需安装和使用；后续新增技能也沿用这一结构。

## 技能目录

| 技能 | 用途 | 入口 |
| --- | --- | --- |
| `astrbot-plugin-dev` | 开发、修改和调试 AstrBot Python 插件 | [SKILL.md](skills/astrbot-plugin-dev/SKILL.md) |
| `miuix-guidance` | 接入、使用、迁移和调试 Compose / KMP 的 Miuix UI | [SKILL.md](skills/miuix-guidance/SKILL.md) |
| `napcat-api-dev` | 查阅 NapCat API，开发调试 OneBot 对接、NapCat 插件与 WebUI | [SKILL.md](skills/napcat-api-dev/SKILL.md) |

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

基于 AstrBot 官方插件开发文档，附带按需读取的参考资料、最小插件示例、固定来源提交和可复现打包工具。技能 **1.3.0** 的文档快照于 **2026-11-21** 核对，固定到 `v4.30.0-beta.1`。 [上游 90ba3270](https://github.com/AstrBotDevs/AstrBot/commit/90ba3270f09b857063da68908d80f742042067cd)

Agent Runtime、对话事件存储和新版公开导入自 `v4.30.0-alpha.1` 起可用。`v4.30.0-beta.1` 包含 ChatUI 交互卡片、工作台和追加输入时将工具调用转入后台的能力。参考资料保留 `v4.29.4` 等旧版的兼容接口。 [Beta 发布记录](https://github.com/AstrBotDevs/AstrBot/releases/tag/v4.30.0-beta.1)

覆盖内容：

- 插件结构、metadata、开发环境与重载。
- 命令/指令组、事件过滤、权限和生命周期钩子。
- 被动回复、主动推送、富媒体、交互按钮与平台差异。
- 配置 Schema、用户/会话选择器、敏感字段、KV 和持久化文件。
- LLM 调用、Decision Provider、工具 schema、Agent、对话与人格。
- 多轮会话等待、取消、超时及会话隔离。
- 独立插件页面、ChatUI 消息卡片与工作台、bridge、Web API、SSE 和国际化。
- 文转图、平台专用接口及插件发布。

入口见 [SKILL.md](skills/astrbot-plugin-dev/SKILL.md)。资料包含 API 的版本边界、官方来源和运行验证要求；技能不会安装 AstrBot 本体或模型服务。

## miuix-guidance

提供 Miuix 的依赖选择、主题、设置页、弹层、导航、图标及模糊 / 玻璃 / 连续圆角指导。技能 **1.2.0** 的快照于 **2026-11-21** 核对，固定到已发布的 `0.9.5-beta03`。 [上游 3526cfe2](https://github.com/compose-miuix-ui/miuix/commit/3526cfe2ca0779c5a2eab99af8737a96c9a8a885) · [Beta 发布记录](https://github.com/compose-miuix-ui/miuix/releases/tag/v0.9.5-beta03)

保留稳定版 `0.9.4` 的依赖选择，补充 Beta 的玻璃输入框与搜索浮层、滚动条和桌面窗口回调迁移，以及 Compose Multiplatform `1.13.0-rc01` 和 Android Blur 的 API 33 要求。

安装到两个客户端：

```bash
npx --yes skills add sakura520222/skill --skill miuix-guidance --agent claude-code codex --global --copy --yes
```

在本仓库尚未推送新技能时，先在仓库根目录把上述来源改为 `.`，即可从本地安装。

调用示例：

```text
使用 $miuix-guidance，为当前 Compose 项目实现支持深色模式的 Miuix 设置页，保留现有导航和状态管理。
```

Claude Code 可使用 `/miuix-guidance`。入口见 [SKILL.md](skills/miuix-guidance/SKILL.md)，来源与维护步骤见 [sources.md](skills/miuix-guidance/references/sources.md)。

## napcat-api-dev

基于 [NapCatQQ 官方仓库](https://github.com/NapNeko/NapCatQQ)与[官方文档](https://napneko.github.io/guide/start-install)，提供按版本查询 API、HTTP / 正反向 WebSocket 对接、消息与事件、文件流、NapCat JS / TS 插件、WebUI 和源码定位指导。技能版本：**1.0.0**；资料整理日期：**2026-11-12**。

文档固定到 NapCatDocs `90399c46`，实现核对固定到 NapCatQQ `72912f29`，另记录文档中的 `4.18.42` OpenAPI。三者不视为同一个发布版本；使用时以实际 NapCat 版本为准。包含文档与实现差异说明，不附带 NapCat 本体代码，也不安装或启动 QQ。

安装到两个客户端：

```bash
npx --yes skills add sakura520222/skill --skill napcat-api-dev --agent claude-code codex --global --copy --yes
```

新技能尚未推送时，在仓库根目录将来源 `sakura520222/skill` 改为 `.` 可从本地安装。

调用示例：

```text
使用 $napcat-api-dev，按当前 NapCat 版本实现反向 WebSocket 对接，正确分流 API 响应和消息事件，并验证断线恢复。
```

Claude Code 可使用 `/napcat-api-dev`。入口见 [SKILL.md](skills/napcat-api-dev/SKILL.md)，来源与维护步骤见 [sources.md](skills/napcat-api-dev/references/sources.md)。该技能涵盖 NapCat 内嵌插件；AstrBot Python 插件开发仍使用 `astrbot-plugin-dev`。

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

维护脚本保留 `astrbot-plugin-dev` 为默认目标，也支持显式选择技能。CI 在 Windows 和 Linux 分别校验、安装及打包三个技能；Python 示例会做语法检查，Kotlin 示例仍需在实际消费项目中编译验证。NapCat 技能的资料校验不代表完成真实 QQ 收发验证。

```bash
python -m pip install -r requirements-dev.txt
python scripts/validate_skill.py
ruff check scripts tests skills/astrbot-plugin-dev/assets
ruff format --check scripts tests skills/astrbot-plugin-dev/assets
python -m unittest discover -s tests -v
python scripts/build.py
python scripts/smoke_install.py
```

校验和打包 Miuix 技能：

```bash
python scripts/validate_skill.py skills/miuix-guidance
python scripts/build.py --skill skills/miuix-guidance --output dist/miuix-guidance
python scripts/smoke_install.py --skill skills/miuix-guidance
```

校验和打包 NapCat 技能：

```bash
python scripts/validate_skill.py skills/napcat-api-dev
python scripts/build.py --skill skills/napcat-api-dev --output dist/napcat-api-dev
python scripts/smoke_install.py --skill skills/napcat-api-dev
```

维护脚本要求 Python >=3.12。最后一条在临时项目中执行真实的 npx 安装，再比对两个客户端目录的全部文件，不改动用户级技能。CI 固定使用 Skills CLI 1.7.4 进行安装回归验证；日常安装命令使用 npm 当前版本。

打包命令在指定输出目录生成带单一技能名顶层目录的 ZIP、同内容的 `.skill` 文件和 `SHA256SUMS.txt`，包含技能正文、参考资料、该技能的资产及许可声明。默认仍打包 AstrBot 到 `dist/`；同时打包多个技能时，为每个技能指定独立输出子目录，避免校验清单互相覆盖。GitHub Actions 校验成功后提供各技能的分发包 artifact。直接克隆此仓库也可以使用 Skills CLI 从本地路径安装。

原始文档抓取和快照更新步骤见 [sources.md](skills/astrbot-plugin-dev/references/sources.md)，逐项来源与 Git blob SHA 见 [sources.json](skills/astrbot-plugin-dev/references/sources.json)。缓存不进入仓库或技能包；本仓库分发经过提炼的开发指导。

## 许可与来源

本仓库采用 **AGPL-3.0-or-later**，许可正文见 [LICENSE](LICENSE)。各技能引用或改写第三方资料时须保留原有来源归属和许可声明。

`astrbot-plugin-dev` 保留 AstrBot 原文及示例的来源归属，改写说明见 [NOTICE.txt](skills/astrbot-plugin-dev/NOTICE.txt)。这是社区整理的独立技能。

`miuix-guidance` 保留 Miuix 的 Apache-2.0 来源归属和许可正文，改写说明见 [NOTICE.txt](skills/miuix-guidance/NOTICE.txt)。重新整理的技能遵循本仓库许可，不包含上游字体或图标二进制。

`napcat-api-dev` 保留 NapCatDocs 的 MIT 来源归属和许可正文，说明见 [NOTICE.txt](skills/napcat-api-dev/NOTICE.txt)。NapCatQQ 本体使用自定义及混合许可，技能未复制其实现，不能将本仓库许可视为上游源码的许可。
