<template>
  <section class="editor-grid">
    <CmsImportStrip
      description="批量导入论文成果，优先按 DOI 更新；没有 DOI 时按题目和年份匹配。"
      template-url="/templates/publications-import-template.xlsx" :loading="importing" :progress="importProgress"
      uploading-text="正在上传论文成果表，请不要关闭页面。" processing-text="上传完成，正在写入论文成果。"
      @import="$emit('import', $event)"
    />
    <CmsContentList title="论文成果" action-label="新增论文" :items="rows" :active-key="editingId || ''" @create="$emit('create')" @edit="$emit('edit', $event)" />
    <article class="card form-panel">
      <div class="form-heading"><div><span>{{ editingId ? '正在编辑' : '新增内容' }}</span><h2>{{ form.title || '论文成果' }}</h2></div></div>
      <el-form label-position="top">
        <el-form-item label="GB/T 7714-2025格式引文"><el-input v-model="form.citation_text" type="textarea" :rows="4" placeholder="例：作者. 论文题目. 期刊, 2026, 14(5): 123765. DOI: 10.xxxx/xxxxx" /></el-form-item>
        <div class="citation-actions"><button class="secondary-inline-action" type="button" @click="$emit('parse')">拆分并预览</button><span>保存前请确认拆分出的标题、作者和期刊信息。</span></div>
        <div v-if="hasPreview" class="citation-preview">
          <div class="citation-preview__title">拆分预览</div>
          <dl>
            <div><dt>题名</dt><dd>{{ preview.title || '未识别' }}</dd></div>
            <div><dt>作者</dt><dd>{{ preview.authors || '未识别' }}</dd></div>
            <div><dt>期刊</dt><dd>{{ preview.journal || '未识别' }}</dd></div>
            <div><dt>年份</dt><dd>{{ preview.year || '未识别' }}</dd></div>
            <div><dt>卷期页</dt><dd>{{ volumePreview || '未识别' }}</dd></div>
            <div><dt>DOI</dt><dd>{{ preview.doi || '未填写' }}</dd></div>
          </dl>
        </div>
        <div class="form-two-col">
          <el-form-item label="可见范围"><el-select v-model="form.visibility"><el-option label="公开" value="public" /><el-option label="成员可见" value="members" /><el-option label="管理员可见" value="admins" /></el-select></el-form-item>
          <el-form-item label="首页排序"><el-input-number v-model="form.sort_order" :min="0" /></el-form-item>
        </div>
        <el-form-item label="摘要"><el-input v-model="form.abstract" type="textarea" :rows="4" /></el-form-item>
        <el-form-item label="PDF 附件"><UploadFileField v-model="form.pdf_file" :disabled="saving" accept="application/pdf,.pdf" :max-size-mb="200" :existing-label="currentPdf ? displayFileLabel(currentPdf) : ''" /></el-form-item>
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
defineProps<{ rows: Array<any>; editingId: number | null; form: Record<string, any>; preview: Record<string, any>; hasPreview: boolean; volumePreview: string; currentPdf: string; saving: boolean; progress: number; importing: boolean; importProgress: number; displayFileLabel: (value: string) => string }>()
defineEmits<{ create: []; edit: [row: any]; save: []; delete: []; parse: []; import: [file: File] }>()
</script>
