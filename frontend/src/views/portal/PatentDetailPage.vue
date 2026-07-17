<template>
  <PortalLayout>
    <PortalResultDetail :return-to="returnTo" type-label="专利成果" :title="patent?.title || '专利成果'" info-title="专利信息">
      <section>
        <h2>发明人</h2>
        <p>{{ patent?.inventors || '发明人信息待补充。' }}</p>
      </section>
      <template #info>
        <dl>
          <div><dt>专利号</dt><dd>{{ patent?.patent_number || '-' }}</dd></div>
          <div><dt>状态</dt><dd>{{ patent?.status || '-' }}</dd></div>
          <div v-if="patent?.application_date"><dt>申请日期</dt><dd>{{ patent.application_date }}</dd></div>
          <div v-if="patent?.authorization_date"><dt>授权日期</dt><dd>{{ patent.authorization_date }}</dd></div>
          <div v-if="patent?.pdf_file"><dt>文件大小</dt><dd>{{ pdfSizeLabel }}</dd></div>
        </dl>
      </template>
      <template #actions>
        <FileActionLinks :url="patent?.pdf_file" view-label="在线查看 PDF" download-label="下载 PDF" />
      </template>
    </PortalResultDetail>
  </PortalLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import { fetchPatent, type Patent } from '../../api/publicPortal'
import { usePortalReturn } from '../../composables/usePortalReturn'
import PortalLayout from '../../layouts/PortalLayout.vue'
import PortalResultDetail from '../../components/PortalResultDetail.vue'
import FileActionLinks from '../../components/FileActionLinks.vue'
import { formatOptionalFileSize } from '../../utils/files'

const route = useRoute()
const returnTo = usePortalReturn('/publications')
const patent = ref<Patent | null>(null)

const pdfSizeLabel = computed(() => formatOptionalFileSize(patent.value?.pdf_file_size))

onMounted(async () => {
  patent.value = await fetchPatent(String(route.params.id || ''))
})
</script>
