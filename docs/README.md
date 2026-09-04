# docs 索引：小微 AI 架构研究

本目录汇集对微信「小微 AI」（小程序 AI 开发模式）的研究文档，按研究方法分为三条路线，互为印证。

## 路线一：源码实证（2026-09-03，本次交付）

从微信开发者工具 Nightly 版 `app.asar` 解包源码出发，先实证工具自身架构，再结合官方文档与业界范式反推客户端真实架构。

| 文档 | 性质 | 说明 |
|---|---|---|
| [devtools-agent-architecture.md](./devtools-agent-architecture.md) | L1 纯实证 | 开发者工具 Agent 架构：启动链路、SKILL 装配（`__agentData`）、webview 拓扑、NDJSON 协议链路、MagicBrush 渲染模拟、handoff 模拟、调试设施。含 3 分钟速读、术语表与各章「人话」导语，新手可按导读路径阅读（配图 [devtools-agent-architecture.html](./devtools-agent-architecture.html)） |
| [xiaowei-architecture-whitepaper.md](./xiaowei-architecture-whitepaper.md) | 两层结构反推（L1/L2/P/L3 分级） | 小微真实架构白皮书 v3-draft：第一部分基准层（官方三方+实证协议+端云五方+三方消歧）；第二部分三大块细化（后台内部 v4 假设/客户端四区/端云通道 T1·T2，含方案空间活文档）；第三部分专题（协议对比/Handoff/GUI 通道专章/业界对照/存疑）。配图 [xiaowei-architecture.html](./xiaowei-architecture.html)（1 总览+3 细化面板，实线=基准/虚线=假设） |

**核心方法**：工具 = 真实架构的「简化版 + 调试增强版」，反推 = 剔除增强 + 还原简化 + 置信度分级。

## 路线二：黑盒对话探测（2026-09-02 及之前，历史文档）

通过与小微直接对话问答，探测其行为边界并归纳架构。与路线一交叉印证。

| 文档 | 说明 |
|---|---|
| [reverse-wechat-ai/架构推测_v2.1.md](./reverse-wechat-ai/架构推测_v2.1.md) | 逆向报告终版（P1/P2/P3 约 25 问探测，置信度标注） |
| [reverse-wechat-ai/微信小微_架构图.md](./reverse-wechat-ai/微信小微_架构图.md) | 基于探测结果的 ASCII 架构图 |
| [reverse-wechat-ai/架构层探测_问答结果.md](./reverse-wechat-ai/架构层探测_问答结果.md) | 原始问答档案 |
| [reverse-wechat-ai/](./reverse-wechat-ai/) | 其余过程稿（v1/v2）、专项问答（capability-qa/mini-app） |
| [小微AI小程序接入技术报告.md](./小微AI小程序接入技术报告.md) | 面向接入方的产品流程报告（含交互截图） |

## 路线三：官方文档镜像

| 文档 | 说明 |
|---|---|
| [wechat-ai-docs/](./wechat-ai-docs/) | 小程序 AI 开发模式官方文档站本地镜像（11 篇，2026-07-21 抓取），含接入指南、运行机制、API/组件支持列表、FAQ、changelog |

## 关键交叉印证点

| 结论 | 路线一（源码） | 路线二（黑盒） | 路线三（官方） |
|---|---|---|---|
| 原子接口跑在独立 JS 上下文 | instanceframe 与逻辑层共用 asLoader | 探测确认环境隔离 | 「独立 JS 环境」明示 |
| 原子组件用 glass-easel 渲染 | 工具用 MagicBrush 模拟替代 | — | 文档明示 glass-easel |
| SKILL 声明随请求上行 | `skill_data` 报文实证 | — | 文档未明示（实证补强） |
| handoff 场景值体系 | 工具模拟 1454 + 场景值表 1433-1443 | 探测到卡片入口行为 | 场景值 1433/1434/1435/1436/1442/1443 |
| 接力单向不可回话 | demo README + 工具链路 | 探测确认 | 文档未明示（实证补强） |
