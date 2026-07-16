import { computed, readonly, ref } from 'vue'

const activeRequests = ref(0)
const visible = ref(false)
const showLabel = ref(false)
const progress = ref(0)

let showTimer: ReturnType<typeof setTimeout> | undefined
let labelTimer: ReturnType<typeof setTimeout> | undefined
let progressTimer: ReturnType<typeof setInterval> | undefined
let hideTimer: ReturnType<typeof setTimeout> | undefined

function clearTimer(timer: ReturnType<typeof setTimeout> | undefined) {
  if (timer) clearTimeout(timer)
}

function stopProgressTimer() {
  if (progressTimer) clearInterval(progressTimer)
  progressTimer = undefined
}

function startProgressTimer() {
  stopProgressTimer()
  progressTimer = setInterval(() => {
    if (!visible.value || progress.value >= 90) return
    const remaining = 90 - progress.value
    progress.value = Math.min(90, progress.value + Math.max(0.8, remaining * 0.08))
  }, 280)
}

export function beginNetworkRequest() {
  activeRequests.value += 1
  clearTimer(hideTimer)
  hideTimer = undefined

  if (activeRequests.value > 1) return

  progress.value = visible.value ? Math.min(progress.value, 72) : 10
  showLabel.value = false
  clearTimer(showTimer)
  clearTimer(labelTimer)

  showTimer = setTimeout(() => {
    visible.value = true
    progress.value = Math.max(progress.value, 18)
    startProgressTimer()
  }, 120)

  labelTimer = setTimeout(() => {
    if (activeRequests.value > 0) showLabel.value = true
  }, 650)
}

export function finishNetworkRequest() {
  activeRequests.value = Math.max(0, activeRequests.value - 1)
  if (activeRequests.value > 0) return

  clearTimer(showTimer)
  clearTimer(labelTimer)
  showTimer = undefined
  labelTimer = undefined
  showLabel.value = false
  stopProgressTimer()

  if (!visible.value) {
    progress.value = 0
    return
  }

  progress.value = 100
  hideTimer = setTimeout(() => {
    visible.value = false
    progress.value = 0
    hideTimer = undefined
  }, 240)
}

export function useNetworkActivity() {
  return {
    activeRequests: readonly(activeRequests),
    isLoading: computed(() => activeRequests.value > 0),
    progress: readonly(progress),
    showLabel: readonly(showLabel),
    visible: readonly(visible),
  }
}
