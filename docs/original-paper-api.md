# 论文原文自动同步 API

## 接口与权限

继续使用已有接口，不需要浏览器或后台表单：

- `POST /api/wechat/manage/papers/`：multipart，必填 `doi` 和 `pdf`，后台通过已有 Crossref 逻辑补全英文题名、作者、期刊和年份。
- `GET /api/wechat/manage/papers/?search=<DOI>`：上传前查重。
- `GET /api/wechat/manage/papers/<id>/`：回读结果。
- `POST /api/wechat/manage/papers/lookup/`：可选，提前识别元数据。

请求头为 `Authorization: Bearer <专用随机令牌>`。机器令牌仅适用于论文原文查询和新增；不能修改、删除、替换已有 PDF，也不能管理账号、门户、公众号或其他内容。现有网页会话登录和 CSRF 保护不变。服务端默认关闭机器认证。

## 一次性配置

在公众号项目的 Windows 终端运行：

```powershell
python scripts/configure_labhub_token.py
```

脚本只将随机令牌写入公众号项目已忽略的 `.env`，不打印令牌，不改变管理员密码，不访问浏览器；输出的是服务端所需的 SHA-256 校验值。已有令牌不会自动轮换。

服务器先获取这次代码，再在项目根目录运行（替换为上一步的 `server_hash`，不是原始令牌）：

```bash
bash deploy/scripts/configure-paper-upload-token.sh <server_hash>
```

该脚本仅更新生产 `.env` 中的 `LABHUB_PAPER_UPLOAD_TOKEN_SHA256` 并重建启动 backend，不删除卷、不重建数据库、不新建账号，不需要迁移。必须通过可信 HTTPS 地址调用接口。原始令牌留在上传客户端；勿提交、粘贴到聊天或写进日志。

撤销机器权限：清空服务器 `.env` 中的 `LABHUB_PAPER_UPLOAD_TOKEN_SHA256` 后重新创建 backend 容器。轮换时在客户端生成新的随机令牌，并同步更新服务器校验值。不要复用管理员密码作为令牌。

## 分享设置与核验

仅传 DOI 和 PDF 默认存为未公开，文件不开放下载。经用户明确要求公开时，另传 `is_visible=true`、适当的 `sharing` 和真实的 `rights_note`。站点操作授权不等于出版商转载许可，不能自动伪造 CC BY 或版权方授权。

同步脚本会回读管理记录、匿名公开记录、预览和下载响应头，并把匿名下载 PDF 的 SHA-256 与本地文件核对。重复 DOI 不再创建；请求结果不确定时先查服务器，不盲目重发。无 Token 或认证失败时明确停止，不自动切回浏览器填表或尝试管理员账号。
