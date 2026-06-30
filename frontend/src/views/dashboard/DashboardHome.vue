<template>
  <InternalLayout title="内部工作台">
    <section class="dashboard-hero">
      <div>
        <span>中农雨磷 Research Workspace</span>
        <h1>科研管理概览</h1>
        <p>集中查看课题组资料、仪器设备状态、学生信息与近期归档材料。</p>
      </div>
      <RouterLink class="outline-action" to="/">返回门户首页</RouterLink>
    </section>

    <section class="dashboard-grid">
      <article v-for="item in dashboard.summary" :key="item.label" class="card summary-card">
        <span>{{ item.label }}</span>
        <strong>{{ item.value }}</strong>
        <p>{{ item.note }}</p>
      </article>
    </section>

    <section class="panel-grid">
      <article class="card panel">
        <div class="panel-heading">
          <h2>仪器设备状态</h2>
          <RouterLink to="/instruments">查看台账</RouterLink>
        </div>
        <div v-if="dashboard.instrument_status.length" class="stack-list">
          <div v-for="item in dashboard.instrument_status" :key="item.id" class="list-row">
            <div>
              <strong>{{ item.name }}</strong>
              <span>{{ item.room || '未填写房间' }} {{ item.location_detail }}</span>
            </div>
            <span :class="['status-tag', instrumentStatusClass(item.status)]">{{ instrumentStatusText(item.status) }}</span>
          </div>
        </div>
        <div v-else class="empty-note">暂无需要关注的设备状态</div>
      </article>

      <article class="card panel">
        <div class="panel-heading">
          <h2>最新内部资料</h2>
          <RouterLink to="/documents">进入资料库</RouterLink>
        </div>
        <div v-if="dashboard.latest_documents.length" class="stack-list">
          <div v-for="doc in dashboard.latest_documents" :key="doc.id" class="list-row">
            <div>
              <strong>{{ doc.title }}</strong>
              <span>{{ doc.category_name }} · {{ doc.current_version }} · {{ formatDate(doc.updated_at) }}</span>
            </div>
            <span class="status-tag normal">{{ visibilityText(doc.visibility) }}</span>
          </div>
        </div>
        <div v-else class="empty-note">暂无可查阅资料</div>
      </article>

      <article class="card panel">
        <div class="panel-heading">
          <h2>待办事项</h2>
          <span>{{ dashboard.todos.length }} 项</span>
        </div>
        <div v-if="dashboard.todos.length" class="todo-list">
          <RouterLink v-for="todo in dashboard.todos" :key="todo.title" :to="todo.target" class="todo-row">
            <span :class="['dot', todo.level]" />
            <div>
              <strong>{{ todo.title }}</strong>
              <p>{{ todo.detail }}</p>
            </div>
          </RouterLink>
        </div>
        <div v-else class="empty-note">当前没有需要马上处理的事项</div>
      </article>

      <article class="card panel">
        <div class="panel-heading">
          <h2>学生资料归档</h2>
          <RouterLink to="/students">查看学生信息</RouterLink>
        </div>
        <div v-if="dashboard.student_archives.length" class="progress-list">
          <div v-for="student in dashboard.student_archives" :key="student.id" class="progress-row">
            <div class="progress-meta">
              <strong>{{ student.name }}</strong>
              <span>{{ degreeText(student.degree_type) }} {{ student.grade || '' }}</span>
            </div>
            <p>{{ student.file_count }} 份归档材料</p>
            <p v-if="student.latest_file_title">最近上传：{{ student.latest_file_title }}</p>
            <p v-else-if="student.research_direction">{{ student.research_direction }}</p>
          </div>
        </div>
        <div v-else class="empty-note">暂无可见学生信息或归档材料</div>
      </article>

      <article class="card panel wide-panel">
        <div class="panel-heading">
          <h2>最近下载</h2>
          <RouterLink to="/documents">资料库</RouterLink>
        </div>
        <div v-if="dashboard.recent_downloads.length" class="download-grid">
          <div v-for="item in dashboard.recent_downloads" :key="item.id" class="download-item">
            <strong>{{ item.document_title }}</strong>
            <span>{{ item.version_label }} · {{ formatDate(item.downloaded_at) }}</span>
          </div>
        </div>
        <div v-else class="empty-note">暂无下载记录</div>
      </article>
    </section>
  </InternalLayout>
</template>

<script setup lang="ts">
import { onMounted, reactive } from 'vue'

import { fetchDashboard, type DashboardData } from '../../api/dashboard'
import InternalLayout from '../../layouts/InternalLayout.vue'

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

