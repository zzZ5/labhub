import { ref } from 'vue'
import { ElMessage } from 'element-plus'

import { cmsApi } from '../../../api/cms'

export type CmsImportKind = 'members' | 'publications' | 'projects' | 'patents' | 'awards'

type ImportResult = { created: number; updated: number; skipped: number; images?: number }

export function useCmsImport(reload: () => Promise<void>) {
  const importProgress = ref(0)
  const importingKind = ref<CmsImportKind | ''>('')
  const actions: Record<CmsImportKind, (file: File, progress: (event: { loaded: number; total?: number }) => void) => Promise<ImportResult>> = {
    members: cmsApi.importMembers,
    publications: cmsApi.importPublications,
    projects: cmsApi.importProjects,
    patents: cmsApi.importPatents,
    awards: cmsApi.importAwards,
  }

  async function importFile(file: File, kind: CmsImportKind) {
    if (!file.name.toLowerCase().endsWith('.xlsx')) {
      ElMessage.warning('请上传 .xlsx 文件。')
      return
    }
    importingKind.value = kind
    importProgress.value = 0
    try {
      const result = await actions[kind](file, (event) => {
        if (event.total) importProgress.value = Math.min(99, Math.round((event.loaded / event.total) * 100))
      })
      importProgress.value = 100
      ElMessage.success(`导入完成：新增 ${result.created} 条，更新 ${result.updated} 条，跳过 ${result.skipped} 条${result.images ? `，图片 ${result.images} 张` : ''}。`)
      try {
        await reload()
      } catch {
        ElMessage.warning('导入数据已经保存，但列表刷新失败，请手动刷新页面查看。')
      }
    } catch (error: any) {
      ElMessage.error(error?.response?.data?.detail || '导入失败，请检查模板列名、日期格式和必填字段。')
    } finally {
      globalThis.setTimeout(() => {
        if (importingKind.value === kind) {
          importingKind.value = ''
          importProgress.value = 0
        }
      }, 900)
    }
  }

  return { importProgress, importingKind, importFile }
}
