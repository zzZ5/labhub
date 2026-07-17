<template>
  <PortalLayout>
    <section class="detail-head">
      <div class="container">
        <ReturnLink class="back-link portal-back-link" :to="returnTo">返回科研成果</ReturnLink>
        <p class="section-kicker">获奖成果</p>
        <h1>{{ award?.title || '获奖成果' }}</h1>
      </div>
    </section>
    <section class="page-section">
      <div class="container detail-layout">
        <main class="card detail-card">
          <img v-if="award?.image" class="award-image" :src="award.image" :alt="award.title" />
          <h2>成果说明</h2>
          <p>{{ award?.description || '成果说明待补充。' }}</p>
          <section v-if="award?.participants">
            <h2>参与人员</h2>
            <p class="muted">{{ award.participants }}</p>
          </section>
        </main>
        <aside class="card side-card">
          <strong>获奖信息</strong>
          <dl>
            <div>
              <dt>奖项等级</dt>
              <dd>{{ award?.award_level || '-' }}</dd>
            </div>
            <div>
              <dt>获奖日期</dt>
              <dd>{{ award?.award_date || '-' }}</dd>
            </div>
            <div v-if="award?.image">
              <dt>图片大小</dt>
              <dd>{{ imageSizeLabel }}</dd>
            </div>
            <div v-if="award?.attachment">
              <dt>附件大小</dt>
              <dd>{{ attachmentSizeLabel }}</dd>
            </div>
          </dl>
          <a v-if="award?.attachment" class="primary-link" :href="award.attachment" target="_blank" rel="noreferrer">查看附件</a>
          <a v-if="award?.attachment" class="outline-link" :href="award.attachment" download>下载附件</a>
        </aside>
      </div>
    </section>
  </PortalLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import { fetchAward, type Award } from '../../api/publicPortal'
import { usePortalReturn } from '../../composables/usePortalReturn'
import PortalLayout from '../../layouts/PortalLayout.vue'
import ReturnLink from '../../components/ReturnLink.vue'
import { formatOptionalFileSize } from '../../utils/files'

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
  display: grid;
  gap: 22px;
  padding: 30px 34px;
}

.award-image {
  width: 100%;
  max-height: 420px;
  border-radius: var(--radius-md);
  object-fit: cover;
}

.detail-card h2 {
  margin: 0 0 10px;
  color: var(--color-deep-green);
  font-size: 21px;
}

.detail-card p {
  margin: 0;
  color: var(--color-text);
  font-size: 16px;
  line-height: 1.85;
}

.detail-card .muted {
  color: var(--color-muted);
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
  margin: 18px 0;
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

.primary-link,
.outline-link {
  display: flex;
  justify-content: center;
  border-radius: var(--radius-sm);
  padding: 9px 14px;
  font-weight: 700;
}

.primary-link {
  background: var(--color-cau-green);
  color: #fff;
}

.outline-link {
  margin-top: 10px;
  border: 1px solid rgba(0, 135, 60, 0.28);
  color: var(--color-cau-green);
}

@media (max-width: 900px) {
  .detail-layout {
    grid-template-columns: 1fr;
  }
}
</style>
