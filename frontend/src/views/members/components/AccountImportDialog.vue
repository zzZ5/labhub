<template>
  <el-dialog
    :model-value="open"
    title="批量导入成员账号"
    width="640px"
    destroy-on-close
    @update:model-value="$emit('update:open', $event)"
  >
    <div class="account-import">
      <section class="import-guide">
        <div>
          <strong>按模板整理账号清单</strong>
          <p>填写姓名、初始密码和学校身份；邮箱与账号名至少填写一个，学生账号可选择同步生成档案。</p>
        </div>
        <a href="/templates/accounts-import-template.xlsx" download>下载导入模板</a>
      </section>

      <el-form label-position="top">
        <el-form-item label="账号清单（.xlsx）">
          <UploadFileField
            v-model="file"
            :disabled="saving"
            accept=".xlsx"
            :max-size-mb="10"
            hint="仅支持账号导入模板，单个文件不超过 10 MB"
          />
        </el-form-item>
      </el-form>

      <section v-if="result" class="import-result" aria-live="polite">
        <div class="result-heading">
          <div><strong>导入结果</strong><span>共处理 {{ result.total }} 行</span></div>
          <span :class="['result-state', result.failed ? 'has-error' : 'success']">{{ result.failed ? '部分完成' : '导入完成' }}</span>
        </div>
        <div class="result-counts">
          <span><strong>{{ result.created }}</strong> 新增账号</span>
          <span><strong>{{ result.student_profiles }}</strong> 学生档案</span>
          <span><strong>{{ result.skipped }}</strong> 跳过</span>
          <span><strong>{{ result.failed }}</strong> 失败</span>
        </div>
        <div v-if="result.issues.length" class="issue-list">
          <div v-for="issue in result.issues" :key="`${issue.row}-${issue.status}-${issue.message}`">
            <span>第 {{ issue.row }} 行</span>
            <p>{{ issue.message }}</p>
          </div>
        </div>
      </section>
    </div>

    <template #footer>
      <UploadProgress
        :active="saving"
        :progress="progress"
        uploading-text="正在上传账号清单，请不要关闭窗口。"
        processing-text="上传完成，正在校验并创建账号。"
      />
      <el-button @click="$emit('update:open', false)">{{ result ? '关闭' : '取消' }}</el-button>
      <el-button type="primary" :loading="saving" @click="submit">开始导入</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'

import UploadFileField from '../../../components/UploadFileField.vue'
import UploadProgress from '../../../components/UploadProgress.vue'
import type { AccountImportResult } from '../../../api/accounts'

const props = defineProps<{
  open: boolean
  saving: boolean
  progress: number
  result: AccountImportResult | null
}>()
const emit = defineEmits<{
  'update:open': [value: boolean]
  import: [file: File]
}>()

const file = ref<File>()

function submit() {
  if (!file.value) {
    ElMessage.warning('请选择 .xlsx 账号清单。')
    return
  }
  emit('import', file.value)
}

watch(() => props.open, (open) => {
  if (open) file.value = undefined
})
</script>

<style scoped>
.account-import { display: grid; gap: 18px; }
.import-guide { display: flex; align-items: center; justify-content: space-between; gap: 18px; border-left: 3px solid var(--color-cau-green); padding: 12px 14px; background: var(--color-eco-green); }
.import-guide div { min-width: 0; }
.import-guide strong { display: block; color: var(--color-deep-green); font-weight: 650; }
.import-guide p { margin: 4px 0 0; color: var(--color-muted); font-size: 13px; line-height: 1.6; }
.import-guide a { flex: 0 0 auto; color: var(--color-cau-green); font-size: 13px; font-weight: 700; white-space: nowrap; }
.import-result { border: 1px solid var(--color-border); border-radius: var(--radius-sm); overflow: hidden; }
.result-heading { display: flex; align-items: center; justify-content: space-between; gap: 12px; border-bottom: 1px solid var(--color-line); padding: 12px 14px; }
.result-heading > div { display: flex; align-items: baseline; gap: 8px; }
.result-heading strong { color: var(--color-deep-green); }
.result-heading span { color: var(--color-muted); font-size: 12px; }
.result-state { border-radius: 4px; padding: 3px 7px; font-weight: 650; }
.result-state.success { background: var(--color-eco-green); color: var(--color-deep-green); }
.result-state.has-error { background: #fff6df; color: #8b622c; }
.result-counts { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 1px; background: var(--color-line); }
.result-counts span { display: grid; gap: 2px; padding: 11px 12px; background: #fff; color: var(--color-muted); font-size: 12px; }
.result-counts strong { color: var(--color-deep-green); font-size: 18px; }
.issue-list { display: grid; max-height: 180px; overflow-y: auto; padding: 6px 14px 10px; }
.issue-list > div { display: grid; grid-template-columns: 64px minmax(0, 1fr); gap: 10px; border-bottom: 1px solid var(--color-line); padding: 8px 0; }
.issue-list > div:last-child { border-bottom: 0; }
.issue-list span { color: var(--color-blue-gray); font-size: 12px; font-weight: 650; }
.issue-list p { margin: 0; color: var(--color-text); font-size: 12px; line-height: 1.5; }

@media (max-width: 640px) {
  .import-guide { align-items: flex-start; flex-direction: column; gap: 8px; }
  .result-counts { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
</style>
