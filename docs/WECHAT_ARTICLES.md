# 公众号速递

“公众号速递”聚合公众号文章的公开元数据，不复制文章全文。公开页只展示公众号名称、标题、封面、摘要、发布时间和微信原文链接。

## 添加公众号

网站编辑或系统管理员登录内部平台，进入“公众号速递 → 公众号”，点击“添加公众号”。

- `RSS`：填写公众号或合规聚合服务提供的 RSS 地址。
- `开放接口`：填写已获授权的 JSON 接口地址。
- `仅手动录入`：不联网同步，在“文章”页手动维护。

## 开放接口格式

接口可直接返回数组，也可在 `articles`、`items` 或 `data` 字段中返回数组。每个条目支持：

```json
{
  "id": "provider-article-id",
  "title": "文章标题",
  "url": "https://mp.weixin.qq.com/s/...",
  "summary": "简短摘要",
  "cover_image": "https://example.com/cover.jpg",
  "published_at": "2026-07-27T09:00:00+08:00"
}
```

`title`、`url` 为必填字段。发布时间缺失时使用同步时间。`id` 用于稳定去重；没有 `id` 时使用规范化原文链接去重。

如接口需要 Bearer Token，在服务器 `.env` 中配置令牌，例如：

```dotenv
WECHAT_API_TOKEN_EXAMPLE=replace-with-provider-token
```

随后在公众号表单的“接口令牌环境变量”中填写 `WECHAT_API_TOKEN_EXAMPLE`。不要把真实令牌填写在网页表单或提交到 GitHub。

## 定时同步

Celery Beat 默认每 30 分钟调用一次：

```text
apps.wechat_articles.tasks.sync_all_wechat_accounts
```

可在 `.env` 调整：

```dotenv
WECHAT_SYNC_INTERVAL_MINUTES=30
WECHAT_SYNC_TIMEOUT_SECONDS=30
```

修改后重启 `celery_worker` 和 `celery_beat`。手动点击“同步”或“同步全部”也会把任务提交给 Celery。

## 使用边界

- 不抓取公众号全文。
- 不处理微信登录、验证码或反爬限制。
- 不配置来源地址时，可一直使用后台手动录入。
- RSS 或开放接口未提供封面、摘要时，页面显示占位图或默认提示。
