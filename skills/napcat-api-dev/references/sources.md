# 来源、版本与维护

快照整理日期：2026-11-12。技能版本：1.0.0。资料以官方文档为入口，并核对关键接口实现；未连接 QQ 账号或运行 NapCat 实例。

| 来源 | 固定提交 / 版本 | 清单 |
| --- | --- | --- |
| [NapCatDocs](https://github.com/NapNeko/NapCatDocs) | `90399c468599fb28fe4c426e4444844ba9f89548` | [sources.json](sources.json) |
| [NapCatQQ](https://github.com/NapNeko/NapCatQQ) | `72912f293924f43463b5976b01fc094a8ae11481` | [sources-implementation.json](sources-implementation.json) |
| 文档内 OpenAPI | `4.18.42`，属于上述文档提交 | 主清单中的 `src/api/4.18.42/openapi.json` |

清单逐项记录文件路径、不可变 source URL、Git blob SHA 和参考资料映射。主分支快照、OpenAPI 版本和用户运行版本相互独立，不声明本技能覆盖所有 release，也不把主分支新增 API 自动归入 4.18.42。

## 官方入口

- [用户指定的安装导航](https://napneko.github.io/guide/start-install)
- [基础配置](https://napneko.github.io/config/basic)
- [版本化 API](https://napneko.github.io/api/)
- [插件开发](https://napneko.github.io/develop/plugin/index)
- [插件类型参考](https://napneko.github.io/develop/plugin/api/type)
- [源码仓库](https://github.com/NapNeko/NapCatQQ)

在线页面可能晚于或早于固定快照。参数冲突时读取目标版本 schema 和真实校验路径；明确记录采用的版本，不静默混合。已核对的差异包括 HTTP 角色描述、群文件 URL 的 `group_id` 参数、HTTP 的 WS 支持和插件 action helper 的返回值，分别说明在对应参考资料中。

## 在技能仓库中复核来源

以下命令在 `sakura520222/skill` 仓库根目录执行，使用仓库维护工具，不是安装后的技能运行依赖。目标缓存目录必须不存在或为空：

```bash
python scripts/fetch_sources.py --manifest skills/napcat-api-dev/references/sources.json --output .cache/napcat-docs-verify
python scripts/fetch_sources.py --manifest skills/napcat-api-dev/references/sources-implementation.json --output .cache/napcat-code-verify
```

脚本校验下载字节的 Git blob SHA；缓存不进入分发包。更新时分别为两个清单使用 `--ref <目标提交或标签>` 和新的输出目录，审阅相关差异，再更新引用及清单。不要只替换 commit 和日期而保留未经重新核对的说明。若只更新一个上游，也重新确认另一清单仍是本轮采用的来源；`snapshot_date` 是共同的整理日期。

维护验证：

```bash
python scripts/validate_skill.py skills/napcat-api-dev
python -m unittest discover -s tests -v
python scripts/build.py --skill skills/napcat-api-dev --output dist/napcat-api-dev
python scripts/smoke_install.py --skill skills/napcat-api-dev
```

校验覆盖主清单及 `sources-*.json` 的不可变提交、blob 格式、日期和引用映射。安装检查使用临时项目，比较 Claude Code 与 Codex 的完整文件；不会给当前用户安装技能，也不部署 NapCat。

## 许可与内容范围

NapCatDocs 的 MIT 许可保留在 [LICENSE-NAPCATDOCS.txt](../LICENSE-NAPCATDOCS.txt)。NapCatQQ 的自定义许可仅作为源码查阅依据记录，技能不包含其实现。自行整理的指导采用本仓库 AGPL-3.0-or-later；见 [NOTICE.txt](../NOTICE.txt) 和 [LICENSE.txt](../LICENSE.txt)。不要把“文档可引用”解释为“上游实现可任意重新许可”。
