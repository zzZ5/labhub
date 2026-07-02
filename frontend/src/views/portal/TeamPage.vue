<template>
  <PortalLayout>
    <section class="portal-page-head">
      <div class="container">
        <p class="section-kicker">团队成员</p>
        <h1>团队成员</h1>
        <p>课题组由导师、博士研究生、硕士研究生、毕业学生与合作成员共同构成，围绕农业资源环境问题开展团队协作研究。</p>
      </div>
    </section>
    <section class="page-section">
      <div class="container">
        <div class="team-filter card">
          <el-input v-model="keyword" clearable placeholder="搜索姓名、研究方向、邮箱" />
          <el-select v-model="roleFilter" clearable placeholder="身份头衔">
            <el-option v-for="role in roleOptions" :key="role.value" :label="role.label" :value="role.value" />
          </el-select>
          <span>{{ filteredMembers.length }} / {{ displayMembers.length }} 人</span>
        </div>
        <div class="member-grid">
          <RouterLink v-for="member in pagedMembers" :key="member.name" class="card member-card" :to="member.to">
            <img :src="member.avatar" :alt="member.name" />
            <div>
              <h2>{{ member.name }}</h2>
              <span class="status-tag normal">{{ member.role_label || '团队成员' }}</span>
              <p>{{ member.research_direction || member.profile || '研究方向待补充' }}</p>
              <small v-if="member.email">{{ member.email }}</small>
            </div>
          </RouterLink>
        </div>
        <div v-if="!filteredMembers.length" class="card empty-panel">暂无公开团队成员，请在内部平台“门户内容”中维护。</div>
        <div v-if="totalPages > 1" class="team-pager">
          <button type="button" :disabled="page === 1" @click="page -= 1">上一页</button>
          <span>第 {{ page }} / {{ totalPages }} 页</span>
          <button type="button" :disabled="page === totalPages" @click="page += 1">下一页</button>
        </div>
      </div>
    </section>
  </PortalLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'

import { fetchMembers, type Member } from '../../api/publicPortal'
import PortalLayout from '../../layouts/PortalLayout.vue'

const members = ref<Member[]>([])
const keyword = ref('')
const roleFilter = ref('')
const page = ref(1)
const pageSize = 12

const displayMembers = computed(() => members.value.map((member) => ({
  ...member,
  to: member.id ? `/team/${member.id}` : '/team',
})))
const roleOptions = computed(() => {
  const map = new Map<string, string>()
  displayMembers.value.forEach((member) => {
    const title = member.role_label || member.role_type || '团队成员'
    map.set(title, title)
  })
  return Array.from(map.entries()).map(([value, label]) => ({ value, label }))
})
const filteredMembers = computed(() => {
  const q = keyword.value.trim().toLowerCase()
  return displayMembers.value.filter((member) => {
    const roleKey = member.role_label || member.role_type || '团队成员'
    const haystack = `${member.name} ${roleKey} ${member.research_direction} ${member.profile} ${member.email}`.toLowerCase()
    return (!roleFilter.value || roleKey === roleFilter.value) && (!q || haystack.includes(q))
  })
})
const totalPages = computed(() => Math.max(1, Math.ceil(filteredMembers.value.length / pageSize)))
const pagedMembers = computed(() => filteredMembers.value.slice((page.value - 1) * pageSize, page.value * pageSize))

onMounted(async () => {
  try {
    members.value = await fetchMembers()
  } catch {
    members.value = []
  }
})

watch([keyword, roleFilter], () => {
  page.value = 1
})

watch(totalPages, (total) => {
  if (page.value > total) page.value = total
})
</script>

<style scoped>
.portal-page-head {
  position: relative;
  border-bottom: 1px solid rgba(31, 61, 43, 0.1);
  padding: 28px 0 24px;
  background:
    linear-gradient(90deg, rgba(234, 245, 238, 0.76), rgba(255, 255, 255, 0.96) 48%, rgba(248, 247, 242, 0.92)),
    var(--color-white);
}

.portal-page-head::before {
  position: absolute;
  top: 30px;
  bottom: 26px;
  left: max(20px, calc((100vw - var(--container)) / 2));
  width: 3px;
  border-radius: 999px;
  content: "";
  background: var(--color-cau-green);
}

.portal-page-head .container {
  padding-left: 22px;
}

.portal-page-head h1 {
  margin: 0 0 9px;
  color: var(--color-deep-green);
  font-size: clamp(28px, 3.1vw, 38px);
  font-weight: 650;
  line-height: 1.18;
}

.portal-page-head p:last-child {
  max-width: 820px;
  margin: 0;
  color: var(--color-muted);
  font-size: 15px;
  line-height: 1.65;
}

.portal-page-head .section-kicker {
  color: var(--color-cau-green);
}

.page-section {
  padding-top: 30px;
  background: var(--color-rice);
}

.team-filter {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 180px auto;
  align-items: center;
  gap: 12px;
  margin-bottom: 18px;
  padding: 14px;
  box-shadow: none;
}

.team-filter span {
  color: var(--color-muted);
  font-size: 14px;
  white-space: nowrap;
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
  color: inherit;
  text-decoration: none;
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

.team-pager {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 14px;
  margin-top: 22px;
  color: var(--color-muted);
  font-size: 14px;
}

.team-pager button {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: 8px 14px;
  background: #fff;
  color: var(--color-text);
  cursor: pointer;
}

.team-pager button:disabled {
  cursor: not-allowed;
  opacity: 0.45;
}

.empty-panel {
  padding: 28px;
  color: var(--color-muted);
  box-shadow: none;
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

  .team-filter {
    grid-template-columns: 1fr;
  }
}
</style>


