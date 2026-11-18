# ChatUI 消息卡片与工作台

先确认目标包含 [消息视图 #11179](https://github.com/AstrBotDevs/AstrBot/pull/11179) 和所需的 [工作台 #11218](https://github.com/AstrBotDevs/AstrBot/pull/11218) 实现。这两项均晚于 `v4.30.0-alpha.1` 标签。当前内置宿主是 AstrBot ChatUI。

## 声明视图和交互方式

视图入口固定为 `views/<name>/index.html`，通过 `metadata.yaml` 中的 `views` 声明。名称在插件内唯一。前端用相对路径加载外部 module 脚本，由宿主注入 SDK。

| `target` | 打开方式 | 操作接口 |
| --- | --- | --- |
| `chat_message` | 命令、消息 handler 或工具创建消息卡片 | `bridge.view.subscribe()`、`bridge.view.action()` |
| `chat_workbench` | 由消息或工具在右侧打开工作台 | 同消息卡片 |
| `chat_workbench_with_launcher` | 可由消息打开，也可从工作台「＋」打开 | 有 `context.view` 时使用视图接口，否则使用插件 Web API |
| `plugin_page` | WebUI 独立页面，默认 target | [Web API](web-views.md) |

## 创建和更新消息卡片

```yaml
views:
  - name: counter
    target: chat_message
    title: 计数器
    version: 1
    actions: ["counter:increment"]
```

以下方法放在 `Star` 子类内，从 `astrbot.api.event` 导入 `AstrMessageEvent`、`filter`：

```python
@filter.command("counter")
async def counter(self, event: AstrMessageEvent):
    yield event.view_result(
        name="counter", data={"count": 0}, text="计数器已创建，当前值为 0。"
    )


@filter.ui_action("counter:increment")
async def increment(self, event: AstrMessageEvent):
    interaction = event.get_ui_interaction()
    if interaction is None:
        return
    yield event.view_result(data={"count": interaction.view.data["count"] + 1})
```

创建时传名称及非空 `text`，用于平台不支持视图或加载失败时的文字回退。判断平台能力使用 `event.platform_meta.support_ui_interaction`。工具可以直接返回 `event.view_result()`，其中 `text` 提供给模型。UI 回调省略 `name` 会完整替换当前卡片的数据。`interaction.view.data` 是服务端快照，`interaction.data` 是本次客户端输入。业务上仍需校验操作者和输入。

在 `views/counter/app.js` 中订阅初始及后续快照，HTML 需包含 `#count`、`#increment`、`#error` 和模块脚本：

```javascript
const bridge = window.AstrBotPluginView;
await bridge.ready();
const count = document.querySelector("#count");
const button = document.querySelector("#increment");
const errorText = document.querySelector("#error");
bridge.view.subscribe(({ data }) => {
  count.textContent = String(data.count);
});
button.onclick = async () => {
  button.disabled = true;
  errorText.textContent = "";
  try {
    await bridge.view.action("counter:increment", {});
  } catch (error) {
    errorText.textContent = error.message;
  } finally {
    button.disabled = false;
  }
};
```

- `version` 表示数据和动作契约，不兼容升级后旧卡片回退到文字。成功更新会推进 `revision`，旧 revision 返回 `REVISION_CONFLICT` 并先同步快照。
- 重试同一动作时复用 `interaction_id`，业务外部副作用也以它做幂等。历史卡片只读取存储的快照。写入视图与请求模型会暂存至回调结束，外部副作用不能依赖框架回滚。
- 数据须可 JSON 序列化。快照上限 1 MiB，操作输入上限 64 KiB。一个处理链最多更新原卡片一次并请求模型一次。

## 常驻工作台

`chat_workbench_with_launcher` 的双入口可用 `await bridge.ready()` 返回的 `context.view` 区分。通过「＋」打开的常驻视图没有快照，使用插件 Web API、上传下载和 SSE。会话切换时监听 `onContext()` 的 `sessionId`，为空时清理相应界面，并防止上一会话的异步响应覆盖新页面。后端从 `request.username` 校验会话归属。

常驻视图可在用户操作时调用 `bridge.chat.fill(text)` 追加至输入框，或用 `bridge.chat.send(text)` 请求发送，Promise 完成表示请求已接受。无会话、会话切换或正在生成时，发送可能被拒绝。

来源：[视图总览、消息交互组件和工作台文档](https://github.com/AstrBotDevs/AstrBot/tree/06fc50b43ea1c13093c91762f3b9361911362f9a/docs/zh/dev/star/guides/plugin-views)、[Bridge 类型定义](https://github.com/AstrBotDevs/AstrBot/blob/06fc50b43ea1c13093c91762f3b9361911362f9a/docs/public/types/astrbot-plugin-view.d.ts)。
