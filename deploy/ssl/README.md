# HTTPS

Place production certificates in this directory and add an Nginx `listen 443 ssl;` server block in `deploy/nginx/conf.d/labhub.conf`.

Recommended production options:

- Use a host-level reverse proxy such as Caddy or Traefik for automatic Let's Encrypt certificates.
- Or mount `fullchain.pem` and `privkey.pem` here and configure `ssl_certificate` and `ssl_certificate_key`.
