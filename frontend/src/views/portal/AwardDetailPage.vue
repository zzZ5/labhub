<template>
  <PortalLayout>
    <PortalResultDetail :return-to="returnTo" type-label="获奖成果" :title="award?.title || '获奖成果'" info-title="获奖信息">
      <template #meta><p class="meta-list"><span v-if="award?.award_date">{{ award.award_date.slice(0, 4) }}</span></p></template>
      <img v-if="award?.image" class="award-image" :src="award.image" :alt="award.title" />
      <section>
        <h2>成果说明</h2>
        <RichContent v-if="award?.description" :html="award.description" />
        <p v-else>成果说明待补充。</p>
      </section>
      <section v-if="award?.participants">
        <h2>参与人员</h2>
        <p class="muted">{{ award.participants }}</p>
      </section>
      <template #info>
        <dl>
          <div><dt>奖项等级</dt><dd>{{ award?.award_level || '-' }}</dd></div>
          <div><dt>获奖日期</dt><dd>{{ award?.award_date || '-' }}</dd></div>
          <div v-if="award?.image"><dt>图片大小</dt><dd>{{ imageSizeLabel }}</dd></div>
          <div v-if="award?.attachment"><dt>附件大小</dt><dd>{{ attachmentSizeLabel }}</dd></div>
          <div v-if="award?.updated_at"><dt>最近更新</dt><dd>{{ formatPortalDateTime(award.updated_at) }}</dd></div>
          <div><dt>浏览量</dt><dd>{{ award?.view_count || 0 }}</dd></div>
        </dl>
      </template>
      <template #actions>
        <FileActionLinks v-if="award?.image" :url="award.image" view-label="在线查看图片" download-label="下载图片" />
        <FileActionLinks :url="award?.attachment" view-label="在线查看附件" download-label="下载附件" />
      </template>
    </PortalResultDetail>
  </PortalLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import { fetchAward, type Award } from '../../api/publicPortal'
import { usePortalReturn } from '../../composables/usePortalReturn'
import PortalLayout from '../../layouts/PortalLayout.vue'
import PortalResultDetail from '../../components/PortalResultDetail.vue'
import FileActionLinks from '../../components/FileActionLinks.vue'
import RichContent from '../../components/RichContent.vue'
import { formatOptionalFileSize } from '../../utils/files'
import { formatPortalDateTime } from '../../utils/date'

const route = useRoute()
const returnTo = usePortalReturn('/publications')
const award = ref<Award | null>(null)

const imageSizeLabel = computed(() => formatOptionalFileSize(award.value?.image_size))
const attachmentSizeLabel = computed(() => formatOptionalFileSize(award.value?.attachment_size))

onMounted(async () => {
  award.value = await fetchAward(String(route.params.id || ''))
})
</script>

<style scoped>
.award-image {
  width: 100%;
  max-height: 420px;
  border-radius: var(--radius-md);
  object-fit: cover;
}
</style>
