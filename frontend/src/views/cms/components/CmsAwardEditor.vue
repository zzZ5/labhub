<template>
  <section class="editor-grid">
    <CmsImportStrip
      description="批量导入获奖成果，按奖项名称和获奖日期更新；Excel 行内图片会作为获奖图片。"
      template-url="/templates/awards-import-template.xlsx" :loading="importing" :progress="importProgress"
      uploading-text="正在上传获奖成果表，请不要关闭页面。" processing-text="上传完成，正在写入获奖成果。"
      @import="$emit('import', $event)"
    />
    <CmsContentList title="获奖成果" action-label="新增获奖" :items="rows" :active-key="editingId || ''" @create="$emit('create')" @edit="$emit('edit', $event)" />
    <article class="card form-panel">
      <div class="form-heading"><div><span>{{ editingId ? '正在编辑' : '新增内容' }}</span><h2>{{ form.title || '获奖成果' }}</h2></div></div>
      <el-form label-position="top">
        <el-form-item label="奖项名称"><el-input v-model="form.title" /></el-form-item>
        <div class="form-two-col"><el-form-item label="奖项等级"><el-input v-model="form.award_level" /></el-form-item><el-form-item label="获奖日期"><el-date-picker v-model="form.award_date" type="date" value-format="YYYY-MM-DD" clearable /></el-form-item></div>
        <el-form-item label="参与人员"><el-input v-model="form.participants" type="textarea" :rows="2" /></el-form-item>
        <div class="form-two-col">
          <el-form-item label="获奖图片"><UploadFileField v-model="form.image" :disabled="saving" accept="image/*" :existing-label="currentImage ? displayFileLabel(currentImage) : ''" /></el-form-item>
          <el-form-item label="附件"><UploadFileField v-model="form.attachment" :disabled="saving" accept="application/pdf,image/*,.pdf" :existing-label="currentAttachment ? displayFileLabel(currentAttachment) : ''" /></el-form-item>
        </div>
        <el-form-item label="可见范围"><el-select v-model="form.visibility"><el-option label="公开" value="public" /><el-option label="成员可见" value="members" /><el-option label="管理员可见" value="admins" /></el-select></el-form-item>
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
import UploadFileField from '../../../components/UploadFileField.vue'
defineProps<{ rows: Array<any>; editingId: number | null; form: Record<string, any>; currentImage: string; currentAttachment: string; saving: boolean; progress: number; importing: boolean; importProgress: number; displayFileLabel: (value: string) => string }>()
defineEmits<{ create: []; edit: [row: any]; save: []; delete: []; import: [file: File] }>()
</script>
