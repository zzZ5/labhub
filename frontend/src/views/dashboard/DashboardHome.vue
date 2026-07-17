<template>
  <InternalLayout title="内部工作台">
    <section class="dashboard-page">
      <section class="quick-grid">
        <RouterLink v-for="item in quickLinks" :key="item.title" class="card quick-card" :to="item.to">
          <span class="quick-kicker">{{ item.kicker }}</span>
          <strong class="quick-title">{{ item.title }}</strong>
          <div v-if="item.value !== null" class="quick-metric"><b>{{ item.value }}</b><small>{{ item.unit }}</small></div>
          <span v-else class="quick-entry">进入管理</span>
        </RouterLink>
      </section>

      <section class="panel-grid">
        <article class="card panel">
          <div class="panel-heading">
            <div>
              <h2>近期资料</h2>
              <p>最近更新、可查阅的内部资料。</p>
            </div>
            <RouterLink to="/documents">进入资料库</RouterLink>
          </div>
          <div v-if="dashboard.latest_documents.length" class="stack-list">
            <RouterLink v-for="doc in dashboard.latest_documents" :key="doc.id" class="compact-row-link" :to="{ path: '/documents', query: { document: doc.id } }">
              <CompactDataRow :title="doc.title" :description="`${doc.category_name || '未分类'} · ${formatDate(doc.updated_at)}`">
                <template #trailing><span class="row-link">查看</span></template>
              </CompactDataRow>
            </RouterLink>
          </div>
          <EmptyState v-else compact title="暂无近期资料" description="资料上传后会显示在这里。" />
        </article>

        <article class="card panel">
          <div class="panel-heading">
            <div>
              <h2>设备状态</h2>
              <p>仅显示维护中或停用的设备。</p>
            </div>
            <RouterLink to="/instruments">查看仪器平台</RouterLink>
          </div>
          <div v-if="dashboard.instrument_status.length" class="stack-list">
            <RouterLink v-for="item in dashboard.instrument_status" :key="item.id" class="compact-row-link" :to="`/instruments/${item.id}`">
              <CompactDataRow :title="item.name" :description="item.location_detail || '未填写位置'">
                <template #trailing><span :class="['status-tag', instrumentStatusClass(item.status)]">{{ instrumentStatusText(item.status) }}</span></template>
              </CompactDataRow>
            </RouterLink>
          </div>
          <EmptyState v-else compact title="设备状态正常" description="当前没有维护中或停用的设备。" />
        </article>

        <article class="card panel wide-panel">
          <div class="panel-heading">
            <div>
              <h2>学生归档</h2>
              <p>展示最近可见的学生档案和归档材料数量。</p>
            </div>
            <RouterLink to="/students">查看学生档案</RouterLink>
          </div>
          <div v-if="dashboard.student_archives.length" class="stack-list student-list">
            <RouterLink v-for="student in dashboard.student_archives" :key="student.id" class="compact-row-link" :to="{ path: '/students', query: { student: student.id } }">
              <CompactDataRow :title="student.name" :description="`${degreeText(student.degree_type)} ${student.grade || ''} · ${student.latest_file_title || student.research_direction || '暂无近期材料'}`">
                <template #trailing><span class="archive-count">{{ student.file_count }} 份资料</span></template>
              </CompactDataRow>
            </RouterLink>
          </div>
          <EmptyState v-else compact title="暂无学生档案" description="建档后会显示最近更新的档案。" />
        </article>
      </section>
    </section>
  </InternalLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive } from 'vue'

import { fetchDashboard, type DashboardData } from '../../api/dashboard'
import InternalLayout from '../../layouts/InternalLayout.vue'
import CompactDataRow from '../../components/CompactDataRow.vue'
import EmptyState from '../../components/EmptyState.vue'
import { useSessionStore } from '../../stores/session'

const session = useSessionStore()
const dashboard = reactive<DashboardData>({
  summary: [
    { label: '待审核账号', value: 0, note: '仅管理员与硕博导师可见' },
    { label: '设备数量', value: 0, note: '仪器平台全部设备' },
    { label: '资料数量', value: 0, note: '当前权限范围内' },
    { label: '学生档案数量', value: 0, note: '当前可见学生档案' },
  ],
  instrument_status: [],
  latest_documents: [],
  todos: [],
  student_archives: [],
  recent_downloads: [],
})

const canEditPortal = computed(() => Boolean(session.user?.is_superuser || session.hasAnyRole(['admin', 'editor'])))
const canManageMembers = computed(() => Boolean(session.user?.is_superuser || session.hasAnyRole(['admin'])))
const pendingUserCount = computed(() => dashboard.summary.find((item) => item.label === '待审核账号')?.value || 0)
type QuickLink = { title: string; kicker: string; value: number | null; unit: string; to: string }

