<template>
  <PortalLayout>
    <PortalPageHeader title="团队成员" description="汇聚不同研究背景的师生，在开放交流与协作实践中共同推进科研工作。" />
    <section class="page-section">
      <div class="container">
        <div class="role-filter" role="group" aria-label="按身份头衔筛选">
          <button type="button" :class="{ active: !roleFilter }" @click="roleFilter = ''">全部成员</button>
          <button v-for="role in roleOptions" :key="role.value" type="button" :class="{ active: roleFilter === role.value }" @click="roleFilter = role.value">
            {{ role.label }}
          </button>
        </div>
        <div class="team-filter card">
          <el-input v-model="keyword" clearable placeholder="搜索姓名、头衔或研究方向">
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
          <span class="result-count">共 {{ filteredMembers.length }} 位</span>
        </div>
        <div class="member-grid">
          <RouterLink v-for="member in pagedMembers" :key="member.name" class="card member-card" :to="member.to">
            <div class="member-photo">
              <img v-if="member.avatar && !imageErrors.has(member.id)" :src="member.avatar" :alt="member.name" @error="imageErrors.add(member.id)" />
              <ImagePlaceholder v-else :label="`${member.name}暂无头像`" :initial="member.name" />
            </div>
            <div class="member-content">
              <div class="member-name-row">
                <h2>{{ member.name }}</h2>
                <ArrowRight />
              </div>
              <span class="member-role">{{ member.role_label || '团队成员' }}</span>
              <p>{{ member.research_direction || member.profile || '研究方向待补充' }}</p>
            </div>
          </RouterLink>
        </div>
        <div v-if="!filteredMembers.length" class="card empty-panel">暂无公开团队成员，请在内部平台“门户内容”中维护。</div>
        <AppPagination :page="page" :total-pages="totalPages" @change="setPage" />
      </div>
    </section>
  </PortalLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { ArrowRight, Search } from '@element-plus/icons-vue'
import { useRoute, useRouter } from 'vue-router'

import { fetchMembers, type Member } from '../../api/publicPortal'
import AppPagination from '../../components/AppPagination.vue'
import ImagePlaceholder from '../../components/ImagePlaceholder.vue'
import PortalPageHeader from '../../components/PortalPageHeader.vue'
import PortalLayout from '../../layouts/PortalLayout.vue'

const members = ref<Member[]>([])
const route = useRoute()
const router = useRouter()
const queryText = (value: unknown) => typeof value === 'string' ? value : ''
const queryPage = (value: unknown) => Math.max(1, Number.parseInt(queryText(value), 10) || 1)
const keyword = ref(queryText(route.query.q))
const roleFilter = ref(queryText(route.query.role))
const page = ref(queryPage(route.query.page))
const pageSize = 12
const imageErrors = reactive(new Set<number>())

const displayMembers = computed(() => members.value.map((member) => ({
  ...member,
  to: member.id ? { path: `/team/${member.id}`, query: { from: route.fullPath } } : '/team',
})))
const roleOptions = computed(() => {
  const map = new Map<string, string>()
  displayMembers.value.forEach((member) => {
    const title = member.role_label || member.role_type || '团队成员'
    map.set(title, title)
  })
  return Array.from(map.entries())
    .map(([value, label]) => ({ value, label }))
    .sort((a, b) => roleRank(a.label) - roleRank(b.label) || a.label.localeCompare(b.label, 'zh-CN'))
})

function roleRank(label: string) {
  const order = ['硕博导师', '博士后', '博士生', '硕士生', '本科生', '其他成员']
  const index = order.findIndex((item) => label.includes(item))
  return index < 0 ? order.length : index
}
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

function syncQuery() {
  const query: Record<string, string> = {}
  if (page.value > 1) query.page = String(page.value)
  if (keyword.value.trim()) query.q = keyword.value.trim()
  if (roleFilter.value) query.role = roleFilter.value
  void router.replace({ path: '/team', query })
}

function setPage(value: number) {
  page.value = Math.min(Math.max(1, value), totalPages.value)
}

watch([keyword, roleFilter], () => {
  page.value = 1
  syncQuery()
})

watch(page, syncQuery)

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

.role-filter {
  display: flex;
  gap: 22px;
  margin-bottom: 14px;
  overflow-x: auto;
  border-bottom: 1px solid var(--color-line);
  scrollbar-width: none;
}

.role-filter::-webkit-scrollbar {
  display: none;
}

.role-filter button {
  flex: 0 0 auto;
  min-height: 40px;
  border: 0;
  border-bottom: 2px solid transparent;
  padding: 0 2px;
  background: transparent;
  color: var(--color-muted);
  cursor: pointer;
  font-size: 14px;
}

.role-filter button:hover,
.role-filter button.active {
  border-bottom-color: var(--color-cau-green);
  color: var(--color-cau-green);
  font-weight: 650;
}

.team-filter {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
  border-color: rgba(31, 61, 43, 0.09);
  padding: 12px;
  background: rgba(255, 255, 255, 0.86);
  box-shadow: none;
}

.result-count {
  min-width: 84px;
  color: var(--color-muted);
  font-size: 14px;
  text-align: right;
  white-space: nowrap;
}

.member-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
}

.member-card {
  display: grid;
  grid-template-columns: 112px minmax(0, 1fr);
  min-height: 160px;
  overflow: hidden;
  border-color: rgba(31, 61, 43, 0.1);
  padding: 0;
  background: rgba(255, 255, 255, 0.96);
  color: inherit;
  text-decoration: none;
  box-shadow: var(--shadow-soft);
}

.member-photo {
  min-height: 160px;
  overflow: hidden;
  background: var(--color-panel-strong);
}

.member-photo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center top;
  transition: transform 240ms ease;
}

.member-content {
  display: grid;
  align-content: center;
  gap: 7px;
  min-width: 0;
  padding: 18px 16px;
}

.member-name-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.member-name-row svg {
  width: 17px;
  flex: 0 0 auto;
  color: rgba(0, 135, 60, 0.5);
  transition: transform 180ms ease;
}

.member-card h2 {
  margin: 0;
  color: var(--color-deep-green);
  font-size: 19px;
}

.member-role {
  color: var(--color-cau-green);
  font-size: 13px;
  font-weight: 650;
  line-height: 1.45;
}

.member-card p {
  display: -webkit-box;
  margin: 0;
  overflow: hidden;
  color: var(--color-muted);
  font-size: 13px;
  line-height: 1.55;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.member-card small {
  display: block;
  overflow: hidden;
  color: var(--color-blue-gray);
  font-size: 12px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.member-card:hover .member-photo img {
  transform: scale(1.025);
}

.member-card:hover .member-name-row svg {
  transform: translateX(3px);
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
    grid-template-columns: minmax(0, 1fr) auto;
  }

  .result-count {
    min-width: auto;
    text-align: right;
  }

  .member-card {
    grid-template-columns: 94px minmax(0, 1fr);
    min-height: 132px;
  }

  .member-photo {
    min-height: 132px;
  }

  .member-content {
    padding: 15px 14px;
  }
}
</style>


