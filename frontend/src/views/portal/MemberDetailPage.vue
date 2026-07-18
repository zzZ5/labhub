<template>
  <PortalLayout>
    <PortalDetailLayout
      :return-to="returnTo"
      return-label="返回团队成员"
      kicker="团队成员"
      :title="member?.name || '团队成员'"
      aside-title="成员信息"
    >
      <template v-if="member" #meta>
        <p class="meta-list">
          <span>{{ member.role_label || '团队成员' }}</span>
          <span v-if="member.research_direction">{{ member.research_direction }}</span>
        </p>
      </template>

      <template v-if="member">
        <div class="member-intro">
          <div class="member-avatar">
            <img v-if="member.avatar && !avatarFailed" :src="member.avatar" :alt="member.name" @error="avatarFailed = true" />
            <ImagePlaceholder v-else :label="`${member.name}暂无头像`" :initial="member.name" />
          </div>
          <p>{{ member.research_direction || member.profile || '研究方向暂未补充。' }}</p>
        </div>

        <div class="member-content">
          <section>
            <h2>个人简介</h2>
            <template v-if="profileSections.length">
              <div v-for="section in profileSections" :key="section.title" class="profile-section">
                <h3 v-if="section.title">{{ section.title }}</h3>
                <p v-for="paragraph in section.paragraphs" :key="paragraph">{{ paragraph }}</p>
              </div>
            </template>
            <p v-else class="muted">个人简介暂未补充。</p>
          </section>

          <section v-if="member.experiences?.length">
            <h2>工作与科研经历</h2>
            <div v-for="item in member.experiences" :key="`${item.organization}-${item.position}`" class="timeline-row">
              <time>{{ dateRange(item.start_date, item.end_date) }}</time>
              <div><strong>{{ item.organization }}</strong><span>{{ item.position }}</span><p v-if="item.description">{{ item.description }}</p></div>
            </div>
          </section>

          <section v-if="member.educations?.length">
            <h2>教育经历</h2>
            <div v-for="item in member.educations" :key="`${item.school}-${item.degree}`" class="timeline-row">
              <time>{{ dateRange(item.start_date, item.end_date) }}</time>
              <div><strong>{{ item.school }}</strong><span>{{ [item.degree, item.major].filter(Boolean).join(' · ') }}</span><p v-if="item.description">{{ item.description }}</p></div>
            </div>
          </section>
        </div>
      </template>
      <div v-else class="empty-panel">未找到该团队成员，内容可能已调整。</div>

      <template v-if="member" #aside>
        <dl>
          <div><dt>身份头衔</dt><dd>{{ member.role_label || '团队成员' }}</dd></div>
          <div v-if="member.email"><dt>邮箱</dt><dd><a :href="`mailto:${member.email}`">{{ member.email }}</a></dd></div>
          <div v-if="member.destination"><dt>去向</dt><dd>{{ member.destination }}</dd></div>
        </dl>
      </template>
    </PortalDetailLayout>
  </PortalLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import { fetchMember, type Member } from '../../api/publicPortal'
import { usePortalReturn } from '../../composables/usePortalReturn'
import PortalLayout from '../../layouts/PortalLayout.vue'
import PortalDetailLayout from '../../components/PortalDetailLayout.vue'
import ImagePlaceholder from '../../components/ImagePlaceholder.vue'

const route = useRoute()
const returnTo = usePortalReturn('/team')
const member = ref<Member | null>(null)
const avatarFailed = ref(false)
const sectionHeadings = new Set(['工作经历', '教育经历', '学术与社会服务', '人才与团队项目', '教学工作', '教改项目与论文', '出版书籍与教材', '国际会议报告', '团队与研究生指导'])

const profileSections = computed(() => {
  const blocks = (member.value?.profile || '').split(/\n{2,}/).map((item) => item.trim()).filter(Boolean)
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
.member-intro {
  display: grid;
  grid-template-columns: 144px minmax(0, 1fr);
  align-items: center;
  gap: 24px;
  border-bottom: 1px solid var(--color-line);
  background: linear-gradient(90deg, rgba(234, 245, 238, 0.38), rgba(255, 255, 255, 0));
  padding: 28px 32px;
}

.member-intro > p { margin: 0; color: var(--color-muted); font-size: 17px; line-height: 1.8; }
.member-avatar { width: 144px; overflow: hidden; border: 1px solid var(--color-border-quiet); border-bottom: 3px solid var(--color-cau-gold); border-radius: var(--radius-md); background: var(--color-panel-strong); }
.member-avatar img,
.member-avatar :deep(.image-placeholder) { width: 100%; }
.member-avatar img { display: block; width: 100%; height: auto; }
.member-avatar :deep(.image-placeholder) { aspect-ratio: 4 / 5; }

.member-content { display: grid; gap: 28px; padding: 28px 32px 34px; }
.member-content section + section { border-top: 1px solid var(--color-line); padding-top: 26px; }
.member-content h2 { position: relative; margin: 0 0 16px; padding-left: 13px; color: var(--color-deep-green); font-size: 22px; }
.member-content h2::before { position: absolute; top: 0.16em; bottom: 0.16em; left: 0; width: 3px; background: linear-gradient(180deg, var(--color-cau-green) 0 72%, var(--color-cau-gold) 72% 100%); content: ""; }
.member-content p { margin: 0 0 14px; color: var(--color-text); line-height: 1.85; }
.profile-section + .profile-section { border-top: 1px solid var(--color-line); margin-top: 16px; padding-top: 16px; }
.profile-section h3 { margin: 0 0 10px; color: var(--color-deep-green); font-size: 17px; }
.muted,
.empty-panel { color: var(--color-muted) !important; }
.empty-panel { padding: 28px; }

.timeline-row { display: grid; grid-template-columns: 150px minmax(0, 1fr); gap: 18px; border-top: 1px solid var(--color-line); padding: 16px 0; }
.timeline-row time { color: var(--color-muted); font-size: 14px; }
.timeline-row strong,
.timeline-row span { display: block; }
.timeline-row strong { color: var(--color-deep-green); }
.timeline-row span { margin-top: 4px; color: var(--color-muted); }

@media (max-width: 640px) {
  .member-intro { grid-template-columns: 92px minmax(0, 1fr); align-items: start; gap: 16px; padding: 22px; }
  .member-avatar { width: 92px; }
  .member-intro > p { font-size: 14px; line-height: 1.65; }
  .member-content { padding: 24px 22px 28px; }
  .timeline-row { grid-template-columns: 1fr; gap: 8px; }
}
</style>
