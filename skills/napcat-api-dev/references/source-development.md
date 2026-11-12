# NapCat 本体源码查阅与开发

本节用于用户明确要求修改 NapCat 本体或排查外部 API 无法解释的问题。普通对接优先使用公开 action。

## 定位路径

| 问题 | 起点 |
| --- | --- |
| action 是否存在、别名和注册 | `packages/napcat-onebot/action/router.ts`、`index.ts`、`auto-register.ts` |
| 参数及返回值 | 对应 action 的 schema、校验、`_handle`，以及继承基类 |
| HTTP / WS 行为 | `packages/napcat-onebot/network/` 下对应适配器 |
| 配置默认值与解析 | `packages/napcat-onebot/config/config.ts` |
| 插件生命周期与加载 | `packages/napcat-onebot/network/plugin-manger.ts`、`plugin/loader.ts`、`plugin/types.ts` |
| 底层 QQ 调用 | 从 handler 中 `core.apis` 的实际调用继续追踪到 `packages/napcat-core/` |
| API 文档生成 | `packages/napcat-schema/` 和根 `build:openapi` 脚本 |
| 对外类型导出 | `packages/napcat-types/` |

目录中的 `plugin-manger.ts` 拼写如此，不要按常规拼写猜路径。先检查本地 checkout 的结构；以上是固定快照中的位置。

仓库有 `.codegraph/` 时优先使用 CodeGraph 理解符号、继承和调用链；没有索引时按路径和符号搜索，不为本任务自行索引。跟随真实调用定位，避免将同名示例或生成文档当作运行实现。

## 修改和验证

新增 action 时同时检查名称映射、handler 注册或自动注册方式、payload / return schema、校验逻辑、文档示例和受影响类型。只新增名字不代表 API 可调用。处理异步完成与错误响应时检查所有实际支持的传输，而非只验证 HTTP。

根 `package.json` 提供 `typecheck`、`test`、`build:shell`、`build:framework`、`build:webui`、`build:openapi` 等脚本；按受影响包选取，使用目标 checkout 的包管理器与 lockfile，不把旧命令当作固定不变的契约。Shell、Framework、WebUI 是不同构建路径，运行环境还依赖 QQ 和平台组件。

运行版本由构建信息提供，`packages/napcat-common/src/version.ts` 读取 `VITE_NAPCAT_VERSION`，开发环境可回退到开发版本字符串。根 `package.json` 的版本字段不能用于选择用户的 release。

先做受影响代码的类型检查与测试；再在对应 QQ / NapCat 环境验证 action 行为、事件或加载路径。mock 成功不能证明 NTQQ 底层兼容；没有目标环境就说明未覆盖实际收发及平台兼容性。

## 来源和许可边界

NapCatQQ 根目录使用自定义 Limited Redistribution License，README 另有混合许可说明；NapCatDocs 使用 MIT。两者不能混称为 MIT，也不能因为本技能采用 AGPL 就把上游实现重新许可。此技能只分发自行编写的指导及接口用法，不附带 NapCatQQ 实现或修改后的源码。确需复制或分发上游代码时查目标文件许可及授权条件。

来源：[源码仓库快照](https://github.com/NapNeko/NapCatQQ/tree/72912f293924f43463b5976b01fc094a8ae11481)、[构建脚本](https://github.com/NapNeko/NapCatQQ/blob/72912f293924f43463b5976b01fc094a8ae11481/package.json)、[运行版本](https://github.com/NapNeko/NapCatQQ/blob/72912f293924f43463b5976b01fc094a8ae11481/packages/napcat-common/src/version.ts)、[NapCatQQ 许可](https://github.com/NapNeko/NapCatQQ/blob/72912f293924f43463b5976b01fc094a8ae11481/LICENSE)。
