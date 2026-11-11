# 论文原文与公众号入口

论文原文已合并到“公众号速递”，在同一页面切换“文章解读”和“论文原文”，与团队自身的“论文成果”区分。

公开入口：`/literature-digest?tab=papers`。旧链接 `/papers` 自动跳转到该入口，并保留查询参数。

## 后台录入

1. 网站编辑或管理员登录内部平台，进入“门户内容管理 → 公众号速递 → 论文原文”。
2. 点击“添加原文”，填写 DOI、选择 PDF（最多 50 MB），直接保存即可。支持粘贴 `https://doi.org/...` 链接。
3. 后台从 Crossref 自动获取原标题、作者、期刊、发表年份及 DOI 原文入口。也可先点“识别信息”预览。专题由标题与主题词规则推荐，无法判断时保留未分类；中文译名和公众号解读链接不自动编造。
4. 默认“仅提供原文入口”，已上传的 PDF 不会公开。需要分享文件时，选择允许分享的开放获取许可或已获授权，并填写依据。
5. 勾选“公开展示此文献”后保存。访客无需登录，即可检索公开条目，预览、下载允许分享的 PDF。

上传成功不等于获得转载权限。机构订阅下载、个人下载、仅限阅读的授权不等于可以向公众重新分发。没有分享依据时只提供原文链接。

其余字段及分享许可在“补充信息与分享设置（可选）”中。DOI 未被 Crossref 收录或连接失败时，不保存空白记录，可重试或展开后手动填写标题。已有标题的普通编辑不会强制重新联网获取。仅将 DOI 发给 Crossref 查询，不上传 PDF。

## 部署与菜单

正常部署前后端，执行数据库迁移：

```bash
docker compose -f docker-compose.prod.yml exec backend python manage.py migrate
```

用户提供的网站域名为 `https://labhub.cpolar.cn/`。部署完成后，公众号“获取原文”菜单填写 `https://labhub.cpolar.cn/literature-digest?tab=papers`。一般文章入口为 `https://labhub.cpolar.cn/literature-digest`。尚未执行线上部署或验证公网访问。

在手机微信里测试页面、中文/英文/DOI搜索及 PDF 阅读。微信部分版本可能需要浏览器打开文件；下载行为还需在实际手机验证。

若公众号后台不允许外链，使用本公众号的一篇“原文获取说明”，在其“阅读原文”中填写该网站地址，再将菜单关联到说明文章。是否允许直接外链以账号当前权限和后台提示为准。

## 文件安全

- PDF 保存在 `protected_media/original_papers/`，不放入可公开直连的 `/media/`。
- 所有预览和下载都经过公开状态、分享方式和许可说明检查。隐藏条目或撤回分享后，原接口返回 404。
- 不向访客返回存储路径。生产环境复用 Nginx 的 `internal` 文件通道。
- 移除文件、替换文件或删除条目不会主动清空磁盘文件；旧文件仍受保护，后续清理由独立运维流程处理。
- 这里只新增管理入口，没有自动导入本地历史 PDF、自动公开旧文件或修改公众号菜单。

## 验证

无 Docker 时可使用隔离 SQLite 测试，不连接项目数据库：

```powershell
.\.venv\Scripts\python.exe backend/manage.py test apps.wechat_articles --settings=config.settings.testing
```

前端检查：`npm run build`；浏览器测试：`npx playwright test original-papers.spec.ts`。
