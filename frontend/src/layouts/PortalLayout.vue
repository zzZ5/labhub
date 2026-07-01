<template>
  <div class="portal-shell">
    <header class="portal-nav">
      <RouterLink class="portal-brand" to="/">
        <span class="brand-emblem">
          <img src="/site-icon.png" alt="中农雨磷" />
        </span>
        <span>
          <strong>中农雨磷</strong>
          <small>中国农业大学资源与环境学院</small>
        </span>
      </RouterLink>
      <nav class="portal-links" aria-label="主导航">
        <RouterLink to="/">首页</RouterLink>
        <RouterLink to="/research">研究方向</RouterLink>
        <RouterLink to="/team">团队成员</RouterLink>
        <RouterLink to="/publications">科研成果</RouterLink>
        <RouterLink to="/news">新闻活动</RouterLink>
        <RouterLink class="internal-entry" to="/dashboard">内部平台</RouterLink>
      </nav>
    </header>
    <main class="portal-main">
      <slot />
    </main>
    <footer class="portal-footer">
      <div class="container footer-grid">
        <div>
          <strong>中农雨磷</strong>
          <p>面向农业绿色发展与资源环境治理，开展微生物生态、有机废弃物资源转化与高值产品开发研究。</p>
        </div>
        <div class="footer-address">
          <span>中国农业大学资源与环境学院生态系</span>
          <span>北京市海淀区圆明园西路2号 中国农业大学西校区</span>
        </div>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.portal-shell {
  min-height: 100vh;
  background:
    linear-gradient(180deg, rgba(234, 245, 238, 0.36), rgba(248, 247, 242, 0) 360px),
    var(--color-rice);
}

.portal-nav {
  position: fixed;
  top: 0;
  right: 0;
  left: 0;
  z-index: 30;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: var(--nav-height);
  gap: 24px;
  border-bottom: 1px solid var(--color-border);
  padding: 0 max(20px, calc((100vw - var(--container)) / 2));
  background: #fff;
  box-shadow: 0 1px 0 rgba(31, 61, 43, 0.04);
}

.portal-main {
  padding-top: var(--nav-height);
}

.portal-brand {
  display: inline-flex;
  align-items: center;
  height: 100%;
  gap: 12px;
  min-width: 278px;
}

.brand-emblem {
  display: inline-flex;
  width: 40px;
  height: 40px;
  flex: 0 0 40px;
  overflow: hidden;
  border: 1px solid rgba(0, 135, 60, 0.18);
  border-radius: 50%;
  background: #fff;
}

.brand-emblem img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.portal-brand strong,
.portal-brand small {
  display: block;
}

.portal-brand strong {
  color: var(--color-deep-green);
  font-size: 17px;
  font-weight: 650;
}

.portal-brand small {
  color: var(--color-muted);
  font-size: 12px;
  line-height: 1.3;
}

.portal-links {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  height: 100%;
  gap: 22px;
  color: var(--color-text);
  font-size: 14px;
  white-space: nowrap;
}

.portal-links a {
  position: relative;
  display: inline-flex;
  align-items: center;
  height: 100%;
  min-height: 0;
  color: var(--color-text);
  font-weight: 600;
  transition:
    background 160ms ease,
    border-color 160ms ease,
    color 160ms ease;
}

.portal-links a::after {
  position: absolute;
  right: 0;
  bottom: -1px;
  left: 0;
  height: 2px;
  border-radius: 999px 999px 0 0;
  background: transparent;
  content: "";
}

.portal-links a:hover,
.portal-links a.router-link-active {
  color: var(--color-cau-green);
}

.portal-links a:hover::after,
.portal-links a.router-link-active::after {
  background: var(--color-cau-green);
}

.portal-links .internal-entry {
  height: 36px;
  min-height: 0;
  border: 1px solid rgba(0, 135, 60, 0.24);
  border-radius: var(--radius-sm);
  padding: 0 14px;
  color: var(--color-cau-green);
}

.portal-links .internal-entry::after {
  display: none;
}

.portal-links .internal-entry:hover,
.portal-links .internal-entry.router-link-active {
  border-color: var(--color-cau-green);
  background: var(--color-eco-green);
}

.portal-footer {
  background:
    linear-gradient(90deg, rgba(0, 135, 60, 0.22), transparent 46%),
    var(--color-deep-green);
  color: rgba(255, 255, 255, 0.86);
  padding: 46px 0;
}

.footer-grid {
  display: flex;
  justify-content: space-between;
  gap: 32px;
}

.footer-grid strong {
  display: block;
  color: #fff;
  font-size: 18px;
}

.footer-grid p {
  margin: 8px 0 0;
  max-width: 560px;
  color: rgba(255, 255, 255, 0.74);
  line-height: 1.7;
}

.footer-address {
  display: grid;
  gap: 8px;
  align-content: center;
  color: rgba(255, 255, 255, 0.78);
}

.footer-grid span {
  display: block;
  text-align: right;
  line-height: 1.6;
}

@media (max-width: 980px) {
  .portal-links {
    min-width: 0;
    gap: 18px;
    overflow-x: auto;
    padding-bottom: 4px;
  }

  .portal-links a {
    height: 100%;
  }
}

@media (max-width: 640px) {
  .portal-brand {
    min-width: 0;
  }

  .portal-brand small {
    display: none;
  }

  .footer-grid {
    flex-direction: column;
  }

  .footer-grid span {
    text-align: left;
  }
}
</style>
