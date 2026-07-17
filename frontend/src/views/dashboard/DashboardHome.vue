<template>
  <InternalLayout title="内部工作台">
    <section class="dashboard-page">
      <InternalPageHeader>
        <p>快速进入常用内部模块，查看近期资料、设备状态和学生归档概况。</p>
        <template #actions><RouterLink class="outline-action" to="/">返回门户首页</RouterLink></template>
      </InternalPageHeader>

      <section class="quick-grid">
        <RouterLink v-for="item in quickLinks" :key="item.title" class="card quick-card" :to="item.to">
          <span>{{ item.kicker }}</span>
          <strong>{{ item.title }}</strong>
          <p>{{ item.description }}</p>
        </RouterLink>
      </section>

      <section class="compact-summary dashboard-summary">
        <span v-for="item in visibleSummary" :key="item.label"><strong>{{ item.value }}</strong>{{ item.label }}</span>
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
            <div v-for="doc in dashboard.latest_documents" :key="doc.id" class="list-row">
              <div>
                <strong>{{ doc.title }}</strong>
                <span>{{ doc.category_name || '未分类' }} · {{ formatDate(doc.updated_at) }}</span>
              </div>
            </div>
          </div>
          <div v-else class="empty-note">暂无可查阅资料。</div>
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
            <div v-for="item in dashboard.instrument_status" :key="item.id" class="list-row">
              <div>
                <strong>{{ item.name }}</strong>
                <span>{{ item.location_detail || '未填写位置' }}</span>
              </div>
              <span :class="['status-tag', instrumentStatusClass(item.status)]">{{ instrumentStatusText(item.status) }}</span>
            </div>
          </div>
          <div v-else class="empty-note">当前没有需要关注的设备。</div>
        </article>

        <article class="card panel wide-panel">
          <div class="panel-heading">
            <div>
              <h2>学生归档</h2>
              <p>展示最近可见的学生档案和归档材料数量。</p>
            </div>
            <RouterLink to="/students">查看学生档案</RouterLink>
          </div>
          <div v-if="dashboard.student_archives.length" class="student-grid">
            <RouterLink v-for="student in dashboard.student_archives" :key="student.id" class="student-card" to="/students">
              <strong>{{ student.name }}</strong>
              <span>{{ degreeText(student.degree_type) }} {{ student.grade || '' }}</span>
              <p>{{ student.file_count }} 份归档材料</p>
              <small v-if="student.latest_file_title">最近上传：{{ student.latest_file_title }}</small>
              <small v-else>{{ student.research_direction || '研究方向待补充' }}</small>
            </RouterLink>
          </div>
          <div v-else class="empty-note">暂无可见学生档案。</div>
        </article>
      </section>
    </section>
  </InternalLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive } from 'vue'

import { fetchDashboard, type DashboardData } from '../../api/dashboard'
import InternalLayout from '../../layouts/InternalLayout.vue'
import InternalPageHeader from '../../components/InternalPageHeader.vue'
import { useSessionStore } from '../../stores/session'

const session = useSessionStore()
const dashboard = reactive<DashboardData>({
  summary: [
    { label: '待审核账号', value: 0, note: '仅管理员与硕博导师可见' },
    { label: '设备需关注', value: 0, note: '维护或停用设备' },
    { label: '可查阅资料', value: 0, note: '当前权限范围内' },
    { label: '学生资料', value: 0, note: '开题报告、毕业论文等归档材料' },
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
const quickLinks = computed(() => {
  const links = [
    { title: '内部资料', kicker: '资料库', description: '查看实验方法、组会资料和项目材料', to: '/documents' },
    { title: '仪器平台', kicker: '设备', description: '查看设备图片、位置和使用说明', to: '/instruments' },
    { title: '学生档案', kicker: '归档', description: '维护学生信息和毕业相关材料', to: '/students' },
  ]
  if (canEditPortal.value) {
    links.push({ title: '门户内容', kicker: '网站', description: '维护首页、新闻、成果和团队展示', to: '/cms' })
  }
  if (canManageMembers.value && pendingUserCount.value > 0) {
    links.push({ title: '成员审核', kicker: '账号', description: `${pendingUserCount.value} 个账号等待确认`, to: '/members' })
  }
  return links
})

const visibleSummary = computed(() =>
  dashboard.summary.filter((item) => item.label !== '待审核账号' || item.value > 0),
)

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

.quick-card p,
.panel-heading p,
.student-card p,
.student-card small,
.list-row div span {
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
  gap: 7px;
  min-height: 96px;
  padding: 14px 16px;
  color: inherit;
  box-shadow: none;
}

.quick-card:hover {
  border-color: rgba(0, 135, 60, 0.28);
  transform: translateY(-1px);
}

.quick-card span {
  color: var(--color-cau-green);
  font-size: 13px;
  font-weight: 700;
}

.quick-card strong {
  color: var(--color-deep-green);
  font-size: 18px;
  font-weight: 650;
}

.quick-card p {
  font-size: 14px;
}

.panel:hover {
  transform: none;
}

.dashboard-summary {
  padding: 0 2px 2px;
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

.list-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  min-height: 58px;
  padding: 12px 0;
  border-top: 1px solid var(--color-line);
}

.list-row:first-child {
  border-top: 0;
}

.list-row strong,
.list-row span {
  display: block;
}

.student-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 12px;
}

.student-card {
  display: grid;
  gap: 5px;
  border: 1px solid var(--color-line);
  border-radius: var(--radius-md);
  padding: 13px 14px;
  background: var(--color-panel);
  color: inherit;
}

.student-card:hover {
  border-color: rgba(0, 135, 60, 0.22);
  background: #fff;
}

.student-card strong {
  color: var(--color-text);
}

.student-card span {
  color: var(--color-cau-green);
  font-size: 13px;
  font-weight: 700;
}

.student-card small {
  overflow: hidden;
  font-size: 13px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.empty-note {
  border-top: 1px solid var(--color-line);
  padding: 18px 0 4px;
  color: var(--color-muted);
  font-size: 14px;
}

@media (max-width: 1080px) {
  .quick-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .student-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 760px) {
  .panel-heading {
    display: grid;
    align-items: start;
  }

  .quick-grid,
  .panel-grid,
  .student-grid {
    grid-template-columns: 1fr;
  }

  .wide-panel {
    grid-column: auto;
  }

  .list-row {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
