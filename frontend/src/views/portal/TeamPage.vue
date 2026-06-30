<template>
  <PortalLayout>
    <section class="portal-page-head">
      <div class="container">
        <p class="section-kicker">Team</p>
        <h1>团队成员</h1>
        <p>课题组由导师、博士研究生、硕士研究生、毕业学生与合作成员共同构成，围绕农业资源环境问题开展团队协作研究。</p>
      </div>
    </section>
    <section class="page-section">
      <div class="container member-grid">
        <article v-for="member in displayMembers" :key="member.name" class="card member-card">
          <img :src="member.avatar" :alt="member.name" />
          <div>
            <h2>{{ member.name }}</h2>
            <span class="status-tag normal">{{ member.role_label }}</span>
            <p>{{ member.research_direction || member.profile || '研究方向待补充' }}</p>
            <small v-if="member.email">{{ member.email }}</small>
          </div>
        </article>
      </div>
    </section>
  </PortalLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import { fetchMembers, type Member } from '../../api/publicPortal'
import PortalLayout from '../../layouts/PortalLayout.vue'

const members = ref<Member[]>([])

const fallback = [
  { name: '团队负责人', role_label: '硕博导师', research_direction: '统筹微生物生态、有机废弃物资源转化与高值产品开发方向', profile: '', avatar: '/favicon.svg', email: '' },
  { name: '博士研究生', role_label: '博士生', research_direction: '围绕功能微生物、堆肥腐殖化与低碳转化机制开展研究', profile: '', avatar: '/favicon.svg', email: '' },
  { name: '硕士研究生', role_label: '硕士生', research_direction: '参与有机肥产品开发、养分循环与土壤生态评价', profile: '', avatar: '/favicon.svg', email: '' },
  { name: '毕业学生与合作成员', role_label: '团队网络', research_direction: '共同支撑资源利用、生态环境工程和农业应用场景研究', profile: '', avatar: '/favicon.svg', email: '' },
]

const displayMembers = computed(() => (members.value.length > 1 ? members.value : fallback))

onMounted(async () => {
  try {
    members.value = await fetchMembers()
  } catch {
    members.value = []
  }
})
</script>

<style scoped>
.portal-page-head {
  position: relative;
  border-bottom: 4px solid var(--color-cau-green);
  padding: 56px 0 42px;
  background:`n    linear-gradient(90deg, rgba(234, 245, 238, 0.96), rgba(255, 255, 255, 0.98) 56%, rgba(248, 247, 242, 0.96)),`n    radial-gradient(circle at 88% 26%, rgba(0, 135, 60, 0.08), transparent 28%),`n    var(--color-white);
}

.portal-page-head::before {
  position: absolute;
  top: 0;
  left: 0;
  width: 34%;
  height: 4px;
  content: "";
  background: var(--color-soil);
}

.portal-page-head h1 {
  margin: 0 0 14px;
  color: var(--color-deep-green);
  font-size: clamp(38px, 4.5vw, 56px);
  font-weight: 650;
}

.portal-page-head p:last-child {
  max-width: 780px;
  margin: 0;
  color: var(--color-muted);
  font-size: 17px;
  line-height: 1.8;
}

.portal-page-head .section-kicker {
  color: var(--color-cau-green);
}

.page-section {
  background: var(--color-rice);
}

.member-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
}

.member-card {
  display: grid;
  grid-template-columns: 58px 1fr;
  gap: 15px;
  border-color: rgba(31, 61, 43, 0.1);
  padding: 22px;
  box-shadow: none;
}

.member-card img {
  width: 58px;
  height: 58px;
  border-radius: 14px;
  object-fit: cover;
}

.member-card h2 {
  margin: 0 0 8px;
  color: var(--color-deep-green);
  font-size: 19px;
}

.member-card p {
  margin: 10px 0 0;
  color: var(--color-muted);
  font-size: 14px;
}

.member-card small {
  display: block;
  margin-top: 10px;
  color: var(--color-cau-green);
}

@media (max-width: 980px) {
  .member-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .member-grid {
    grid-template-columns: 1fr;
  }
}
</style>


