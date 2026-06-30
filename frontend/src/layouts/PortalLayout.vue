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
        <RouterLink to="/dashboard">内部平台</RouterLink>
      </nav>
    </header>
    <main>
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
  position: sticky;
  top: 0;
  z-index: 20;
  display: grid;
  grid-template-columns: auto 1fr;
  align-items: center;
  height: var(--nav-height);
  gap: 24px;
  border-top: 4px solid var(--color-cau-green);
  border-bottom: 1px solid var(--color-border);
  padding: 0 max(20px, calc((100vw - var(--container)) / 2));
  background: rgba(255, 255, 255, 0.96);
  backdrop-filter: blur(8px);
}

.portal-brand {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  min-width: 278px;
}

.brand-emblem {
  display: inline-flex;
  width: 44px;
  height: 44px;
  flex: 0 0 44px;
  overflow: hidden;
  border: 1px solid rgba(0, 135, 60, 0.18);
  border-radius: 50%;
  background: #fff;
  box-shadow: var(--shadow-flat);
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
  font-size: 18px;
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
  gap: 6px;
  color: var(--color-text);
  font-size: 14px;
  white-space: nowrap;
}

.portal-links a {
  position: relative;
  display: inline-flex;
  align-items: center;
  min-height: 38px;
  border-radius: 999px;
  padding: 0 12px;
  transition: color 160ms ease;
}

.portal-links a:hover,
.portal-links a.router-link-active {
  background: var(--color-eco-green);
  color: var(--color-cau-green);
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
  .portal-nav {
    grid-template-columns: 1fr auto;
    height: auto;
    min-height: var(--nav-height);
    padding-top: 12px;
    padding-bottom: 12px;
  }

  .portal-links {
    grid-column: 1 / -1;
    justify-content: flex-start;
    overflow-x: auto;
    padding-bottom: 4px;
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
