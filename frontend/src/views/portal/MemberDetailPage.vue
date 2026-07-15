<template>
  <PortalLayout>
    <section class="member-head">
      <div class="container member-head-inner">
        <RouterLink class="back-link portal-back-link" :to="returnTo">返回团队成员</RouterLink>
        <img :src="member?.avatar || '/site-icon.png'" :alt="member?.name || '团队成员'" />
        <div>
          <p class="section-kicker">团队成员</p>
          <h1>{{ member?.name || '团队成员' }}</h1>
          <span class="status-tag normal">{{ member?.role_label || '团队成员' }}</span>
          <p>{{ member?.research_direction || member?.profile || '研究方向待补充。' }}</p>
        </div>
      </div>
    </section>

    <section class="page-section">
      <div class="container detail-layout">
        <main class="card detail-card">
          <section>
            <h2>个人简介</h2>
            <template v-if="profileSections.length">
              <div v-for="section in profileSections" :key="section.title" class="profile-section">
                <h3 v-if="section.title">{{ section.title }}</h3>
                <p v-for="paragraph in section.paragraphs" :key="paragraph">{{ paragraph }}</p>
              </div>
            </template>
            <p v-else class="muted">个人简介可在内部平台“门户内容 - 团队成员”中维护。</p>
          </section>

          <section v-if="member?.experiences?.length">
            <h2>工作 / 科研经历</h2>
            <div v-for="item in member.experiences" :key="`${item.organization}-${item.position}`" class="timeline-row">
              <time>{{ dateRange(item.start_date, item.end_date) }}</time>
              <div>
                <strong>{{ item.organization }}</strong>
                <span>{{ item.position }}</span>
                <p v-if="item.description">{{ item.description }}</p>
              </div>
            </div>
          </section>

          <section v-if="member?.educations?.length">
            <h2>教育经历</h2>
            <div v-for="item in member.educations" :key="`${item.school}-${item.degree}`" class="timeline-row">
              <time>{{ dateRange(item.start_date, item.end_date) }}</time>
              <div>
                <strong>{{ item.school }}</strong>
                <span>{{ [item.degree, item.major].filter(Boolean).join(' · ') }}</span>
                <p v-if="item.description">{{ item.description }}</p>
              </div>
            </div>
          </section>
        </main>

        <aside class="card side-card">
          <dl>
            <div>
              <dt>身份头衔</dt>
              <dd>{{ member?.role_label || '-' }}</dd>
            </div>
            <div>
              <dt>研究方向</dt>
              <dd>{{ member?.research_direction || '-' }}</dd>
            </div>
            <div v-if="member?.email">
              <dt>邮箱</dt>
              <dd><a :href="`mailto:${member.email}`">{{ member.email }}</a></dd>
            </div>
            <div v-if="member?.destination">
              <dt>毕业去向</dt>
              <dd>{{ member.destination }}</dd>
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

import { fetchMember, type Member } from '../../api/publicPortal'
import { usePortalReturn } from '../../composables/usePortalReturn'
import PortalLayout from '../../layouts/PortalLayout.vue'

const route = useRoute()
const returnTo = usePortalReturn('/team')
const member = ref<Member | null>(null)

const sectionHeadings = new Set(['工作经历', '教育经历', '学术与社会服务', '人才与团队项目', '教学工作', '教改项目与论文', '出版书籍与教材', '国际会议报告', '团队与研究生指导'])

const profileSections = computed(() => {
  const blocks = (member.value?.profile || '')
    .split(/\n{2,}/)
    .map((item) => item.trim())
    .filter(Boolean)
  return blocks.map((block, index) => {
    const lines = block.split(/\n+/).map((item) => item.trim()).filter(Boolean)
    const first = lines[0] || ''
    if (sectionHeadings.has(first)) return { title: first, paragraphs: lines.slice(1) }
    return { title: index === 0 ? '' : first, paragraphs: index === 0 ? lines : lines.slice(1) }
  }).filter((section) => section.paragraphs.length)
})

