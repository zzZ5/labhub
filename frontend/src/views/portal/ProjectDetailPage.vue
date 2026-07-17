<template>
  <PortalLayout>
    <section class="detail-head">
      <div class="container">
        <ReturnLink class="back-link portal-back-link" :to="returnTo">返回科研成果</ReturnLink>
        <p class="section-kicker">科研项目</p>
        <h1>{{ project?.title || '科研项目' }}</h1>
      </div>
    </section>
    <section class="page-section">
      <div class="container detail-layout">
        <main class="card detail-card">
          <h2>项目说明</h2>
          <p>{{ project?.description || '项目说明待补充。' }}</p>
        </main>
        <aside class="card side-card">
          <strong>项目信息</strong>
          <dl>
            <div>
              <dt>项目编号</dt>
              <dd>{{ project?.project_number || '未公开' }}</dd>
            </div>
            <div>
              <dt>项目来源</dt>
              <dd>{{ project?.funding_source || '-' }}</dd>
            </div>
            <div>
              <dt>团队/负责人</dt>
              <dd>{{ project?.principal_investigator || '-' }}</dd>
            </div>
            <div>
              <dt>状态</dt>
              <dd>{{ project?.status || '-' }}</dd>
            </div>
            <div v-if="project?.amount && Number(project.amount) > 0">
              <dt>经费</dt>
              <dd>{{ amountLabel }}</dd>
            </div>
            <div v-if="project?.start_date || project?.end_date">
              <dt>周期</dt>
              <dd>{{ [project?.start_date, project?.end_date].filter(Boolean).join(' 至 ') }}</dd>
            </div>
          </dl>
        </aside>
      </div>
    </section>
  </PortalLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import { fetchProject, type Project } from '../../api/publicPortal'
import { usePortalReturn } from '../../composables/usePortalReturn'
import PortalLayout from '../../layouts/PortalLayout.vue'
import ReturnLink from '../../components/ReturnLink.vue'

const route = useRoute()
const returnTo = usePortalReturn('/publications')
const project = ref<Project | null>(null)

const amountLabel = computed(() => {
  const amount = Number(project.value?.amount || 0)
  if (!amount) return ''
  return `${amount.toLocaleString('zh-CN')} 万元`
})

onMounted(async () => {
  project.value = await fetchProject(String(route.params.id || ''))
})
</script>

<style scoped>
.detail-head {
  border-bottom: 1px solid rgba(31, 61, 43, 0.1);
  padding: 34px 0 30px;
  background: rgba(255, 255, 255, 0.72);
}

.back-link {
  display: inline-flex;
  margin-bottom: 14px;
  color: var(--color-cau-green);
  font-weight: 700;
}

.detail-head h1 {
  max-width: 980px;
  margin: 0;
  color: var(--color-deep-green);
  font-size: clamp(26px, 3.2vw, 38px);
  font-weight: 650;
  line-height: 1.25;
}

.page-section {
  background: var(--color-rice);
}

.detail-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 310px;
  gap: 24px;
}

.detail-card,
.side-card {
  border-color: rgba(31, 61, 43, 0.1);
  box-shadow: none;
}

.detail-card {
  padding: 30px 34px;
}

.detail-card h2 {
  margin: 0 0 12px;
  color: var(--color-deep-green);
  font-size: 21px;
}

.detail-card p {
  margin: 0;
  color: var(--color-text);
  font-size: 16px;
  line-height: 1.85;
}

.side-card {
  align-self: start;
  padding: 22px;
}

.side-card strong {
  color: var(--color-deep-green);
  font-size: 18px;
}

.side-card dl {
  display: grid;
  gap: 14px;
  margin: 18px 0 0;
}

.side-card dt {
  color: var(--color-muted);
  font-size: 13px;
}

.side-card dd {
  margin: 4px 0 0;
  color: var(--color-text);
  line-height: 1.55;
}

@media (max-width: 900px) {
  .detail-layout {
    grid-template-columns: 1fr;
  }
}
</style>
