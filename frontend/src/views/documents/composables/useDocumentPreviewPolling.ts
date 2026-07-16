import { onBeforeUnmount, watch, type Ref } from 'vue'

import type { LabDocument } from '../../../api/documents'

export function useDocumentPreviewPolling(
  document: Ref<LabDocument | null>,
  refresh: (documentId: number) => Promise<LabDocument>,
) {
  let timer: number | undefined
  let attempts = 0

  function stop() {
    if (timer) window.clearTimeout(timer)
    timer = undefined
  }

  function schedule() {
    stop()
    if (document.value?.preview_status !== 'pending' || attempts >= 120) return
    timer = window.setTimeout(async () => {
      const currentId = document.value?.id
      if (!currentId) return
      attempts += 1
      try {
        const refreshed = await refresh(currentId)
        if (document.value?.id === currentId) document.value = refreshed
      } catch {
        // A transient polling failure should not interrupt the reader.
      } finally {
        schedule()
      }
    }, 2500)
  }

  watch(document, (next, previous) => {
    if (next?.id !== previous?.id) attempts = 0
    schedule()
  }, { immediate: true })
  onBeforeUnmount(stop)
}