function summaryValue(...labels: string[]) {
  return dashboard.summary.find((item) => labels.includes(item.label))?.value || 0
}
const quickLinks = computed(() => {
  const links: QuickLink[] = [
    { title: '内部资料', kicker: '资料库', value: summaryValue('资料数量', '可查阅资料'), unit: '份', to: '/documents' },
    { title: '仪器平台', kicker: '设备', value: summaryValue('设备数量'), unit: '台', to: '/instruments' },
    { title: '学生档案', kicker: '归档', value: summaryValue('学生档案数量', '归档数量', '学生资料'), unit: '份', to: '/students' },
  ]
  if (canEditPortal.value) {
    links.push({ title: '门户内容', kicker: '网站', value: null, unit: '', to: '/cms' })
  }
  if (canManageMembers.value && pendingUserCount.value > 0) {
    links.push({ title: '成员审核', kicker: '账号', value: pendingUserCount.value, unit: '个待审核', to: '/members' })
  }
  return links
})

onMounted(async () => {
  try {
    if (!session.initialized) await session.loadCurrentUser()
    const data = await fetchDashboard()
    Object.assign(dashboard, data)
  } catch {
    // 未登录或接口暂不可用时保留空工作台，避免内部页面整体失效。
  }
})

function formatDate(value: string) {
  if (!value) return '-'
  return new Intl.DateTimeFormat('zh-CN', { month: '2-digit', day: '2-digit' }).format(new Date(value))
}

function instrumentStatusClass(status: string) {
  if (status === 'normal') return 'normal'
  if (status === 'maintenance') return 'maintenance'
  return 'archived'
}

function instrumentStatusText(status: string) {
  return (
    {
      normal: '正常',
      maintenance: '维护中',
      disabled: '停用',
    }[status] || '待确认'
  )
}

function degreeText(degree: string) {
  if (degree === 'phd') return '博士'
  if (degree === 'master') return '硕士'
  if (degree === 'undergraduate') return '本科'
  return '学生'
}
</script>

<style scoped>
.dashboard-page {
  display: grid;
  gap: 16px;
}

.panel-heading p {
  margin: 0;
  color: var(--color-muted);
  line-height: 1.55;
}

.outline-action {
  flex: 0 0 auto;
  padding: 9px 16px;
}

.quick-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.quick-card {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: end;
  gap: 5px 14px;
  min-height: 104px;
  padding: 14px 16px;
  color: inherit;
  box-shadow: none;
}

.quick-card:hover {
  border-color: rgba(0, 135, 60, 0.28);
  transform: translateY(-1px);
}

.quick-kicker {
  grid-column: 1 / -1;
  color: var(--color-cau-green);
  font-size: 13px;
  font-weight: 700;
}

.quick-title {
  color: var(--color-deep-green);
  font-size: 18px;
  font-weight: 650;
}

.quick-metric {
  display: flex;
  align-items: baseline;
  justify-content: flex-end;
  gap: 4px;
  color: var(--color-cau-green);
}

.quick-metric b {
  font-family: Inter, Arial, sans-serif;
  font-size: 28px;
  font-weight: 650;
  line-height: 1;
}

.quick-metric small,
.quick-entry {
  color: var(--color-muted);
  font-size: 12px;
  font-weight: 600;
}

.quick-entry {
  justify-self: end;
  color: var(--color-cau-green);
}

.panel:hover {
  transform: none;
}

.panel-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.panel {
  border-radius: var(--radius-lg);
  padding: 20px;
}

.wide-panel {
  grid-column: 1 / -1;
}

.panel-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 12px;
  border-bottom: 1px solid var(--color-line);
  padding-bottom: 12px;
}

.panel-heading h2 {
  margin: 0 0 4px;
  color: var(--color-deep-green);
  font-size: 19px;
  font-weight: 650;
}

.panel-heading a {
  flex: 0 0 auto;
  color: var(--color-cau-green);
  font-size: 14px;
  font-weight: 700;
}

.stack-list {
  display: grid;
}

.compact-row-link {
  display: block;
  min-width: 0;
  border-top: 1px solid var(--color-line);
  color: inherit;
}

.compact-row-link:first-child {
  border-top: 0;
}

.row-link,
.archive-count { flex: 0 0 auto; color: var(--color-cau-green); font-size: 13px; font-weight: 650; }
.student-list { grid-template-columns: repeat(2, minmax(0, 1fr)); column-gap: 24px; }
.student-list .compact-row-link:nth-child(2) { border-top: 0; }

@media (max-width: 1080px) {
  .quick-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

}

@media (max-width: 760px) {
  .panel-heading {
    display: grid;
    align-items: start;
  }

  .quick-grid,
  .panel-grid,
  .student-list {
    grid-template-columns: 1fr;
  }

  .student-list .compact-row-link:nth-child(2) { border-top: 1px solid var(--color-line); }

  .wide-panel {
    grid-column: auto;
  }

}
</style>
