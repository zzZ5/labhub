<template>
  <PortalLayout>
    <PortalResultDetail :return-to="returnTo" type-label="科研项目" :title="project?.title || '科研项目'" info-title="项目信息">
      <section>
        <h2>项目说明</h2>
        <p>{{ project?.description || '项目说明待补充。' }}</p>
      </section>
      <template #info>
        <dl>
          <div><dt>项目编号</dt><dd>{{ project?.project_number || '未公开' }}</dd></div>
          <div><dt>项目来源</dt><dd>{{ project?.funding_source || '-' }}</dd></div>
          <div><dt>团队 / 负责人</dt><dd>{{ project?.principal_investigator || '-' }}</dd></div>
          <div><dt>状态</dt><dd>{{ project?.status || '-' }}</dd></div>
          <div v-if="project?.amount && Number(project.amount) > 0"><dt>经费</dt><dd>{{ amountLabel }}</dd></div>
          <div v-if="project?.start_date || project?.end_date"><dt>周期</dt><dd>{{ [project?.start_date, project?.end_date].filter(Boolean).join(' 至 ') }}</dd></div>
        </dl>
      </template>
    </PortalResultDetail>
  </PortalLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import { fetchProject, type Project } from '../../api/publicPortal'
import { usePortalReturn } from '../../composables/usePortalReturn'
import PortalLayout from '../../layouts/PortalLayout.vue'
import PortalResultDetail from '../../components/PortalResultDetail.vue'

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
