<template>
  <section class="editor-grid">
    <CmsImportStrip
      description="批量导入科研项目，优先按项目编号更新；没有编号时按项目名称匹配。"
      template-url="/templates/projects-import-template.xlsx"
      :loading="importing" :progress="importProgress"
      uploading-text="正在上传科研项目表，请不要关闭页面。" processing-text="上传完成，正在写入科研项目。"
      @import="$emit('import', $event)"
    />
    <CmsContentList title="科研项目" action-label="新增项目" :items="rows" :active-key="editingId || ''" @create="$emit('create')" @edit="$emit('edit', $event)" />
    <article class="card form-panel">
      <div class="form-heading"><div><span>{{ editingId ? '正在编辑' : '新增内容' }}</span><h2>{{ form.title || '科研项目' }}</h2></div></div>
      <el-form label-position="top">
        <el-form-item label="项目名称"><el-input v-model="form.title" /></el-form-item>
        <div class="form-two-col">
          <el-form-item label="项目编号"><el-input v-model="form.project_number" /></el-form-item>
          <el-form-item label="资助来源"><el-input v-model="form.funding_source" /></el-form-item>
        </div>
        <div class="form-two-col">
          <el-form-item label="负责人"><el-input v-model="form.principal_investigator" /></el-form-item>
          <el-form-item label="状态"><el-input v-model="form.status" /></el-form-item>
        </div>
        <div class="form-two-col">
          <el-form-item label="经费"><el-input v-model="form.amount" placeholder="可留空" /></el-form-item>
          <el-form-item label="可见范围"><el-select v-model="form.visibility"><el-option label="公开" value="public" /><el-option label="成员可见" value="members" /><el-option label="管理员可见" value="admins" /></el-select></el-form-item>
        </div>
        <div class="form-two-col">
          <el-form-item label="开始日期"><el-date-picker v-model="form.start_date" type="date" value-format="YYYY-MM-DD" clearable /></el-form-item>
          <el-form-item label="结束日期"><el-date-picker v-model="form.end_date" type="date" value-format="YYYY-MM-DD" clearable /></el-form-item>
        </div>
        <el-form-item label="说明"><el-input v-model="form.description" type="textarea" :rows="4" /></el-form-item>
        <el-form-item label="首页排序"><el-input-number v-model="form.sort_order" :min="0" /></el-form-item>
      </el-form>
      <CmsFormActions :saving="saving" :progress="progress" :deletable="Boolean(editingId)" @save="$emit('save')" @delete="$emit('delete')" />
    </article>
  </section>
</template>

<script setup lang="ts">
import CmsContentList from './CmsContentList.vue'
import CmsFormActions from './CmsFormActions.vue'
import CmsImportStrip from './CmsImportStrip.vue'
defineProps<{ rows: Array<any>; editingId: number | null; form: Record<string, any>; saving: boolean; progress: number; importing: boolean; importProgress: number }>()
defineEmits<{ create: []; edit: [row: any]; save: []; delete: []; import: [file: File] }>()
</script>

