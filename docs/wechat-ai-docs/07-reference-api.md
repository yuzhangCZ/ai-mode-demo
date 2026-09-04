> 源页面：https://developers.weixin.qq.com/miniprogram/dev/ai/reference/api.html
> 抓取时间：2026-07-21

# API 支持列表

API 的支持情况在原子接口环境与原子组件环境下有所不同，以下从新增 API 和原有 API 两个维度分别列出所有支持的 API。

## 新增 API

小程序 AI 开发模式下新增的 API 都在 `wx.modelContext` 命名空间下。

**原子接口支持的如下：**

1. 创建 Skill：`wx.modelContext.createSkill(skillPath: string)`
   - 注册原子接口：`skill.registerAPI('name', handler)`
   - 注册中间件：`skill.use(Middleware)`
2. 获取会话 ID：`wx.modelContext.getSessionId()`
3. 设置所有组件过期：`wx.modelContext.expireAllCards({ componentPaths, match })`

**原子组件支持的如下：**

1. 关联小程序页面：`wx.modelContext.getViewContext(this).setRelatedPage({ path, query })`
2. 上行消息：`wx.modelContext.getContext().sendFollowUpMessage()`
3. 更新卡片状态并同步给模型：`wx.modelContext.getViewContext(this).updateModelContext({content: [{type: 'text', text: '用户选择了xxx'}]})`
4. 半屏页面：
   - 打开半屏页面：`wx.modelContext.getViewContext(this).openDetailPage({ url })`
   - 预加载半屏页面：`wx.modelContext.getViewContext(this).preloadDetailPage({ url })`
   - 半屏页面更新卡片：`wx.modelContext.getContext().reapplyApiCall({ arguments })`
5. 原子组件过期态：
   - 设置所有组件过期：`wx.modelContext.expireAllCards({ componentPaths, match })`
   - 设置之前的组件过期：`wx.modelContext.getViewContext(this).expirePreviousCards({ componentPaths, match })`
6. 原子组件接收事件：`wx.modelContext.getViewContext(this).on(NotificationType, calback)`
   - 原子接口入参：`wx.modelContext.NotificationType.Input`
   - 原子接口出参：`wx.modelContext.NotificationType.Result`
   - 内容溢出事件：`wx.modelContext.NotificationType.Overflow`
   - 过期事件：`wx.modelContext.NotificationType.Expire`

## 原有 API

小程序原有部分 API 支持在小程序 AI 开发模式下调用，但原子接口与原子组件可调用的接口有所不同，支持情况如下表：

> 若某个分类下的 API 都支持，细分 API 则不会全部列出，请跳转到接口文档查看
>
> 原则上，不会再提供原有的已标为废弃版本的 API

