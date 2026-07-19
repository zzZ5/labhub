<template>
  <PortalLayout>
    <PortalResultDetail :return-to="returnTo" type-label="论文成果" :title="paper?.title || '论文详情'" info-title="论文信息">
      <template #meta>
        <p class="meta-list">
          <span>{{ paper?.year || '年份待补充' }}</span>
          <span v-if="paper?.journal">{{ paper.journal }}</span>
          <span v-if="paper?.doi">DOI: {{ paper.doi }}</span>
        </p>
      </template>
      <section>
        <h2>作者</h2>
        <p class="muted">{{ paper?.authors || '作者信息待补充' }}</p>
      </section>
      <section>
        <h2>摘要</h2>
        <RichContent v-if="paper?.abstract" :html="paper.abstract" />
        <p v-else>摘要待补充。</p>
      </section>
      <template #info>
        <dl>
          <div><dt>年份</dt><dd>{{ paper?.year || '-' }}</dd></div>
          <div><dt>期刊</dt><dd>{{ paper?.journal || '待补充' }}</dd></div>
          <div v-if="volumeIssuePages"><dt>卷期页</dt><dd>{{ volumeIssuePages }}</dd></div>
          <div v-if="paper?.jcr_partition || paper?.cas_partition"><dt>分区</dt><dd>{{ [paper?.jcr_partition, paper?.cas_partition].filter(Boolean).join(' / ') }}</dd></div>
          <div v-if="Number(paper?.impact_factor) > 0"><dt>影响因子</dt><dd>{{ paper?.impact_factor }}</dd></div>
          <div v-if="paper?.pdf_file"><dt>文件大小</dt><dd>{{ pdfSizeLabel }}</dd></div>
          <div v-if="paper?.updated_at"><dt>最近更新</dt><dd>{{ formatPortalDateTime(paper.updated_at) }}</dd></div>
          <div><dt>浏览量</dt><dd>{{ paper?.view_count || 0 }}</dd></div>
        </dl>
      </template>
      <template #actions>
        <a v-if="paper?.doi" class="doi-link" :href="doiUrl" target="_blank" rel="noreferrer">打开 DOI 页面</a>
        <FileActionLinks :url="paper?.pdf_file" view-label="在线查看 PDF" download-label="下载 PDF" />
      </template>
    </PortalResultDetail>
  </PortalLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import { fetchPublication, type Publication } from '../../api/publicPortal'
import { usePortalReturn } from '../../composables/usePortalReturn'
import PortalLayout from '../../layouts/PortalLayout.vue'
import PortalResultDetail from '../../components/PortalResultDetail.vue'
import FileActionLinks from '../../components/FileActionLinks.vue'
import RichContent from '../../components/RichContent.vue'
import { formatOptionalFileSize } from '../../utils/files'
import { formatPortalDateTime } from '../../utils/date'

const route = useRoute()
const returnTo = usePortalReturn('/publications')
const paper = ref<Publication | null>(null)

const doiUrl = computed(() => {
  if (!paper.value?.doi) return ''
  return paper.value.doi.startsWith('http') ? paper.value.doi : `https://doi.org/${paper.value.doi}`
})

const volumeIssuePages = computed(() => {
  if (!paper.value) return ''
  return [paper.value.volume, paper.value.issue, paper.value.pages].filter(Boolean).join(', ')
})

const pdfSizeLabel = computed(() => formatOptionalFileSize(paper.value?.pdf_file_size))

onMounted(async () => {
  paper.value = await fetchPublication(String(route.params.id || ''))
})
</script>

<style scoped>
.doi-link {
  display: flex;
  min-height: 40px;
  align-items: center;
  justify-content: center;
  margin-bottom: 9px;
  border: 1px solid rgba(0, 135, 60, 0.28);
  border-radius: var(--radius-sm);
  color: var(--color-cau-green);
  font-size: 14px;
  font-weight: 700;
}
</style>
