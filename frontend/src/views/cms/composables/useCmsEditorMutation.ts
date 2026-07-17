import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { requestErrorMessage } from '../../../utils/requestErrors'

type UploadProgressEvent = {
  loaded: number
  total?: number
}

type MutationAction = (onUploadProgress: (event: UploadProgressEvent) => void) => Promise<unknown>

export function useCmsEditorMutation(afterChange: () => void | Promise<void>) {
  const saving = ref(false)
  const progress = ref(0)

  function onUploadProgress(event: UploadProgressEvent) {
    if (!event.total) return
    progress.value = Math.min(99, Math.round((event.loaded / event.total) * 100))
  }

  function errorMessage(error: any, fallback: string) {
    return requestErrorMessage(error, fallback)
  }

  function resetProgressSoon() {
    setTimeout(() => {
      if (!saving.value) progress.value = 0
    }, 800)
  }

  async function saveResult<T>(action: (onUploadProgress: (event: UploadProgressEvent) => void) => Promise<T>, successText = '内容已保存') {
    if (saving.value) return { succeeded: false as const, result: undefined }
    saving.value = true
    progress.value = 0
    try {
      const result = await action(onUploadProgress)
      if (progress.value > 0) progress.value = 100
      await afterChange()
      ElMessage.success(successText)
      return { succeeded: true as const, result }
    } catch (error) {
      ElMessage.error(errorMessage(error, '保存失败，请检查表单内容。'))
      return { succeeded: false as const, result: undefined }
    } finally {
      saving.value = false
      resetProgressSoon()
    }
  }

  async function save(action: MutationAction, successText = '内容已保存') {
    const outcome = await saveResult(action, successText)
    return Boolean(outcome && outcome.succeeded)
  }

  async function remove(message: string, action: () => Promise<unknown>) {
    try {
      await ElMessageBox.confirm(message, '删除确认', {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning',
      })
    } catch {
      return false
    }
    return save(() => action(), '内容已删除')
  }

  return { saving, progress, save, saveResult, remove, errorMessage }
}
