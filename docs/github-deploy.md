# GitHub 简易部署

以下流程适合单台 Linux 服务器部署 LabHub。先用服务器 IP 跑通，后续再绑定域名和 HTTPS。

## 1. 服务器安装依赖

```bash
sudo apt update
sudo apt install -y git curl
curl -fsSL https://get.docker.com | sudo sh
sudo apt install -y docker-compose-plugin
sudo usermod -aG docker $USER
```

重新登录服务器后确认：

```bash
docker version
docker compose version
```

## 2. 拉取项目

```bash
cd /opt
git clone 你的GitHub仓库地址 labhub
cd /opt/labhub
```

## 3. 配置服务器环境变量

```bash
cp .env.production.example .env
nano .env
```

至少修改：

```env
DJANGO_SECRET_KEY=换成很长的随机字符串
DJANGO_ALLOWED_HOSTS=服务器IP,你的域名,localhost,127.0.0.1
DJANGO_CSRF_TRUSTED_ORIGINS=http://服务器IP,http://你的域名
POSTGRES_PASSWORD=换成强密码
ADMIN_EMAIL=baoju_liu@foxmail.com
ADMIN_PASSWORD=换成强密码
SITE_DOMAIN=服务器IP或你的域名
NGINX_HTTP_PORT=8088
```

如果暂时只用 HTTP/IP 访问，保持：

```env
DJANGO_SECURE_COOKIES=False
```

如果已经配置 HTTPS，改成：

```env
DJANGO_CSRF_TRUSTED_ORIGINS=https://你的域名
DJANGO_SECURE_COOKIES=True
```

## 4. 首次启动

```bash
bash deploy/scripts/init.sh
```

访问：

```text
http://服务器IP:8088/
http://服务器IP:8088/admin/
```

如果使用 cpolar，转发目标填写：

```text
http://127.0.0.1:8088
```

## 5. 以后更新

本地提交并推送 GitHub 后，在服务器执行：

```bash
cd /opt/labhub
bash deploy/scripts/deploy.sh
```

## 6. 只重启服务

如果只是修改了 `.env`，或想手动重启生产服务：

```bash
cd /srv/labhub
bash deploy/scripts/restart.sh
```

## 7. 常用命令

```bash
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f backend
docker compose -f docker-compose.prod.yml logs -f nginx
bash deploy/scripts/backup_db.sh
bash deploy/scripts/backup_media.sh
```

不要把服务器上的 `.env`、`media/`、`protected_media/` 提交到 GitHub。