| 分类 | API | 原子接口 | 原子组件 |
| --- | --- | --- | --- |
| 基础 | wx.env | 支持 | 支持 |
| 登录 | wx.login | 支持 | 不支持（需声明 scope.dynamic） |
|  | wx.checkSession | 支持 | 不支持（需声明 scope.dynamic） |
| 发起请求 | wx.request | 支持 | 不支持（需声明 scope.dynamic） |
| 网络 | 全部 | 支持 | 不支持 |
| 云开发 | 全部 | 支持 | 不支持 |
| 位置 | wx.getLocation | 支持 | 不支持 |
|  | wx.getFuzzyLocation | 支持 | 不支持 |
|  | wx.openLocation | 不支持 | 支持 |
|  | wx.chooseLocation | 不支持 | 支持 |
| 加密 | wx.getUserCryptoManager | 支持 | 不支持 |
| 系统 | wx.getDeviceInfo | 支持 | 支持 |
|  | wx.getAppBaseInfo | 支持 | 支持 |
|  | wx.getWindowInfo | 支持 | 支持 |
| 数据缓存 | wx.getStorage | 支持 | 支持 |
|  | wx.setStorage | 支持 | 支持 |
|  | wx.batchGetStorage | 支持 | 支持 |
|  | wx.batchSetStorage | 支持 | 支持 |
|  | wx.getStorageInfo | 支持 | 支持 |
|  | wx.removeStorage | 支持 | 支持 |
|  | wx.clearStorage | 支持 | 支持 |
|  | wx.getStorage | 支持 | 支持 |
|  | wx.setStorageSync | 支持 | 支持 |
|  | wx.getStorageSync | 支持 | 支持 |
| 分享 | wx.shareAppMessage | 不支持 | 支持（需在 tap 事件回调中调用） |
| 手机号 | wx.getPhoneNumber | 支持 | 不支持 |
|  | wx.getRealtimePhoneNumber | 支持 | 不支持 |
| 图片视频 | wx.chooseMedia | 不支持 | 支持 |
|  | wx.chooseMessageFile | 不支持 | 支持 |
|  | wx.previewMedia | 不支持 | 支持 |
|  | wx.saveImageToPhotosAlbum | 不支持 | 支持 |
|  | wx.getImageInfo | 支持 | 不支持 |
| 人脸核身 | wx.startFacialRecognitionVerify | 支持 | 不支持 |
|  | wx.startFacialRecognitionVerifyAndUploadVideo | 支持 | 不支持 |
| 支付 | wx.requestPayment | 不支持 | 支持 |
|  | wx.requestVirtualPayment | 不支持 | 支持 |
|  | wx.verifyPaymentPassword | 不支持 | 支持 |
|  | wx.requestJointPayment | 不支持 | 支持 |
|  | wx.openPublicServicePayment | 不支持 | 支持 |
|  | wx.openBusinessView businessType=openPublicServicePayment | 不支持 | 支持 |
|  | wx.openBusinessView businessType=trafficInvestList | 不支持 | 支持 |
|  | wx.openBusinessView businessType=wxpayPapayIndex | 不支持 | 支持 |
| 微信支付分 | wx.openBusinessView businessType=wxpayScoreUse | 不支持 | 支持 |
|  | wx.openBusinessView businessType=wxpayScoreEnable | 不支持 | 支持 |
| 订阅消息 | wx.requestSubscribeMessage | 支持 | 不支持 |
| 授权 | wx.authorize | 支持 | 不支持 |
| 电话 | wx.makePhoneCall | 不支持 | 支持 |
| 扫码 | wx.scanCode | 不支持 | 支持 |
| 交互 | wx.showToast | 不支持 | 支持 |
|  | wx.hideToast | 不支持 | 支持 |
| 城市服务 | wx.openBusinessView businessType=wxCityWxpayAuth | 不支持 | 支持 |
| 收货地址 | wx.chooseAddress | 不支持 | 支持 |
| 设置 | wx.openSetting | 不支持 | 支持 |
|  | wx.getSetting | 支持 | 不支持 |
| WiFi | 全部 | 支持 | 不支持 |
| 蓝牙-通用 | 全部 | 支持 | 不支持 |
| 蓝牙-低功耗 中心设备 | 全部 | 支持 | 不支持 |
| 蓝牙-低功耗 外围设备 | 全部 | 支持 | 不支持 |
| WebSocket | 全部 | 支持 | 不支持 |
| mDNS | 全部 | 支持 | 不支持 |
| 加速计 | 全部 | 支持 | 不支持 |
| 罗盘 | 全部 | 支持 | 不支持 |
| 设备方向 | 全部 | 支持 | 不支持 |
| 陀螺仪 | 全部 | 支持 | 不支持 |
| TCP 通信 | 全部 | 支持 | 不支持 |
| UDP 通信 | 全部 | 支持 | 不支持 |
| 上传 | 全部 | 支持 | 不支持 |
| 下载 | 全部 | 支持 | 支持 |
| 文件 | wx.openDocument | 不支持 | 支持 |
| 地图 | 全部，除了 MapContext.openMapApp | 不支持 | 支持 |
| 微信运动 | wx.getWeRunData | 支持 | 不支持 |
| 发票 | wx.chooseInvoiceTitle | 不支持 | 支持 |
|  | wx.chooseInvoice | 不支持 | 支持 |
| 账号信息 | wx.getAccountInfoSync | 支持 | 支持 |
| 人脸检测 | 全部 | 支持 | 不支持 |
| 振动 | 全部 | 不支持 | 支持 |
| 隐私信息授权 | wx.getPrivacySetting | 不支持 | 支持 |
|  | wx.openPrivacyContract | 支持 | 支持 |

---

*2026 年 06 月 29 日*

*添加 viewContext.updateModelContext 的使用描述*
