# 微信小程序 AI 开发模式 · 接口文档

> **定位**：小程序 AI 开发模式暴露给开发者的接口参考，聚焦**接口定义与功能**（函数签名 + 出入参类型 + 类型集中定义），供 Coding Agent 写代码时查阅。
>
> **事实源与优先级**（冲突时以源码为准并标注差异）：
> 1. **基础库源码**：本机微信开发者工具 `WeappVendor/3.16.1.wxvpkg` 与 `3.17.2.wxvpkg` 解包实证（`WAAgentAppMainContext.js` / `WAAgentBase.js` / `WAAgentAppSubContext.js` / `WAServiceMainContext.js`，明文 minified JS）→ 徽标 `[源码]`
> 2. **官方文档镜像**（2026-07-21 快照，`docs/wechat-ai-docs/`）→ 徽标 `[官方]`
> 3. **本仓库 demo**（`skills/drink-skill/`，可在工具内真实运行）→ 徽标 `[demo]`
> 4. 无依据 → 徽标 `[未验证]`
>
> **类型约定**：全文使用 TypeScript 语法描述签名；**第一章为全部共享类型的唯一权威定义**，API 详情按类型名引用。运行时为 JavaScript，类型是契约描述而非运行时校验（`arguments` 的实际形状由 `mcp.json` 的 `inputSchema` 决定）。**接口/类型名（如 `ModelContext`、`ViewContext`、`DetailPageModelContext`）均为本文档的引用约定，运行时不存在同名符号**——直接挂在 `wx` 上的只有各 API 详情小节签名中的 `wx.*` 调用路径。
>
> **版本口径**：按基础库 **3.16.1 ～ 3.17.2** 源码实证；两版本 `wx.modelContext` 主面一致，例外单独标注（如 `wx.onAgentHandoff` 家族 **3.16.1 不存在、3.17.2 存在**，与官方「Handoff 需 iOS 8.0.75 / 基础库 3.16.2+」互证）。内测 beta，以[官方更新日志](https://developers.weixin.qq.com/miniprogram/dev/ai/changelog.html)为准。
>
> **四个执行上下文**（同一 API 在不同上下文可用性不同）：
> ① **原子接口环境**（隔离 JS 环境，跑 `apis/*.js`）② **原子组件环境**（卡片渲染，跑 `components/*`）③ **半屏页面**（detail page）④ **小程序页面 / 接力页**（普通小程序环境）

---

## 目录

- [一、类型定义（TypeScript）](#一类型定义typescript)
- [二、wx.modelContext 命名空间总览](#二wxmodelcontext-命名空间总览)
- [三、API 详情](#三api-详情)
- [四、原子接口开发者契约](#四原子接口开发者契约)
- [五、声明式配置接口](#五声明式配置接口)
- [六、源码与官方文档差异对照表](#六源码与官方文档差异对照表)
- [附：证据索引（源码）](#附证据索引源码)

---

## 一、类型定义（TypeScript）

> 本章是全文类型的**唯一权威定义**；各 API 小节只引用类型名。每条注明来源徽标；标注「运行时无校验」处仅靠开发者自觉遵守。

### 1.1 基础类型

```ts
/** 通用回调结果：errMsg 形如 'xxx:ok' / 'xxx:fail <reason>'（微信 API 惯例）[源码][官方] */
interface ErrMsgResult {
  errMsg: string
}

/** 矩形区域（半屏页关闭按钮位置）[官方] */
interface Rect {
  left: number
  top: number
  width: number
  height: number
}

/** 卡片可用尺寸（对应卡片宽高比 4:1 ~ 1:1 约束；缺省 0）[官方][源码] */
interface Dimensions {
  minHeight: number
  maxHeight: number
  width: number
}

/** 原子组件实例（glass-easel 组件 this）；getContext/getViewContext 靠 getPageId() 绑定卡片帧 [源码] */
interface ComponentInstance {
  getPageId(): number | string   // pageId 形如 "pageId:12"，内部解析为数字帧 ID
}
```

### 1.2 原子接口契约类型

```ts
/** 文本内容块（AtomicApiResult.content 与多数上行消息的元素）[官方][源码] */
interface TextContent {
  type: 'text'
  text: string
}

/** 显式指定下一步调用的原子接口（AtomicApiResult.apiCalls 元素）[官方] */
interface ApiCall {
  name: string
  arguments: Record<string, unknown>
}

/** 页面接力数据（AtomicApiResult.handoff；与 content 同级返回）[官方] */
interface HandoffResolver {
  path?: string      // 允许动态指定页面路径
  query?: string     // 必须 string（demo：encodeURIComponent 后拼接）
  payload?: any      // 业务数据，接力页经 wx.onAgentHandoff 接收
}

/** 原子接口返回值 [官方]（限额与校验：见 4.2） */
interface AtomicApiResult {
  isError?: boolean           // 默认 false；true 时不渲染卡片，structuredContent 被忽略
  content: TextContent[]      // 必填；给模型的事实 + 下一步动作；≤200KB
  structuredContent?: object  // 给模型 + 卡片渲染；≤200KB
  _meta?: object              // 仅卡片可见（模型不可见）；≤200KB
  handoff?: HandoffResolver
  apiCalls?: ApiCall[]        // ≤200KB
}

/**
 * 原子接口 handler 的函数签名。
 * args 的实际形状由 mcp.json 的 inputSchema 声明（运行时无静态校验，接口内需自行校验）[官方]。
 * 返回 AtomicApiResult 或其 Promise；返回 undefined 会被运行时替换为
 * { isError: true, content: [{type:'text', text:'Tool execution error: missing result'}] } [源码]
 */
type AtomicApiHandler<TInput extends object = Record<string, any>> = (
  args: TInput
) => AtomicApiResult | Promise<AtomicApiResult>

/** createSkill 返回的 Skill 实例 [源码][官方] */
interface Skill {
  registerAPI<TInput extends object = Record<string, any>>(
    name: string,
    handler: AtomicApiHandler<TInput>
  ): void
  use(middleware: Middleware): void
}

/**
 * 中间件执行上下文：内置字段 + 任意自定义扩展位（如 ctx.loginState）[源码]。
 * 注意：handler 收到的是原始 arguments（深拷贝前），中间件无法改写传给 handler 的入参 [源码]。
 */
interface MiddlewareContext {
  name: string                       // 本次调用的原子接口名 [源码]
  skillPath: string                  // 归属 Skill 路径 [源码]
  arguments: Record<string, unknown> // 本次调用入参（深拷贝，只读语义）[源码]
  [key: string]: any                 // 中间件间共享的扩展位
}

/**
 * 洋葱模型中间件 [官方][源码]：
 * - next() 前为前置、await next() 后为后置；next() 只能调用一次（重复调用抛 "next() called multiple times"）[源码]
 * - 返回非 undefined 值将短路为最终结果（后续中间件与 handler 不再执行）[源码]
 * - 不调用 next() 的中间件导致结果 { isError: true, content: 'Middleware did not call next()' } [源码]
 */
type Middleware = (
  ctx: MiddlewareContext,
  next: () => Promise<void>
) => Promise<void | AtomicApiResult>
```

### 1.3 过滤与选项类型

```ts
/** 卡片过期过滤器（expireAllCards / expirePreviousCards 共用）[源码] */
interface ExpireFilter {
  skillPath?: string                    // 前缀匹配组件路径（首 '/' 忽略）；官方未记载
  componentPaths?: string[]             // 精确匹配组件路径数组（首 '/' 忽略）
  match?: 'all' | 'latest'              // 默认 'all'；'latest' 仅最近一张匹配卡片
}

/** 打开/预加载半屏页面选项 [源码][demo]（官方文档写 {path, query}，实证只读 url，见 D1） */
interface OpenDetailPageOption {
  url: string    // 页面路径，query 内联：'path?key=value'；demo 用绝对路径（首 '/'）
}

/** 关闭半屏页面选项（未公开 API）[源码] */
interface CloseDetailPageOption {
  closeAll?: boolean
}

/** 卡片标题栏「进入小程序」入口设置 [源码][官方] */
interface SetRelatedPageOption {
  path?: string        // 未提供时沿用 mcp.json components[].pagePath 静态声明
  query?: string       // 首部 '?'/'&' 自动剥离后拼接
  appId?: string       // 跨小程序（官方未记载）
  envVersion?: string  // 版本环境（官方未记载）
}

/** 交互状态回传参数 [官方][源码]（每项必须 type:'text' 且 text 非空，含其他类型整单拒绝） */
interface UpdateModelContentParam {
  content: TextContent[]
}
```

### 1.4 上下文对象类型

```ts
/** 通知事件类型值 [源码]（官方仅记载前四个 ★） */
type NotificationTypeValue =
  | 'input'     // ★ 原子接口入参到达
  | 'result'    // ★ 原子接口出参到达
  | 'overflow'  // ★ 内容溢出
  | 'resize'    // 尺寸变化（官方未记载）
  | 'expire'    // ★ 卡片过期
  | 'ban'       // 卡片封禁（官方未记载）
  | 'unban'     // 卡片解封（官方未记载）

/** wx.modelContext.NotificationType 枚举对象 [源码] */
interface NotificationType {
  readonly Input: 'input'
  readonly Result: 'result'
  readonly Overflow: 'overflow'
  readonly Resize: 'resize'
  readonly Expire: 'expire'
  readonly Ban: 'ban'
  readonly UnBan: 'unban'
}

/** 各通知事件的回调载荷（on(type, cb) 的 cb 入参）[源码]；未记载事件的载荷标 [未验证] */
interface NotificationEventMap {
  input:    { input: Record<string, unknown> }   // 即 toolCall.arguments
  result:   { result: AtomicApiResult }          // 即原子接口返回值
  overflow: unknown                              // [未验证]
  resize:   unknown                              // [未验证]
  expire:   { expiredText: string }
  ban:      unknown                              // [未验证]
  unban:    unknown                              // [未验证]
}

/** getContext() 返回的模型上下文（原子组件环境）[源码] */
interface ModelContext {
  on<K extends NotificationTypeValue>(type: K, callback: (payload: NotificationEventMap[K]) => void): void
  off(type?: NotificationTypeValue, callback?: Function): void
  /** 见 3.8：三形态 message；须 tap 手势内调用；500ms 节流 */
  sendFollowUpMessage(message: FollowUpMessage): Promise<ErrMsgResult>
}

/** 半屏页面 modelContext（wx.modelContext.getContext() 返回）[源码] */
interface DetailPageModelContext {
  /** 见 3.9：发送后自动关闭半屏页面 */
  sendFollowUpMessage(param: SendFollowUpMessageParam): Promise<ErrMsgResult>
  /** 见 3.11：重跑调用链；须 tap 手势内调用；执行后自动关闭半屏页面 */
  reapplyApiCall(params?: ReapplyApiCallParam): Promise<ErrMsgResult>
}

/** getViewContext() 返回的卡片视图上下文（原子组件环境）[源码] */
interface ViewContext {
  getDimensions(): Dimensions
  on<K extends NotificationTypeValue>(type: K, callback: (payload: NotificationEventMap[K]) => void): void
  off(type?: NotificationTypeValue, callback?: Function): void
  /** 见 3.14：tap 手势内调用；3000ms 冷却 */
  openDetailPage(option: OpenDetailPageOption): Promise<ErrMsgResult>
  /** 见 3.15：无手势要求（可预加载） */
  preloadDetailPage(option: OpenDetailPageOption): Promise<ErrMsgResult>
  /** 见 3.16：未公开 API */
  closeDetailPage(option?: CloseDetailPageOption): Promise<ErrMsgResult>
  /** 见 3.17：过期当前帧之前的卡片 */
  expirePreviousCards(filter?: ExpireFilter): Promise<ErrMsgResult>
  /** 见 3.18 */
  setRelatedPage(option: SetRelatedPageOption): Promise<ErrMsgResult>
  /** 见 3.19：tap 回调内同步调用；500ms 节流 */
  updateModelContext(param: UpdateModelContentParam): Promise<ErrMsgResult>
}
```

运行时 `wx.modelContext.NotificationType` 的实际形状（源码字面量）`[源码]`：

```js
wx.modelContext.NotificationType = {
  Input: 'input', Result: 'result', Overflow: 'overflow', Resize: 'resize',
  Expire: 'expire', Ban: 'ban', UnBan: 'unban'
}
```

### 1.5 消息与事件类型

```ts
/** 上行消息中的 api/call 内容块：直接触发指定原子接口调用（官方未记载）[源码] */
type ApiCallContentItem =
  | { type: 'api/call'; name: string; arguments: Record<string, unknown> }              // 平铺形态
  | { type: 'api/call'; data: { name: string; arguments: Record<string, unknown> } }    // data 包裹形态（demo 用）

/** 上行消息内容项 [源码] */
type FollowUpContentItem = TextContent | ApiCallContentItem

/**
 * 原子组件环境上行消息（sendFollowUpMessage 入参）：三形态 union [源码]。
 * content 为数组时：非空、首项必须 type:'text'；text 项拼接为上行文本，其余作 contentItems 透传；
 * 顶层 handoff 字段会被静默剥离。
 */
type FollowUpMessage =
  | string
  | { content: string }
  | { content: FollowUpContentItem[] }

/** 半屏页面 sendFollowUpMessage 入参 [官方][源码] */
type SendFollowUpMessageParam =
  | { type: 'text'; text: string }          // text 时必填
  | { type: 'image'; fileid: string }       // image 时必填（云存储文件 ID）
  | { content: TextContent[] }              // 官方 02 篇示例形态

/** reapplyApiCall 入参：透传给运行时，可覆盖重跑入参（官方示例形态）[官方][源码] */
interface ReapplyApiCallParam {
  arguments: Record<string, unknown>
}

/** wx.onAgentHandoff 回调事件 [源码][demo] */
interface HandoffEvent {
  pageId: string    // 形如 "pageId:12"（源码拼 'pageId:' 前缀；demo 直接作 map key）
  path: string
  query: string     // 未解码的原始 query 串——需自行 decodeURIComponent [源码]
  payload?: any     // handoff.payload 透传；可能缺失，接力页需兼容 [demo]
}
type AgentHandoffCallback = (event: HandoffEvent) => void

/** web-view H5 桥接消息（wx.miniProgram.postMessage 的 data）[官方][源码] */
type H5BridgeMessage =
  | { type: 'sendFollowUpMessage'; content: TextContent[] }
  | { type: 'reapplyApiCall'; params?: ReapplyApiCallParam }
```

---

## 二、wx.modelContext 命名空间总览

### 2.1 命名空间成员（源码实证）

`wx.modelContext` 在基础库中是一个工厂函数返回的对象，成员如下 `[源码]`：

| 成员签名 | 功能 |
|---|---|
| `createSkill(skillPath: string): Skill` | 创建 Skill 实例（仅原子接口环境生效，其他上下文为 no-op） |
| `registerAPI(name: string, handler: AtomicApiHandler): void` | 直接注册原子接口（仅原子接口环境生效）；与 `skill.registerAPI` 等价 `[官方]` |
| `getContext(instance?: ComponentInstance): ModelContext`（③ 半屏页返回 `DetailPageModelContext`，见 3.6 / D11） | 获取模型上下文（事件订阅 + 上行消息） |
| `getViewContext(instance: ComponentInstance): ViewContext` | 获取卡片视图上下文（尺寸 / 半屏 / 过期 / 关联页 / 状态回传） |
| `NotificationType: NotificationType` | 通知事件类型枚举（7 值，类型定义见 1.4） |
| `getSessionId(): string` | 获取当前会话 ID（返回 `runtimeSessionId`） |
| `expireAllCards(filter?: ExpireFilter): Promise<ErrMsgResult>` | 将已渲染卡片置为过期态 |

### 2.2 各上下文实际可用的 API 面

| 上下文 | 可用 API | 来源 |
|---|---|---|
| ① 原子接口环境 | `wx.modelContext` 全部成员；`wx.login` / `wx.request` / 网络 / 云开发 / storage 等（详见官方 07 权限矩阵） | `[源码]` `[官方]` |
| ② 原子组件环境 | `getContext(this): ModelContext`；`getViewContext(this): ViewContext`（全方法）；`wx.modelContext.{NotificationType, getSessionId, expireAllCards}` | `[源码]` |
| ③ 半屏页面 | `wx.modelContext.getContext(): DetailPageModelContext`（源码形态：`modelContext: {getContext: () => ({sendFollowUpMessage, reapplyApiCall})}`）；`wx.getDetailPageCloseButtonBoundingClientRect(): Rect` | `[源码]` `[官方]` |
| ④ 小程序/接力页 | `wx.onAgentHandoff(cb)` / `wx.offAgentHandoff()`（3.16.2+）；另见 3.22 未公开 agent API 家族 | `[源码]` `[官方]` |

---

## 三、API 详情

> 模板：**签名（TS）** → 功能 → 适用上下文 → 参数 → 返回 → 行为与限制 → 示例 → 来源。类型引用第一章。

### 3.1 wx.modelContext.createSkill

```ts
wx.modelContext.createSkill(skillPath: string): Skill
```

- **功能**：创建 Skill 实例。`skillPath` 必须与 `app.json` 的 `agent.skills[].path` 一致 `[官方]`。
- **适用上下文**：① 原子接口环境（`"sub"` 上下文；其他上下文中为 no-op 空函数）`[源码]`。
- **参数**：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `skillPath` | `string` | 是 | 非空字符串；内部做路径规范化（去尾部 `/` 等）。空串报错 `createSkill requires a non-empty skillPath string` `[源码]` |

- **返回**：`Skill`（`{registerAPI, use}`，类型见 1.2）`[源码]`。
- **行为与限制**：`createSkill` 本身不做存在性校验（不检查目录是否真实存在）`[源码]`。
- **示例**：

```js
const skill = wx.modelContext.createSkill('skills/drink-skill')
```

- **来源**：`[源码]` `[官方]` `[demo]`

### 3.2 skill.registerAPI / wx.modelContext.registerAPI

```ts
skill.registerAPI<TInput>(name: string, handler: AtomicApiHandler<TInput>): void
wx.modelContext.registerAPI<TInput>(name: string, handler: AtomicApiHandler<TInput>): void   // 等价
```

- **功能**：注册原子接口。`name` 必须与 `mcp.json` 中 `apis[].name` 一致 `[官方]`。
- **适用上下文**：① 原子接口环境。
- **参数**：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `name` | `string` | 是 | 非空字符串；空串报 `registerAPI: name must be a non-empty string` |
| `handler` | `AtomicApiHandler<TInput>` | 是 | 见 1.2；非函数报 `registerAPI: handler must be a function` |

- **返回**：`void`。
- **行为与限制** `[源码]`：handler 存入**全局注册表**（跨 Skill 共享，同名覆盖，覆盖时 warn `registerAPI: overwriting existing handler`）。注册是进程内行为，真实调用链由 AI 后台下发 `tools/call` 后查表执行。
- **示例**：

```js
skill.registerAPI('getWeather', getWeather)
```

- **来源**：`[源码]` `[官方]` `[demo]`

### 3.3 skill.use

```ts
skill.use(middleware: Middleware): void
```

- **功能**：注册洋葱模型中间件；`next()` 前为前置、后为后置。多个中间件按注册顺序成链 `[官方]`。
- **适用上下文**：① 原子接口环境。
- **参数**：`middleware: Middleware`（见 1.2），必须为函数（非函数被忽略并 warn）`[源码]`。
- **返回**：`void`。
- **行为与限制**：
  - 中间件链与原子接口执行共享 **300s 超时**，超时结果为 `{isError:true, content:'Tool "X" execution timed out after Nms'}` `[官方]` `[源码]`；
  - 中间件按规范化后的 `skillPath` 归组（同一个 Skill 的多次 `use` 依次追加）`[源码]`；
  - **ctx 内置字段** `{name, skillPath, arguments}`（arguments 为深拷贝），可挂自定义属性 `[源码]`；
  - **`next()` 只能调一次**（重复抛 `next() called multiple times`）`[源码]`；
  - **中间件返回非 undefined 值 → 短路为最终结果**，后续中间件与 handler 不执行 `[源码]`；
  - 不调 `next()` → `{isError:true, content:'Middleware did not call next()'}` `[源码]`；
  - **handler 收到原始 `arguments` 而非 ctx**，中间件无法改写传给 handler 的入参 `[源码]`。
- **示例**：

```js
skill.use(async (ctx, next) => {
  ctx.loginState = await getLoginState()     // 前置：ctx 是 MiddlewareContext
  try {
    await next()                             // 后置继续
  } catch (e) { throw e }                    // 错误监听
})
```

- **来源**：`[官方]` `[源码]`

### 3.4 wx.modelContext.getSessionId

```ts
wx.modelContext.getSessionId(): string
```

- **功能**：获取当前 AI 会话 ID（源码返回 `runtimeSessionId`）。
- **适用上下文**：①②（源码实现在命名空间工厂内，随 `wx.modelContext` 暴露）。
- **返回**：`string` `[源码]`。
- **来源**：`[官方]` `[源码]`

### 3.5 wx.modelContext.expireAllCards

```ts
wx.modelContext.expireAllCards(filter?: ExpireFilter): Promise<ErrMsgResult>
```

- **功能**：将已渲染的原子组件卡片置为过期态（灰色蒙层、不可点击）。可在原子接口 / 原子组件里调用 `[官方]`。
- **参数**：`filter: ExpireFilter`（类型定义见 1.3）。源码完整语义 `[源码]`：`skillPath` **前缀匹配**、`componentPaths` **精确匹配**（两者首 `/` 均忽略），`match` 默认 `'all'`（`'latest'` 时仅最近一张匹配卡片过期）。

- **返回**：`Promise<ErrMsgResult>`，成功 `errMsg: 'expireAllCards:ok'`（源码底层调 expirePreviousCards 后重写 errMsg）`[源码]`。
- **行为与限制**：
  - 仅对 `mcp.json` 中声明了 `expirable: true` 的组件生效 `[官方]` `[源码]`（源码逐帧检查 `frame.expirable`）；
  - 范围限定当前 appId 的卡片 `[源码]`；
  - 已过期 / 已销毁的卡片跳过 `[源码]`；
  - 过期后客户端收到 `NotifyCardExpired` 通知渲染蒙层，`expiredText` 取自 mcp.json 声明 `[源码]`。
- **示例**：

```js
wx.modelContext.expireAllCards()                                        // 全部 expirable 卡片过期
wx.modelContext.expireAllCards({ componentPaths: ['components/weather-card/index'] })
wx.modelContext.expireAllCards({ skillPath: 'skills/drink-skill', match: 'latest' })
```

- **来源**：`[官方]` `[源码]`

### 3.6 wx.modelContext.getContext

```ts
// 原子组件环境
wx.modelContext.getContext(instance?: ComponentInstance): ModelContext
// 半屏页面环境（返回不同接口）
wx.modelContext.getContext(): DetailPageModelContext
```

- **功能**：获取模型上下文对象，用于订阅通知与上行消息（两个环境的返回类型不同，见 1.4）。
- **适用上下文**：② 原子组件环境（传 `this` 提取 `pageId` 绑定帧）；③ 半屏页面 `[源码]`。
- **参数**：`instance: ComponentInstance`（可省略；省略时不绑定帧，返回独立上下文）`[源码]`。
- **返回**：`ModelContext`（组件环境）/ `DetailPageModelContext`（半屏页）。
- **行为与限制**：同一 `pageId` 重复获取返回已注册的同一实例 `[源码]`。
- **示例**：

```js
this._modelCtx = wx.modelContext.getContext(this)   // 原子组件内（推荐传 this）
```

- **来源**：`[官方]` `[源码]` `[demo]`

### 3.7 ModelContext.on / off

```ts
modelContext.on<K extends NotificationTypeValue>(
  type: K,
  callback: (payload: NotificationEventMap[K]) => void
): void
modelContext.off(type?: NotificationTypeValue, callback?: Function): void
```

- **功能**：订阅/取消订阅通知事件。组件环境常用 `Result` 事件拿原子接口返回值驱动卡片渲染。
- **事件回放语义** `[源码]`：

| 事件 | 回调入参 | 说明 |
|---|---|---|
| `NotificationType.Input` | `{input: arguments}` | 原子接口入参（`toolCall.arguments`） |
| `NotificationType.Result` | `{result: AtomicApiResult}` | 原子接口返回值 |

- **返回**：`void`。
- **行为与限制**：绑定帧时，注册即回放历史 `Input`/`Result`（若该帧已有 toolCall/toolResult）`[源码]`；`ViewContext.on / off` 与本节**同签名**（源码共享同一事件总线实现），无需单独小节 `[源码]`。
- **示例**：

```js
const { NotificationType } = wx.modelContext
this._modelCtx.on(NotificationType.Result, (data) => {
  const { structuredContent, _meta } = data.result
})
```

- **来源**：`[官方]` `[源码]` `[demo]`

### 3.8 ModelContext.sendFollowUpMessage（原子组件环境）

```ts
modelContext.sendFollowUpMessage(message: FollowUpMessage): Promise<ErrMsgResult>
// FollowUpMessage: string | { content: string } | { content: FollowUpContentItem[] }
```

- **功能**：代用户向对话区上行一条消息，等同用户亲自发送 `[官方]`。
- **参数**：`message: FollowUpMessage`（三形态 union，见 1.5）`[源码]`：
  - `content` 为数组时：非空、**首项必须 `type:'text'`**；`text` 项拼接为上行文本；非 text 项作为 `contentItems` 透传；
  - `ApiCallContentItem`（`type:'api/call'`）**直接触发指定原子接口调用**，`arguments` 序列化后 ≤ **2000 字符**——官方文档完全未记载 `[源码]`；
  - 参数对象上的 `handoff` 字段会被静默剥离（不可借道上行的 handoff）`[源码]`；
  - 源码存在第二参数可跳过 tap 手势校验（内部调试用途），开发者不应使用 `[源码]`。

- **返回**：`Promise<ErrMsgResult>`，成功 `errMsg: 'sendFollowUpMessage:ok'`。
- **行为与限制** `[源码]`：
  - **必须发生在用户 tap 手势链内**（无手势时拒绝：`:fail can only be invoked by user TAP gesture.`）；
  - **500ms 节流**：短时间重复调用拒绝 `sendFollowUpMessage:fail throttled`；
  - 文案应以**用户第一人称**书写（「帮我…」，不是「系统已…」）`[官方]`。
- **示例**：

```js
this._modelCtx.sendFollowUpMessage('帮我确认支付')                          // 形态一：纯字符串
this._modelCtx.sendFollowUpMessage({ content: '帮我确认支付' })             // 形态二
this._modelCtx.sendFollowUpMessage({                                       // 形态三：携带 api/call
  content: [
    { type: 'text', text: `选择${item.name}` },
    { type: 'api/call', data: { name: 'selectDrink', arguments: { drinkId: item.drinkId } } }
  ]
})
```

- **来源**：`[官方]` `[源码]` `[demo]`

### 3.9 DetailPageModelContext.sendFollowUpMessage（半屏页面环境）

```ts
wx.modelContext.getContext().sendFollowUpMessage(param: SendFollowUpMessageParam): Promise<ErrMsgResult>
// SendFollowUpMessageParam: {type:'text',text} | {type:'image',fileid} | {content: TextContent[]}
```

- **功能**：半屏页面内上行文本/图片消息。**发送成功后自动关闭半屏页面回到对话**（源码：发完即调 `closeDetailPage` 且 `closeAll:true`）`[源码]`。

> ⚠️ **差异（D11）**：官方 08/02 篇示例**直呼** `wx.modelContext.sendFollowUpMessage(...)`；**源码实证半屏页的 `wx.modelContext` 仅有 `getContext()`**，本方法与 3.11 `reapplyApiCall` 都挂在 `getContext()` 返回值上——按官方形态调用为 `undefined`。demo 无半屏页实跑佐证，以源码为准。

- **适用上下文**：③ 半屏页面（含 web-view 内 H5，见 3.10）。
- **参数**：`param: SendFollowUpMessageParam`（三形态 union：`{type:'text', text}` / `{type:'image', fileid}` / `{content: TextContent[]}`，字段定义见 1.5；源码将 message 整体透传运行时，两形态均可用）`[官方]`（08 篇）`[源码]`。

- **返回**：`Promise<ErrMsgResult>`；非半屏页调用抛错 `fail page info not found` / `not an agent detail page` `[源码]`。
- **示例**：

```js
wx.modelContext.getContext().sendFollowUpMessage({ content: [{ type: 'text', text: '帮我确认支付' }] })
```

- **来源**：`[官方]` `[源码]`

### 3.10 web-view H5 上行桥接

```ts
wx.miniProgram.postMessage({ data: H5BridgeMessage }): void
// H5BridgeMessage: {type:'sendFollowUpMessage', content} | {type:'reapplyApiCall', params?}
```

- **功能**：H5 内代用户上行消息 / 重跑调用链。源码 `onWebInvokeAppService` 分发表实证支持 `sendFollowUpMessage` 与 `reapplyApiCall` 两个 type `[源码]`。
- **示例**：

```js
wx.miniProgram.postMessage({
  data: { type: 'sendFollowUpMessage', content: [{ type: 'text', text: '...' }] }
})
```

- **来源**：`[官方]`（sendFollowUpMessage）`[源码]`（reapplyApiCall 桥接）

### 3.11 DetailPageModelContext.reapplyApiCall

```ts
wx.modelContext.getContext().reapplyApiCall(params?: ReapplyApiCallParam): Promise<ErrMsgResult>
```

- **功能**：半屏页面操作后重新执行「原子接口 → 原子组件」调用链，更新卡片内容 `[官方]`。

> ⚠️ 同 D11（见 3.9）：官方写 `wx.modelContext.reapplyApiCall()` 直呼，源码实证须 `wx.modelContext.getContext().reapplyApiCall()`。

- **适用上下文**：③ 半屏页面。
- **参数**：`params: ReapplyApiCallParam`（可省略；见 1.5）——源码将其作为 `params` 字段随 `reapplyApiCall` 消息透传给运行时 `[源码]`。
- **返回**：`Promise<ErrMsgResult>`，成功 `errMsg: 'reapplyApiCall:ok'`；失败：`fail not an agent detail page`（非半屏页）/ `fail no tap mark`（无用户手势）`[源码]`。
- **行为与限制** `[源码]`：**必须在用户 tap 手势内调用**；执行后自动 `closeDetailPage` 关闭半屏页面。
- **示例**：

```js
wx.modelContext.getContext().reapplyApiCall()                              // 无参：重跑调用链刷新卡片
wx.modelContext.getContext().reapplyApiCall({ arguments: { city: '深圳' } })  // 覆盖入参重跑
```

- **来源**：`[官方]` `[源码]`

### 3.12 wx.modelContext.getViewContext

```ts
wx.modelContext.getViewContext(instance: ComponentInstance): ViewContext
```

- **功能**：获取卡片视图上下文 `ViewContext`（全方法签名见 1.4；方法详情见 3.13–3.19）。
- **适用上下文**：② 原子组件环境。
- **参数**：`instance: ComponentInstance`（组件 `this`；`pageId` 形如 `"pageId:12"`，内部解析为数字帧 ID）`[源码]`。
- **返回**：`ViewContext`；同一帧重复获取返回同一实例 `[源码]`。
- **示例**：

```js
this._viewCtx = wx.modelContext.getViewContext(this)
```

- **来源**：`[官方]` `[源码]` `[demo]`

### 3.13 ViewContext.getDimensions

```ts
viewContext.getDimensions(): Dimensions   // { minHeight, maxHeight, width }
```

- **功能**：获取卡片可用尺寸信息（对应卡片宽高比 4:1～1:1 约束）`[官方]`。
- **返回**：`Dimensions`（缺省各字段 0）`[源码]`。
- **来源**：`[官方]` `[源码]`

### 3.14 ViewContext.openDetailPage

```ts
viewContext.openDetailPage(option: OpenDetailPageOption): Promise<ErrMsgResult>
// OpenDetailPageOption: { url: string }  — query 内联进 url
```

- **功能**：从卡片拉起半屏页面。**只能在原子组件内调用（原子接口内不可调）** `[官方]`。
- **参数**：`option: OpenDetailPageOption`（见 1.3）——`url` 页面路径可内联 query（`path?key=value`）；demo 用绝对路径（首 `/`）`[demo]` `[源码]`。

> ⚠️ **差异**：官方 02 篇示例写 `{path, query}` 两字段 `[官方]`；**源码实现只读 `option.url`**（`(0,y.iQ)(env, r.url)`）`[源码]`，demo 全部用 `{url}` 且可运行 `[demo]`。**按 `{url}` 使用**（差异表 D1）。

- **返回**：`Promise<ErrMsgResult>`，成功 `errMsg: 'openDetailPage:ok'`；失败 `openDetailPage:fail too soon since last openDetailPage`（**距上次调用 < 3000ms 冷却**）或无手势拒绝 `[源码]`。
- **行为与限制** `[源码]`：必须用户 tap 手势内调用；成功后向半屏页发送 `agentDetailPageOpened`（jsonrpc 消息，携带 `agentDetailPageId/appId/pageId`）；半屏页进入场景值 **1433/1434** `[官方]`。
- **示例**：

```js
this._viewCtx.openDetailPage({ url: '/packageDetail/pages/sku-picker?drinkId=3' })
```

- **来源**：`[官方]` `[源码]` `[demo]`

### 3.15 ViewContext.preloadDetailPage

```ts
viewContext.preloadDetailPage(option: OpenDetailPageOption): Promise<ErrMsgResult>
```

- **功能**：预加载半屏页面（提前下载分包），提升打开速度 `[官方]`。
- **参数**：`option: OpenDetailPageOption`（同 3.14，源码读 `url`）`[源码]`。
- **返回**：`Promise<ErrMsgResult>`，成功 `errMsg: 'preloadDetailPage:ok'`；分包下载失败 reject `preloadDetailPage:fail ... subpackage download failed` `[源码]`。
- **行为与限制**：无手势要求（预加载可提前做）；内部依赖 `__glassEaselAdapter__`，不可用时 reject `[源码]`。
- **示例**：

```js
this._viewCtx.preloadDetailPage({ url: '/packageDetail/pages/sku-picker' })
```

- **来源**：`[官方]` `[源码]`

### 3.16 ViewContext.closeDetailPage

```ts
viewContext.closeDetailPage(option?: CloseDetailPageOption): Promise<ErrMsgResult>
// CloseDetailPageOption: { closeAll?: boolean }
```

- **功能**：关闭半屏页面。`closeAll: true` 且当前卡片处于半屏态时，先调 `DismissHalfScreenCard` 收起半屏卡片，再调 `CloseAgentDetailPage` `[源码]`。
- **适用上下文**：② 原子组件环境。**官方文档未记载此 API**（差异表 D10）。
- **返回**：`Promise<ErrMsgResult>`，成功 `errMsg: 'closeDetailPage:ok'` `[源码]`。
- **示例**：

```js
this._viewCtx.closeDetailPage({ closeAll: true })
```

- **来源**：`[源码]`（未公开）

### 3.17 ViewContext.expirePreviousCards

```ts
viewContext.expirePreviousCards(filter?: ExpireFilter): Promise<ErrMsgResult>
```

- **功能**：把**当前卡片之前**渲染的卡片置为过期（不含自身）；仅原子组件内可调 `[官方]`。
- **参数**：`filter: ExpireFilter`（同 3.5）；实现为 `expirePreviousCards({excludeFrameId: 当前帧, filter})` `[源码]`。
- **语义细节** `[源码]`：被排除帧的 `createTime` 之后的卡片不会被过期（严格「之前」）；仅 `expirable: true` 的卡片生效；被 ban 的帧标记过期但延迟 emit（等 unban）。
- **返回**：`Promise<ErrMsgResult>`，成功 `errMsg: 'expirePreviousCards:ok'` `[源码]`。
- **示例**：

```js
this._viewCtx.expirePreviousCards()
this._viewCtx.expirePreviousCards({ componentPaths: ['components/weather-card/index'] })
```

- **来源**：`[官方]` `[源码]`

### 3.18 ViewContext.setRelatedPage

```ts
viewContext.setRelatedPage(option: SetRelatedPageOption): Promise<ErrMsgResult>
// SetRelatedPageOption: { path?, query?, appId?, envVersion? }
```

- **功能**：设置卡片标题栏右上角「进入小程序」入口关联的页面与 query `[官方]`。
- **参数**：`option: SetRelatedPageOption`（四字段 `path` / `query` / `appId` / `envVersion` 均可选，类型定义见 1.3）`[源码]`。`path` 未提供时沿用 mcp.json `components[].pagePath` 静态声明；`query` 首部 `?`/`&` 自动剥离后拼接。

- **返回**：`Promise<ErrMsgResult>`，成功 `errMsg: 'setRelatedPage:ok'`；失败：`fail view not bindable` / `fail frame not found` / `fail relatedPage not configured in toolMeta and arguments`（未声明静态 pagePath 且未传 path）`[源码]`。
- **约束**：`path` 可带固定 query；进入场景值 **1442/1443** `[官方]`。

> ⚠️ **差异**：官方 02 篇另有 `setRelatedPageQuery({city})` 写法 `[官方]`，**源码与 demo 均无此方法**，统一用 `setRelatedPage`（差异表 D3）。

- **示例**：

```js
this._viewCtx.setRelatedPage({ query: `orderId=${sc.orderId}` })   // path 沿用 mcp.json 声明
this._viewCtx.setRelatedPage({ path: 'pages/weather/index', query: 'city=shenzhen' })
```

- **来源**：`[官方]` `[源码]` `[demo]`

### 3.19 ViewContext.updateModelContext

```ts
viewContext.updateModelContext(param: UpdateModelContentParam): Promise<ErrMsgResult>
// UpdateModelContentParam: { content: TextContent[] }
```

- **功能**：把用户在卡片上的交互选择以文本同步给模型，保证后续回答接得上 `[官方]`。
- **适用上下文**：② 原子组件环境。
- **参数**：`param.content: TextContent[]`——非空数组，**每项必须 `type:'text'` 且 `text` 非空**（源码逐项校验，含其他类型即整单拒绝）`[官方]` `[源码]`。
- **返回**：`Promise<ErrMsgResult>`，成功 `errMsg: 'updateModelContext:ok'`；失败 `updateModelContext:fail throttled` 等 `[源码]`。
- **行为与限制** `[源码]` `[官方]`：
  - **必须在 tap 事件回调内同步调用**（异步/定时器中无手势会被拒绝）；
  - **500ms 节流**；
  - 源码按帧的 `toolCallId` 上行，绑定的帧必须有 toolCall 上下文。
- **示例**：

```js
this._viewCtx.updateModelContext({ content: [{ type: 'text', text: '用户选择了深圳' }] })
```

- **来源**：`[官方]` `[源码]`

### 3.20 wx.onAgentHandoff / wx.offAgentHandoff

```ts
wx.onAgentHandoff(callback: AgentHandoffCallback): void
wx.offAgentHandoff(): void
// AgentHandoffCallback: (event: HandoffEvent) => void
// HandoffEvent: { pageId: string, path: string, query: string, payload?: any }
```

- **功能**：页面接力（Handoff）。AI 输出小程序卡片，用户点击进入你的页面，接力数据经此事件送达 `[官方]`。
- **适用上下文**：④ 小程序/接力页（WAService 环境）。
- **参数**：`callback: AgentHandoffCallback`，事件 `HandoffEvent` 四字段类型定义见 1.5 `[源码]` `[demo]`。要点：`pageId` 形如 `"pageId:12"`（源码拼 `pageId:` 前缀，demo 直接作 map key）；`query` 为**未解码的原始 query 字符串**——源码内置警告「需自行 decodeURIComponent 后使用」`[源码]`；`payload` 为 `handoff.payload` 透传，**可能缺失，接力页需兼容** `[demo]`。

- **返回**：`void`。
- **行为与限制**：
  - **版本**：3.16.1 基础库无此 API（全文件无 `onAgentHandoff`），3.17.2 存在 `[源码]`；官方口径 iOS 8.0.75 / 基础库 3.16.2 / 工具 nightly 2.02.2607032 `[官方]`；
  - 每次进入接力页触发一次；建议 `onLoad` 尽早注册、`onUnload` 注销 `[官方]`；
  - 事件派发在基础库 WAService 内（工具 app.asar 中无实现，属正常分发路径）`[源码]`。
- **配套**：原子接口返回 `handoff: HandoffResolver`（见 4.2）；mcp.json `apis[].pagePath` 声明接力页（暂不支持动态改）`[官方]`。
- **示例**：

```js
// app.js（尽早注册）
wx.onAgentHandoff(({ pageId, path, query, payload }) => {
  this.globalData.agentHandoffs[pageId] = { path, query, payload }
})
wx.offAgentHandoff()   // 注销
```

- **来源**：`[官方]` `[源码]` `[demo]`

### 3.21 wx.getDetailPageCloseButtonBoundingClientRect

```ts
wx.getDetailPageCloseButtonBoundingClientRect(): Rect   // { left, top, width, height }
```

- **功能**：半屏页面获取左上角关闭按钮位置，用于业务适配避让 `[官方]`。
- **适用上下文**：③ 半屏页面。基础库 3.16.1+ `[官方]`。
- **返回**：`Rect` `[官方]` `[源码]`。
- **来源**：`[官方]` `[源码]`

### 3.22 源码发现的其他 agent API（未公开文档化）

以下 API 在基础库 API 注册表与调用深度表中实证存在 `[源码]`，官方 AI 文档未记载，**生产使用前需自行验证**（签名 `[未验证]`）：

| API（推断签名） | 备注 |
|---|---|
| `wx.openAgent(option?): void` / `wx.openSubAgent(option?): void` | 打开 Agent 相关入口 |
| `wx.onAgentOpen(cb): void` / `wx.offAgentOpen(): void` | Agent 打开事件 |
| `wx.getAgentRuntime(): unknown` | 获取 Agent 运行时 |
| `wx.checkIsSupportAgent(): boolean` | 能力检测（调用深度 0，疑为同步） |
| `wx.navigateBackAgent(option?): void` | Agent 内返回（demo 环境亦有引用） |

- **来源**：`[源码]`（存在性），`[未验证]`（行为细节）

---

## 四、原子接口开发者契约

### 4.1 mcp.json · apis[] 声明

| 属性 | 必填 | 说明 | 来源 |
|---|---|---|---|
| `name` | 是 | 标识符，与 `index.js` 注册的原子接口函数名一致 | `[官方]` |
| `description` | 是 | 功能描述（模型选型与填参依据） | `[官方]` |
| `inputSchema` | 是 | 入参 JSON Schema（object）——决定 `AtomicApiHandler<TInput>` 的 `TInput` 形状 | `[官方]` |
| `outputSchema` | 建议填 | `structuredContent` 对应 schema（**不计入 mcp.json 体积**） | `[官方]` |
| `_meta.ui.componentPath` | 否 | 结果卡片组件路径（相对 SKILL 目录） | `[官方]` |
| `_meta.ui.pagePath` | 否 | demo 扩展写法：接口级关联页面（demo 中与 handoff 接力页配合） | `[demo]` |
| `pagePath` | 否 | Handoff 接力页路径（apis 级，暂不支持动态改） | `[官方]` |

- **多模态**：`inputSchema` 字段标注 `"format": "image" | "file"`，用户上传内容自动传入该字段，纯声明生效 `[官方]`。
- **体积**：mcp.json ≤ **24000 字符**（计算时除去 `outputSchema`、空格与换行）`[官方]`。

```json
{
  "apis": [{
    "name": "getWeather",
    "description": "获取指定城市的天气信息",
    "inputSchema": {
      "type": "object",
      "properties": { "city": { "type": "string", "description": "城市名称" } },
      "required": ["city"]
    },
    "outputSchema": { "type": "object", "properties": { "temperature": { "type": "number" } } },
    "_meta": { "ui": { "componentPath": "components/weather-card/index" } }
  }]
}
```

### 4.2 原子接口返回值（`AtomicApiResult`，类型见 1.2）

- **字段去向** `[官方]`：`isError`/`structuredContent`/`content` 进 LLM 上下文；`_meta` 对 LLM 不可见、传给原子组件；`isError:true` 时忽略 `structuredContent`、不渲染卡片。
- **强制出卡片**：`content` 追加「接下来为用户展示 XXX UI 卡片」引导 `[官方]`。
- **校验与限额（源码逐项校验）** `[源码]`：`_meta` 提供时必须为可序列化 object；`apiCalls` 必须为数组；`content`/`structuredContent`/`_meta`/`apiCalls` 各 ≤ **200KB**，违例报 `Atomic API return value invalid: ...`；handler 返回 `undefined` → `{isError:true, content:'Tool execution error: missing result'}`。
- **示例**（demo `searchDrinks`，含 handoff）`[demo]`：

```js
/** @type {AtomicApiHandler<{keyword?: string}>} */
async function searchDrinks({ keyword } = {}) {
  // …
  return {
    isError: false,
    content: [{ type: 'text', text: `已搜索到 ${matched.length} 款匹配饮品。请引导用户点击下方小程序卡片挑选。` }],
    structuredContent: { items, total: matched.length },
    handoff: { query: `keyword=${encodeURIComponent(keyword)}`, payload: { items: viewItems } },
    _meta: { viewItems }
  }
}
```

### 4.3 原子组件卡片约束（影响组件实现）

| 约束 | 值 | 来源 |
|---|---|---|
| 卡片高度 | 宽高比 4:1 ～ 1:1；初始化时决定、后续不可改 | `[官方]` |
| 交互事件 | 仅 tap / image load / image error | `[官方]` |
| 网络 / 云开发 / 定时器 | 默认禁用；需 `realtime: true` 声明（单独审核） | `[官方]` |
| 内置组件 | `view` / `text`（禁 user-select）/ `map`（禁拖放）/ `button`（禁 open-type）/ `image`（仅网络 png/jpg）/ `canvas`（仅 2d）/ `scroll-view`（仅横向） | `[官方]` |
| 其他 | 禁动画、禁打开小程序、禁 overflow-y；不可声明为虚拟组件 | `[官方]` |

### 4.4 mcp.json · components[] 声明

| 字段 | 类型 | 必填 | 说明 | 来源 |
|---|---|---|---|---|
| `path` | `string` | 是 | 组件路径（相对 SKILL 目录） | `[官方]` |
| `pagePath` | `string` | 是（关联页面必须配置） | 卡片标题栏入口关联的小程序页面 | `[官方]` |
| `realtime` | `boolean` | 否 | 实时动态组件（放开 wx.request / 定时器，需单独审核） | `[官方]` |
| `usage` | `string` | realtime 时建议 | 使用场景说明 | `[官方]` |
| `expirable` | `boolean` | 否 | 卡片可被过期，默认 false | `[官方]` |
| `expiredText` | `string` | 否 | 过期文案，默认「服务已过期」 | `[官方]` |
| `relatedPage` | `string` | 否 | **demo 实际写法**（等价 pagePath 语义；demo 四个组件均用此字段，可运行） | `[demo]` |

### 4.5 过期组件生命周期

```js
Component({
  methods: {
    onExpire() { /* 卡片被置过期时触发，清理定时器等 */ }
  }
})
```

- 过期时组件同时收到 `NotificationType.Expire` 事件（payload `{expiredText}`）`[源码]`，官方记载 `onExpire()` 生命周期方法 `[官方]`（两者可并存）。

---

## 五、声明式配置接口

### 5.1 app.json

```json
{
  "lazyCodeLoading": "requiredComponents",
  "agent": {
    "skills": [
      { "name": "drink", "description": "WeStoreCafe 点单场景：…", "path": "skills/drink-skill" }
    ],
    "pageMetadata": "page-meta.json"
  }
}
```

| 字段 | 位置 | 说明 | 来源 |
|---|---|---|---|
| `agent.skills[]` | agent 内 | Skill 声明：`name` / `description` / `path`；最多 **30 个** | `[官方]` `[demo]` |
| `agent.skills` 所在分包 | — | SKILL 须放**独立分包**（一个分包可放多个 SKILL）；demo 配 `"independent": true` | `[官方]` `[demo]` |
| `lazyCodeLoading` | 顶层 | 必须 `"requiredComponents"`（按需注入） | `[官方]` |
| `pageMetadata` | 顶层（官方写法）/ `agent.pageMetadata`（demo 实际写法，可运行） | 指向 page-meta.json | `[官方]` `[demo]` |
| `instruction` | agent 内（非必填） | 指向 AGENTS.md 全局提示词路径 | `[官方]` |

> ⚠️ `pageMetadata` 两种位置官方镜像与 demo 不一致（见第六节 D7）；以 demo 实跑形态为准时用 `agent.pageMetadata`。

### 5.2 page-meta.json（服务直达数据源）

| 字段 | 必填 | 说明 | 来源 |
|---|---|---|---|
| `path` | 是 | 页面路径，可带固定 query | `[官方]` |
| `name` | 是 | 页面标题 | `[官方]` |
| `description` | 是 | 功能描述（影响 AI 出卡准确度与评测得分） | `[官方]` |
| `query` | 否 | object 格式 JSON Schema | `[官方]` |

- 体积 ≤ **8000 字节** `[官方]`。
- **结构差异**：官方镜像示例为**顶层数组** `[{path, name, ...}]` `[官方]`；demo 实际为 `{"pages": [{...}]}` 包裹且可运行 `[demo]`（见第六节 D7）。

```json
{ "pages": [{ "path": "pages/home/home", "name": "WeStoreCafe 点单首页", "description": "…" }] }
```

### 5.3 AGENTS.md（全局提示词）

- 小程序级说明文件：服务范围、背景知识、回答风格、多 SKILL 关联关系 `[官方]`。
- 通过 `instruction` 字段指定路径（非必填）；≤ **10000 字节** `[官方]`。

### 5.4 SKILL 目录结构与限额

```
skills/drink-skill/
├── SKILL.md          # 业务说明（给 AI 读）；≤16000 字节，单文件不可引用其他 md
├── mcp.json          # 能力声明；≤24000 字符（除 outputSchema 与空白）
├── index.js          # 注册原子接口（createSkill + registerAPI / module.exports）
├── apis/             # 接口实现（建议目录）
└── components/       # 组件实现（建议目录）
```

| 限额 | 值 | 来源 |
|---|---|---|
| SKILL 数量 | ≤ 30 | `[官方]` |
| SKILL.md | ≤ 16000 字节 | `[官方]` |
| mcp.json | ≤ 24000 字符（除 outputSchema、空格、换行） | `[官方]` |
| AGENTS.md | ≤ 10000 字节 | `[官方]` |
| page-meta.json | ≤ 8000 字节 | `[官方]` |
| 接口返回 content / structuredContent / _meta / apiCalls | 各 ≤ 200KB | `[官方]` `[源码]` |
| followup api/call arguments | ≤ 2000 字符 | `[源码]` |
| 中间件链 + 接口执行 | 共享 300s 超时 | `[官方]` `[源码]` |

### 5.5 注册模式（index.js）

```js
// 模式 A：官方最简（module.exports 直接导出）[官方]
module.exports = { getWeather }

// 模式 B：createSkill + registerAPI（可用中间件，demo 采用）[官方] [demo]
const skill = wx.modelContext.createSkill('skills/drink-skill')
skill.use(authMiddleware)
skill.registerAPI('getWeather', getWeather)
```

---

## 六、源码与官方文档差异对照表

> 裁决规则：源码优先，以下差异点写代码时按「应以」列执行。

| # | 事项 | 官方文档 | 基础库源码 / demo 实证 | 应以 |
|---|---|---|---|---|
| D1 | `openDetailPage` 参数 | `{path, query}`（02 篇） | 源码只读 `option.url`；demo 用 `{url: 'path?key=v'}` 可运行 | `{url}`，query 内联 |
| D2 | `expireAllCards` filter | 07 篇 `{componentPaths, match}`；02 篇示例 `{componentPath}` 单数 | `{skillPath(前缀), componentPaths[](精确), match:'all'\|'latest'(默认 all)}` | 源码三字段 |
| D3 | 卡片关联页动态设置 | 02 篇 `setRelatedPageQuery({city})` | 无此方法；实际为 `setRelatedPage({path, query, appId?, envVersion?})`（07 篇与源码一致） | `setRelatedPage` |
| D4 | NotificationType | 4 值（Input/Result/Overflow/Expire） | 7 值（+Resize/Ban/UnBan） | 用官方 4 值，知悉隐藏 3 值 |
| D5 | `wx.onAgentHandoff` | iOS 8.0.75 / 基础库 3.16.2+ | 3.16.1 无、3.17.2 有（互证）；event.query 为未解码原始串 | 版本判断 + 自行 decode |
| D6 | components[] 关联页字段 | `pagePath` | demo 用 `relatedPage` 可运行 | 任一，官方审核以 `pagePath` 为准 |
| D7 | `pageMetadata` 位置 / page-meta.json 结构 | 顶层字段 / 顶层数组 | demo：`agent.pageMetadata` / `{"pages":[...]}` 可运行 | demo 形态（实跑验证） |
| D8 | sendFollowUpMessage content | 仅 text | 支持混入 `{type:'api/call', data:{name, arguments}}` 直接触发原子接口（≤2000 字符） | 需要卡片按钮直调接口时用 |
| D9 | 节流 / 冷却 / 手势 | 「短时间重复调用会被拒绝」（模糊） | updateModelContext / sendFollowUpMessage 500ms 节流；openDetailPage 3000ms 冷却；三者均要求 tap 手势链内 | 源码精确值 |
| D10 | `closeDetailPage` | 未记载 | viewContext 上存在 `{closeAll}` 参数实现 | 未公开能力，慎用 |
| D11 | 半屏页上行/重跑调用路径 | 直呼 `wx.modelContext.sendFollowUpMessage(...)` / `wx.modelContext.reapplyApiCall()`（08 篇 `wx.modelContext.sendFollowUpMessage(Object object)`、02 篇 :510/:556 示例） | 半屏页的 `wx.modelContext` **仅有 `getContext()`**，两个方法都须经 `wx.modelContext.getContext().xxx` 取得；demo 无半屏页实跑佐证 | 源码形态（`getContext()` 链式），见 3.9 / 3.11 |

---

## 附：证据索引（源码）

| 结论 | 文件（wxvpkg 解包） |
|---|---|
| `wx.modelContext` 命名空间工厂（createSkill/registerAPI/getContext/getViewContext/NotificationType/getSessionId/expireAllCards） | `WAAgentAppMainContext.js` @ ~1929012（3.17.2） |
| createSkill / registerAPI / use 实现（全局 handler 表 + 按 skillPath 中间件组） | `WAAgentAppMainContext.js` @ ~1917589 |
| 中间件链执行（ctx 内置 name/skillPath/arguments、next 单次、短路、超时包装、missing result） | `WAAgentAppSubContext.js` @ ~191460 起 |
| getContext（on/off/sendFollowUpMessage + 500ms 节流 + api/call） | `WAAgentAppMainContext.js` @ ~1920719 |
| getViewContext（openDetailPage/preloadDetailPage/closeDetailPage/expirePreviousCards/setRelatedPage/updateModelContext/getDimensions + 3000ms 冷却） | `WAAgentAppMainContext.js` @ ~1922913 起 |
| NotificationType 7 值枚举 | `WAAgentAppMainContext.js` module 6823（3.16.1/3.17.2 一致） |
| expirePreviousCards(appId, excludeFrameId, filter) 逐帧过滤语义 | `WAAgentBase.js` @ ~589736 |
| 返回值校验器（200KB 限额）+ followup api/call 2000 字符校验 | `WAAgentAppMainContext.js` @ ~2032397 |
| 半屏页 modelContext 形态 `{getContext:()=>({sendFollowUpMessage, reapplyApiCall})}` 与自动 closeDetailPage | `WAServiceMainContext.js` @ ~695095 / ~2887420 |
| wx.onAgentHandoff 事件形状（pageId/path/query/payload）+ query 未解码警告 | `WAServiceMainContext.js` @ ~2615101 |
| web-view H5 桥接分发表（sendFollowUpMessage / reapplyApiCall） | `WAServiceMainContext.js` @ ~1804356 |
| agent API 家族（openAgent/onAgentOpen/checkIsSupportAgent/navigateBackAgent 等）注册表 | `WAServiceMainContext.js` @ ~2953945 |
| 子上下文环境注入（getToolHandler/getMiddlewareChain/console/wx 挂载） | `WAAgentAppSubContext.js` @ ~2018044 / ~198628 |
| onAgentHandoff 3.16.1 缺失 / 3.17.2 存在 | 两版本 wxvpkg 全文件 grep 对比 |

> 解包位置（本机）：`~/Library/Application Support/微信开发者工具/d1e8765721a6c23d43b14c95b1843e6b/WeappVendor/{3.16.1,3.17.2}.wxvpkg`（wxapkg 同构格式，0xBE…0xED 头 + 大端索引）。

---

*最后更新：2026-09-07 · 基础库 3.16.1 / 3.17.2 源码实证 + 官方镜像快照 2026-07-21 + 仓库 demo 实跑 · 能力处于内测 beta*
