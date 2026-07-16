<template>
  <section class="editor-grid">
    <CmsImportStrip
      description="批量导入专利成果，优先按专利号更新；没有专利号时按专利名称匹配。"
      template-url="/templates/patents-import-template.xlsx" :loading="importing" :progress="importProgress"
      uploading-text="正在上传专利成果表，请不要关闭页面。" processing-text="上传完成，正在写入专利成果。"
      @import="$emit('import', $event)"
    />
    <CmsContentList title="专利成果" action-label="新增专利" :items="rows" :active-key="editingId || ''" @create="$emit('create')" @edit="$emit('edit', $event)" />
    <article class="card form-panel">
      <div class="form-heading"><div><span>{{ editingId ? '正在编辑' : '新增内容' }}</span><h2>{{ form.title || '专利成果' }}</h2></div></div>
      <el-form label-position="top">
        <el-form-item label="专利名称"><el-input v-model="form.title" /></el-form-item>
        <div class="form-two-col"><el-form-item label="专利号"><el-input v-model="form.patent_number" /></el-form-item><el-form-item label="状态"><el-input v-model="form.status" /></el-form-item></div>
        <el-form-item label="发明人"><el-input v-model="form.inventors" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="PDF 附件">
          <input class="file-input" type="file" accept="application/pdf" @change="$emit('file', $event)" />
          <small v-if="currentPdf">当前 PDF：{{ displayFileLabel(currentPdf) }}</small>
        </el-form-item>
        <div class="form-two-col"><el-form-item label="申请日期"><el-date-picker v-model="form.application_date" type="date" value-format="YYYY-MM-DD" clearable /></el-form-item><el-form-item label="授权日期"><el-date-picker v-model="form.authorization_date" type="date" value-format="YYYY-MM-DD" clearable /></el-form-item></div>
        <el-form-item label="可见范围"><el-select v-model="form.visibility"><el-option label="公开" value="public" /><el-option label="成员可见" value="members" /><el-option label="管理员可见" value="admins" /></el-select></el-form-item>
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
defineProps<{ rows: Array<any>; editingId: number | null; form: Record<string, any>; currentPdf: string; saving: boolean; progress: number; importing: boolean; importProgress: number; displayFileLabel: (value: string) => string }>()
defineEmits<{ create: []; edit: [row: any]; save: []; delete: []; file: [event: Event]; import: [file: File] }>()
</script>

