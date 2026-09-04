> 源页面：https://developers.weixin.qq.com/miniprogram/dev/ai/reference/detail-page.html
> 抓取时间：2026-07-21

# 半屏页面能力支持列表

半屏页面与小程序页面的运行环境基本一致，但部分接口与组件能力受限，不支持的能力分类如下：

- 跳转类 API
- 路由
- 聊天工具类 API
- 地图类 API
- 视频号相关能力
- 微信客服相关能力
- 微信表情
- 广告相关能力

## 新增 API

### `wx.modelContext.sendFollowUpMessage(Object object)`

> 基础库 3.16.1 开始支持

上行消息接口，在半屏页面里，可以使用该接口上行文本、图片，关闭半屏页面回到对话区域。

#### 参数

**Object object**

| 属性 | 类型 | 默认值 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| type | string |  | 是 | 上行内容类型："text" / "image" |
| text | string |  | type=text 时必填 | type 为 "text" 时文本内容 |
| fileid | string |  | type=image 时必填 | type 为 "image" 时图片内容（云存储 fileid） |

### `wx.getDetailPageCloseButtonBoundingClientRect()`

> 基础库 3.16.1 开始支持

获取左上角关闭按钮相对于页面左上角的位置信息，用于业务适配关闭按钮位置。

#### 返回值

**Object object**

| 属性 | 类型 | 说明 |
| --- | --- | --- |
| left | number | 关闭按钮左边界坐标 |
| top | number | 关闭按钮上边界坐标 |
| width | number | 关闭按钮宽度 |
| height | number | 关闭按钮高度 |

## 受限 API

以下接口在半屏页面中不可用：

### 跳转类 API

| API |
| --- |
| wx.openNfcDetails |
| wx.openEmbeddedMiniProgram |
| wx.navigateToMiniProgram |
| wx.openBusinessView |
| wx.openCustomerServiceChat |
| wx.openPublicServicePayment |
| wx.openSetting |

### 路由 API

| API |
| --- |
| wx.reLaunch |
| wx.redirectTo |
| wx.navigateTo |
| wx.navigateBack |
| wx.switchTab |

### 聊天工具类 API

| API |
| --- |
| wx.requestSubscribeMessage |
| wx.shareAppMessage |

### 地图类 API

| API |
| --- |
| wx.openLocation |
| wx.chooseLocation |

### 视频号相关能力

| API |
| --- |
| wx.openChannelsUserProfile |
| wx.openChannelsLiveExperience |
| wx.openChannelsActivity |
| wx.getChannelsLiveInfo |
| wx.getChannelsLiveNoticeUnreadCount |
| wx.reserveChannelsLive |
| wx.openChannelsEventEnvelope |
| wx.openChannelsAtPublish |
| wx.launchChannelsMiniprogramLike |

### 微信客服相关能力

| API |
| --- |
| wx.openCustomerServiceChat |
| <button open-type="contact"> |

### 微信表情

| API |
| --- |
| wx.createInnerAudioContext |

### 广告相关能力

| 组件 / API |
| --- |
| <ad> |
| <ad-custom> |
| <official-account> |
| <rewarded-video-ad> |
| <ad-interaction> |
