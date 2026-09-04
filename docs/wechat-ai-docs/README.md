# 微信小程序 AI 开发模式文档（本地镜像）

本目录是微信小程序 AI 开发模式（"小微 AI"）官方文档站的本地镜像，用于离线查阅与引用。

- **来源站点**：https://developers.weixin.qq.com/miniprogram/dev/ai/
- **抓取时间**：2026-07-21
- **抓取方式**：`mcp__web_reader__webReader`（Markdown）+ 纯标准库 Python 下载图片
- **覆盖范围**：`/miniprogram/dev/ai/` 子树下的全部 11 个页面

## 目录结构

```
wechat-ai-docs/
├── README.md                       # 本索引
├── 01-guide.md                     # 能力介绍
├── 02-integration.md               # 接入方式
├── 03-operating-mechanism.md       # 运行机制
├── 04-debugging.md                 # 调试指南
├── 05-best-practices.md            # 最佳实践
├── 06-reference-component.md       # 组件支持列表
├── 07-reference-api.md             # API 支持列表
├── 08-reference-detail-page.md     # 半屏页面能力支持列表
├── 09-evaluation-guide.md          # 评测指南
├── 10-faq.md                       # 常见问题
├── 11-changelog.md                 # 更新日志
├── download_images.py              # 图片下载 & 链接改写脚本（可重复运行）
└── images/                         # 全部本地化图片（30 张）
```

## 文档索引（按侧边栏顺序）

1. [能力介绍](./01-guide.md)
2. [接入方式](./02-integration.md)
3. [运行机制](./03-operating-mechanism.md)
4. [调试指南](./04-debugging.md)
5. [最佳实践](./05-best-practices.md)
6. [组件支持列表](./06-reference-component.md)
7. [API 支持列表](./07-reference-api.md)
8. [半屏页面能力支持列表](./08-reference-detail-page.md)
9. [评测指南](./09-evaluation-guide.md)
10. [常见问题](./10-faq.md)
11. [更新日志](./11-changelog.md)

## 本地图片说明

- 正文中所有 `res8.wxqcloud.qq.com.cn/wxdoc/...` 域名下的正文图片（共 30 张）已下载到 `images/`，markdown 里的链接已改写为相对路径 `./images/<filename>`。
- 命名规范：`<page-slug>-<seq>-<sha1前8位>.<ext>`，防重名冲突。
- 已自动剔除 `res.wx.qq.com` 域名下的 UI 装饰图标（翻译按钮等）。
- 如有图片下载失败，对应 md 顶部会追加 `> 图片下载失败：<url>` 备注，保留原远程链接。
- 若需要重新下载，执行：`python3 download_images.py`（脚本带本地缓存，重复运行幂等）。
