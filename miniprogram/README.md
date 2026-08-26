# 无锡重点关注企业商业动态 · 微信小程序

## 项目说明

本小程序是「无锡重点关注企业商业动态·每日参阅」网页版的微信小程序版本，功能完全一致：
- **当日动态**：每日精选 8-12 条重点企业商业动态，含事件详情与无锡关联点评
- **历史动态**：全量记录库（600+ 条），支持搜索、产业/类型/城市/企业筛选、Excel 下载
- **自动更新**：每日 7:30 自动搜索新闻、更新数据、重新部署，小程序无需改版即可获取最新内容

## 数据来源

小程序通过 `wx.request` 从已部署的云端拉取 `data.json`，该文件由每日自动化任务自动更新。

- 数据接口：`https://275c8bd5cae0494a8121ddc68ab822f5.app.workbuddy.link/data.json`
- Excel 下载：`https://275c8bd5cae0494a8121ddc68ab822f5.app.workbuddy.link/无锡头部企业商业动态.xlsx`

接口配置写在 `app.js` 的 `globalData` 中，如需修改直接编辑。

## 快速开始

### 1. 安装微信开发者工具

下载地址：https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html

### 2. 导入项目

- 打开微信开发者工具，选择「导入项目」
- 项目目录：选择本 `miniprogram` 文件夹
- AppID：选择「测试号」（touristappid）或输入你已注册的小程序 AppID
- 项目名称：随意，如「无锡企业商业动态」

### 3. 开发预览

导入后即可在模拟器中查看效果。如遇网络请求失败：

- 点击工具栏「详情」→「本地设置」→ 勾选「不校验合法域名、web-view（业务域名）、TLS 版本以及 HTTPS 证书」
- 这样在开发模式下即可正常拉取数据

### 4. 上线发布（需要正式 AppID）

如需正式发布小程序，需完成以下步骤：

1. **注册小程序账号**：前往 https://mp.weixin.qq.com 注册微信小程序，获取 AppID
2. **配置域名白名单**：登录小程序管理后台 → 开发管理 → 开发设置 → 服务器域名
   - **request 合法域名**添加：`https://275c8bd5cae0494a8121ddc68ab822f5.app.workbuddy.link`
   - **downloadFile 合法域名**添加：`https://275c8bd5cae0494a8121ddc68ab822f5.app.workbuddy.link`
3. **替换 AppID**：在 `project.config.json` 中将 `"appid": "touristappid"` 改为你的正式 AppID
4. **上传发布**：在开发者工具中点击「上传」，然后在管理后台提交审核

## 文件结构

```
miniprogram/
├── app.js                    # 全局配置（数据接口 URL）
├── app.json                  # 小程序配置（页面路由、导航栏）
├── app.wxss                  # 全局样式
├── project.config.json       # 开发者工具项目配置
├── sitemap.json              # 搜索索引配置
└── pages/
    └── index/
        ├── index.js          # 页面逻辑（数据加载、Tab切换、搜索筛选、链接复制、Excel下载）
        ├── index.json        # 页面配置
        ├── index.wxml        # 页面模板（当日动态卡片 + 历史动态列表 + 底部Tab）
        └── index.wxss        # 页面样式（rpx 响应式布局）
```

## 功能说明

| 功能 | 实现方式 |
|------|----------|
| 数据加载 | `wx.request` 拉取云端 data.json |
| Tab 切换 | 自定义底部 Tab Bar，当日动态 / 历史动态 |
| 搜索 | `input` 组件 + `bindinput` 实时过滤 |
| 筛选 | `picker` 组件，支持产业/类型/城市/企业四级筛选 |
| 查看原文 | 点击来源链接 → 复制 URL 到剪贴板（小程序限制无法直接打开外链） |
| 下载 Excel | `wx.downloadFile` + `wx.openDocument` |
| 下拉刷新 | `onPullDownRefresh` 重新拉取最新数据 |
| 分享 | `onShareAppMessage` 支持转发给微信好友 |

## 日常维护

小程序源码无需每日修改——数据更新由自动化任务自动完成：
1. 每日 7:30 自动搜索无锡重点企业新闻
2. 生成 new_data.json → 运行 update_page.py → 更新 index.html + data.json + Excel
3. 自动部署到云端，data.json 实时更新
4. 小程序打开即自动拉取最新数据

如需调整页面样式或功能，修改 `miniprogram/pages/index/` 下的文件后在开发者工具中重新上传即可。
