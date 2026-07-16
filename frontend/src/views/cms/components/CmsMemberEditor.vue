<template>
  <section class="editor-grid">
    <CmsImportStrip
      description="批量导入团队成员，可填写姓名、身份头衔、研究方向、邮箱、简介和展示排序。"
      template-url="/templates/members-import-template.xlsx"
      :loading="importing"
      :progress="importProgress"
      uploading-text="正在上传团队成员表，请不要关闭页面。"
      processing-text="上传完成，正在写入团队成员。"
      @import="$emit('import', $event)"
    />
    <CmsContentList title="团队成员" action-label="新增成员" :items="rows" :active-key="editingId || ''" @create="$emit('create')" @edit="$emit('edit', $event)" />
    <article class="card form-panel">
      <div class="form-heading">
        <div><span>{{ editingId ? '正在编辑' : '新增内容' }}</span><h2>{{ form.name || '团队成员' }}</h2></div>
      </div>
      <el-form label-position="top">
        <el-form-item label="姓名"><el-input v-model="form.name" /></el-form-item>
        <div class="form-two-col">
          <el-form-item label="身份头衔"><el-input v-model="form.role_type" placeholder="如：副教授 / 博士生导师、博士研究生、硕士研究生" /></el-form-item>
          <el-form-item label="邮箱"><el-input v-model="form.email" /></el-form-item>
        </div>
        <el-form-item label="研究方向"><el-input v-model="form.research_direction" /></el-form-item>
        <el-form-item label="头像">
          <div class="member-avatar-field">
            <div class="member-avatar-preview">
              <img v-if="avatarPreview && !avatarLoadFailed" :src="avatarPreview" :alt="String(form.name || '成员头像')" @error="avatarLoadFailed = true" />
              <span v-else>{{ form.name ? String(form.name).slice(0, 1) : '头像' }}</span>
            </div>
            <div class="member-avatar-control">
              <input :key="avatarInputKey" class="file-input" type="file" accept="image/*" @change="$emit('file', $event)" />
              <small v-if="selectedAvatar">待上传：{{ selectedAvatar.name }}（{{ formatFileSize(selectedAvatar.size) }}）</small>
              <small v-else-if="currentAvatar">当前头像：{{ displayFileLabel(currentAvatar) }}</small>
              <small v-else>建议使用清晰的正方形或竖版照片。</small>
            </div>
          </div>
        </el-form-item>
        <el-form-item label="简介"><el-input v-model="form.profile" type="textarea" :rows="4" /></el-form-item>
        <el-form-item label="展示排序">
          <el-input-number v-model="form.sort_order" :min="0" />
          <small>0 表示不在公开网站展示；大于 0 时按数字从小到大排序。</small>
        </el-form-item>
      </el-form>
      <CmsFormActions :saving="saving" :progress="progress" :deletable="Boolean(editingId)" @save="$emit('save')" @delete="$emit('delete')" />
    </article>
  </section>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import CmsContentList from './CmsContentList.vue'
import CmsFormActions from './CmsFormActions.vue'
import CmsImportStrip from './CmsImportStrip.vue'

const props = defineProps<{
  rows: Array<any>
  editingId: number | null
  form: Record<string, any>
  avatarPreview: string
  selectedAvatar?: File | null
  currentAvatar: string
  avatarInputKey: number
  saving: boolean
  progress: number
  importing: boolean
  importProgress: number
  displayFileLabel: (value: string) => string
  formatFileSize: (size: number) => string
}>()

defineEmits<{
  create: []
  edit: [row: any]
  save: []
  delete: []
  file: [event: Event]
  import: [file: File]
}>()

const avatarLoadFailed = ref(false)
watch(() => props.avatarPreview, () => { avatarLoadFailed.value = false })
</script>