function dateRange(start?: string | null, end?: string | null) {
  if (!start && !end) return '时间未填写'
  return `${start || '开始'} - ${end || '至今'}`
}

onMounted(async () => {
  try {
    member.value = await fetchMember(String(route.params.id))
  } catch {
    member.value = null
  }
})
</script>

<style scoped>
.member-head {
  border-bottom: 1px solid rgba(31, 61, 43, 0.1);
  padding: 32px 0;
  background: linear-gradient(90deg, rgba(234, 245, 238, 0.78), rgba(255, 255, 255, 0.96) 54%, rgba(248, 247, 242, 0.9));
}

.member-head-inner {
  display: grid;
  grid-template-columns: 118px minmax(0, 1fr);
  align-items: center;
  gap: 24px;
}

.back-link {
  grid-column: 1 / -1;
  justify-self: start;
  display: inline-flex;
  align-items: center;
  min-height: 36px;
  border: 1px solid rgba(0, 135, 60, 0.24);
  border-radius: var(--radius-sm);
  padding: 0 13px;
  background: rgba(255, 255, 255, 0.72);
  color: var(--color-cau-green);
  font-size: 14px;
  font-weight: 700;
  text-decoration: none;
}

.back-link::before {
  margin-right: 7px;
  content: "←";
}

.back-link:hover {
  border-color: var(--color-cau-green);
  background: var(--color-eco-green);
}

.member-head img {
  width: 118px;
  height: 118px;
  border: 1px solid rgba(31, 61, 43, 0.12);
  border-radius: 18px;
  object-fit: cover;
  background: #fff;
}

.member-head h1 {
  margin: 0 0 10px;
  color: var(--color-deep-green);
  font-size: clamp(30px, 3.2vw, 42px);
  font-weight: 650;
}

.member-head p:last-child {
  max-width: 860px;
  margin: 14px 0 0;
  color: var(--color-muted);
  line-height: 1.75;
}

.page-section {
  background: var(--color-rice);
}

.detail-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 300px;
  gap: 20px;
}

.detail-card,
.side-card {
  box-shadow: none;
}

.detail-card {
  display: grid;
  gap: 28px;
  padding: 28px;
}

.detail-card h2 {
  margin: 0 0 16px;
  color: var(--color-deep-green);
  font-size: 22px;
}

.detail-card p {
  margin: 0 0 14px;
  color: var(--color-text);
  line-height: 1.85;
}

.profile-section {
  border-top: 1px solid rgba(31, 61, 43, 0.08);
  padding-top: 16px;
}

.profile-section:first-child {
  border-top: 0;
  padding-top: 0;
}

.profile-section h3 {
  margin: 0 0 10px;
  color: var(--color-deep-green);
  font-size: 17px;
  font-weight: 650;
}

.muted {
  color: var(--color-muted) !important;
}

.timeline-row {
  display: grid;
  grid-template-columns: 150px minmax(0, 1fr);
  gap: 18px;
  border-top: 1px solid var(--color-line);
  padding: 16px 0;
}

.timeline-row time {
  color: var(--color-muted);
  font-size: 14px;
}

.timeline-row strong,
.timeline-row span {
  display: block;
}

.timeline-row strong {
  color: var(--color-deep-green);
}

.timeline-row span {
  margin-top: 4px;
  color: var(--color-muted);
}

.side-card {
  position: sticky;
  top: 96px;
  align-self: start;
  padding: 22px;
}

.side-card dl {
  display: grid;
  gap: 16px;
  margin: 0 0 20px;
}

.side-card dt {
  color: var(--color-muted);
  font-size: 13px;
}

.side-card dd {
  margin: 4px 0 0;
  color: var(--color-text);
}

@media (max-width: 860px) {
  .member-head-inner,
  .detail-layout,
  .timeline-row {
    grid-template-columns: 1fr;
  }

  .side-card {
    position: static;
  }
}
</style>
