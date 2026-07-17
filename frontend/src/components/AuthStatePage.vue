<template>
  <section class="auth-state-page">
    <RouterLink class="auth-state-back" to="/">返回官网</RouterLink>
    <div class="card auth-state-card">
      <div class="auth-state-mark" aria-hidden="true"></div>
      <p class="section-kicker">{{ eyebrow }}</p>
      <h1>{{ title }}</h1>
      <p class="auth-state-description">{{ description }}</p>
      <div class="auth-state-actions"><slot /></div>
    </div>
  </section>
</template>

<script setup lang="ts">
defineProps<{ eyebrow: string; title: string; description: string }>()
</script>

<style scoped>
.auth-state-page {
  display: grid;
  min-height: 100vh;
  place-items: center;
  padding: 72px 28px 36px;
  background: var(--color-rice);
}

.auth-state-back {
  position: fixed;
  top: 24px;
  left: 28px;
  min-height: 36px;
  border: 1px solid rgba(0, 135, 60, 0.2);
  border-radius: var(--radius-sm);
  padding: 6px 12px;
  background: rgba(255, 255, 255, 0.86);
  color: var(--color-cau-green);
  font-size: 14px;
  font-weight: 650;
}

.auth-state-card {
  position: relative;
  width: min(600px, 100%);
  overflow: hidden;
  padding: 34px 36px;
  box-shadow: var(--shadow-soft);
}

.auth-state-card:hover {
  border-color: var(--color-border);
  transform: none;
}

.auth-state-mark {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  width: 4px;
  background: var(--color-cau-green);
}

.auth-state-card h1 {
  margin: 0 0 12px;
  color: var(--color-deep-green);
  font-size: clamp(28px, 4vw, 34px);
  font-weight: 650;
  line-height: 1.25;
}

.auth-state-description {
  margin: 0;
  color: var(--color-muted);
  line-height: 1.8;
}

.auth-state-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 25px;
}

.auth-state-actions :deep(a),
.auth-state-actions :deep(button) {
  min-height: 40px;
}

@media (max-width: 560px) {
  .auth-state-page {
    align-items: start;
    padding: 92px 16px 28px;
  }

  .auth-state-back {
    top: 18px;
    left: 16px;
  }

  .auth-state-card {
    padding: 28px 24px;
  }

  .auth-state-actions {
    display: grid;
  }
}
</style>
