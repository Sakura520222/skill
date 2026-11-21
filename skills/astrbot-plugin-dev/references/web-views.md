# 插件可视化视图与 Web API

先核对目标版本的 `astrbot.api.web` 和 bridge。ChatUI 消息和工作台宿主见 [chatui-views.md](chatui-views.md)。来源：[独立插件页面、共享 Bridge 和 Web API 文档](https://github.com/AstrBotDevs/AstrBot/tree/90ba3270f09b857063da68908d80f742042067cd/docs/zh/dev/star/guides/plugin-views)。

## 结构和连接

简单设置优先 `_conf_schema.json`。独立页面入口是 `views/<view_name>/index.html`，兼容旧的 `pages/`。只扫描一级子目录的 `index.html`。支持新版视图声明的版本可在 `metadata.yaml` 填 `views`，默认 `target` 为 `plugin_page`，未声明的目录仍可自动发现。

后端在构造函数注册带插件名前缀的路由：

```python
from astrbot.api.star import Context, Star
from astrbot.api.web import json_response, request

PLUGIN_NAME = "astrbot_plugin_example"


class ViewPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        context.register_web_api(
            f"/{PLUGIN_NAME}/status", self.status, ["GET"], "Read status"
        )

    async def status(self):
        limit = request.query.get("limit", 20, type=int)
        return json_response({"ready": True, "limit": limit})
```

前端使用外部 module 脚本，以便在 SDK 注入后执行：

```javascript
const bridge = window.AstrBotPluginView;
await bridge.ready();
const result = await bridge.apiGet("status", { limit: 10 });
document.getElementById("output").textContent = JSON.stringify(result);
```

HTML 中放置 `id="output"` 的元素及 `<script type="module" src="./app.js"></script>`。不必自行引入 SDK，AstrBot 返回页面时自动注入。旧别名为 `window.AstrBotPluginPage`。

## 路由与请求

前端 endpoint 只写插件内相对路径，例如 `items/123`；后端对应 `/<plugin_name>/items/<item_id>`。`<name>` 匹配单段，`<path:name>` 匹配多段。Dashboard 转发到 `/api/v1/plugins/extensions/<plugin_name>/...`。

endpoint 不允许 scheme、query、hash、空段、`.`、`..` 或反斜杠。GET 查询放在参数对象，POST 数据放在 body，不要把查询字符串拼进 endpoint。

`astrbot.api.web.request` 仅在 handler 请求上下文中使用：

- `request.query.get("limit", 20, type=int)`、`getlist("tag")`。
- `await request.json(default={})`、`await request.body()`。
- `await request.form()`、`await request.files()`，两者缓存解析结果。
- `request.username`、`headers`、`path_params`、`plugin_name` 等。

不要假定 JSON 一定是字典；先验证类型和字段，再修改配置或数据。推荐响应函数 `json_response(...)`、`error_response(message, status_code=400)`、`file_response(path, filename=..., content_type=...)`、`stream_response(generator)`。旧 Quart handler 可以逐个迁移，不在同一 handler 混用两个 request 代理。

## Bridge 返回值与功能

| 方法 | 行为 |
| --- | --- |
| `ready()` | 等待初始上下文 |
| `getContext()` / `onContext(handler)` | 读取/订阅语言主题等上下文；后者返回取消监听函数 |
| `apiGet(endpoint, params)` | GET 查询 |
| `apiPost(endpoint, body)` | POST JSON |
| `upload(endpoint, file)` | multipart 单文件，字段名固定 `file` |
| `download(endpoint, params, filename)` | 下载，resolve 为 `{filename}` |
| `subscribeSSE(endpoint, handlers, params)` | 订阅，resolve 为 subscription ID |
| `unsubscribeSSE(id)` | 取消订阅 |

普通 JSON 原样 resolve；`{"status":"ok","data":value}` 解包为 value；`status:error` 或 HTTP 失败 reject 为 Error。业务 API 返回普通 JSON 最清晰，前端处理异常。

上传文件用 `(await request.files()).get("file")`，校验为 `PluginUploadFile`。限制文件名/大小/类型和数据目录；不要直接信任来自浏览器的完整路径。

SSE handler 返回 `stream_response(...)`，消息使用 `data: ...\n\n`。前端 handler 可读 `event.raw`、`parsed`、`lastEventId`、`eventType`。卸载视图时取消订阅；不用原生 `EventSource` 绕过 bridge，它不能携带这里所需的 Authorization header。

### SSE 结束与错误通知

`onClose` 来自 [v4.29.4 发布后的上游变更](https://github.com/AstrBotDevs/AstrBot/commit/15e1b9996e94fad780bc207393ea13506d64b49e)，已包含在 `v4.30.0-alpha.1` 标签中。

```javascript
let subscriptionId;
try {
  subscriptionId = await bridge.subscribeSSE("events", {
    onOpen() {
      console.log("SSE 已连接");
    },
    onMessage(event) {
      console.log(event.parsed);
    },
    onClose() {
      console.log("SSE 流正常结束");
    },
    onError() {
      console.error("SSE 读取失败");
    },
  });
} catch (error) {
  console.error("SSE 初次订阅失败", error);
}

window.addEventListener("beforeunload", () => {
  if (subscriptionId !== undefined) bridge.unsubscribeSSE(subscriptionId);
});
```

流正常结束调用 `onClose`，读取失败调用 `onError`；主动 `unsubscribeSSE` 不触发这两个回调。初次订阅失败会直接 reject 返回的 Promise，应由调用处捕获，不能只依靠 `onError`。bridge 不自动重连，需要继续接收时由业务重新订阅，并清理旧订阅，避免重复流。

## 资源、主题和语言

静态资源使用 `./style.css`、`./app.js`、`./assets/...`。当前版本用视图路径令牌鉴权，相对路径自然继承令牌；不要拼接历史 `asset_token` URL 或用 `..` 跨目录。SPA 优先 hash routing。

iframe 的 sandbox 允许脚本/表单/下载，不能读取父页面 DOM、Dashboard cookies 或 LocalStorage。需要 Dashboard 身份的操作走 bridge，后端仍验证输入。

SDK 同步 HTML 的 `data-theme`。带 [主题色支持](https://github.com/AstrBotDevs/AstrBot/pull/11046) 的版本还会同步 CSS `color-scheme` 和 `--astrbot-color-*`，例如 `--astrbot-color-primary`、`--astrbot-color-text` 和 `--astrbot-color-background`。CSS 可直接使用这些变量，兼容旧 bridge 时提供默认值。JS 可通过 `onContext()` 监听变化。标题和翻译见 [i18n.md](i18n.md)。

页面不出现先查目录和重载；bridge 未就绪查脚本加载顺序；API 404 查插件名前缀；SSE 查响应类型和消息空行。没有实际 WebUI 运行时不要声称页面验收通过。