onMounted(async () => {
  try {
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

function visibilityText(visibility: string) {
  return (
    {
      public: '公开',
      members: '成员可见',
      phd: '博士可见',
      pi: '导师可见',
      custom: '指定可见',
    }[visibility] || '内部资料'
  )
}

function degreeText(degree: string) {
  return degree === 'phd' ? '博士' : degree === 'master' ? '硕士' : '学生'
}
</script>

<style scoped>
.dashboard-hero {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 24px;
  margin-bottom: 26px;
  border: 1px solid rgba(0, 135, 60, 0.12);
  border-radius: var(--radius-lg);
  padding: 30px 32px;
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.98), rgba(251, 253, 251, 0.94) 56%, rgba(234, 245, 238, 0.86)),
    #fff;
  box-shadow: var(--shadow-flat);
}

.dashboard-hero span {
  color: var(--color-cau-green);
  font-size: 13px;
  font-weight: 700;
}

.dashboard-hero h1 {
  margin: 6px 0 8px;
  color: var(--color-deep-green);
  font-size: clamp(27px, 3vw, 34px);
  font-weight: 650;
  line-height: 1.2;
}

.dashboard-hero p {
  margin: 0;
  color: var(--color-muted);
}

.outline-action {
  flex: 0 0 auto;
  padding: 9px 16px;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 18px;
  margin-bottom: 24px;
}

.summary-card,
.panel {
  padding: 22px;
}

.summary-card:hover,
.panel:hover {
  transform: none;
}

.summary-card span {
  color: var(--color-muted);
  font-size: 14px;
}

.summary-card strong {
  display: block;
  margin: 9px 0;
  color: var(--color-deep-green);
  font-size: 32px;
  font-weight: 650;
  line-height: 1;
}

.summary-card p {
  margin: 0;
  color: var(--color-muted);
}

.panel-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 20px;
}

.panel {
  border-radius: var(--radius-lg);
}

.wide-panel {
  grid-column: 1 / -1;
}

.panel-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 12px;
  border-bottom: 1px solid var(--color-line);
  padding-bottom: 12px;
}

.panel-heading h2 {
  margin: 0;
  color: var(--color-deep-green);
  font-size: 19px;
  font-weight: 650;
}

.panel-heading a,
.panel-heading span {
  color: var(--color-cau-green);
  font-size: 14px;
  font-weight: 700;
}

.stack-list,
.todo-list,
.progress-list {
  display: grid;
}

.list-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  min-height: 62px;
  padding: 13px 0;
  border-top: 1px solid var(--color-line);
}

.list-row:first-child,
.todo-row:first-child {
  border-top: 0;
}

.list-row strong,
.list-row span,
.todo-row strong,
.todo-row p {
  display: block;
}

.list-row div span,
.todo-row p,
.progress-row p,
.download-item span {
  color: var(--color-muted);
  font-size: 14px;
}

.todo-row {
  display: grid;
  grid-template-columns: 10px 1fr;
  gap: 12px;
  padding: 14px 0;
  border-top: 1px solid var(--color-line);
  color: var(--color-text);
}

.dot {
  width: 10px;
  height: 10px;
  margin-top: 7px;
  border-radius: 50%;
  background: var(--color-cau-green);
}

.dot.warning {
  background: var(--color-soil);
}

.dot.info {
  background: var(--color-blue-gray);
}

.progress-list {
  gap: 18px;
}

.progress-meta {
  display: flex;
  justify-content: space-between;
  gap: 14px;
  margin-bottom: 6px;
}

.progress-meta strong {
  color: var(--color-text);
}

.progress-meta span {
  color: var(--color-muted);
  font-size: 14px;
}

.progress-row p {
  margin: 6px 0 0;
}

.download-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.download-item {
  border: 1px solid var(--color-line);
  border-radius: var(--radius-sm);
  padding: 14px 16px;
  background: var(--color-panel);
}

.download-item:hover {
  border-color: rgba(0, 135, 60, 0.18);
  background: #fff;
}

.download-item strong,
.download-item span {
  display: block;
}

.empty-note {
  border-top: 1px solid var(--color-line);
  padding: 18px 0 4px;
  color: var(--color-muted);
  font-size: 14px;
}

@media (max-width: 980px) {
  .dashboard-grid,
  .panel-grid,
  .download-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .dashboard-hero {
    display: grid;
    align-items: start;
    padding: 22px;
  }

  .dashboard-grid,
  .panel-grid,
  .download-grid {
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
