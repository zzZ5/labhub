import { computed } from 'vue'
import { useRoute } from 'vue-router'

export function usePortalReturn(fallback: string) {
  const route = useRoute()

  return computed(() => {
    const source = Array.isArray(route.query.from) ? route.query.from[0] : route.query.from
    if (!source || !source.startsWith('/') || source.startsWith('//')) return fallback
    return source
  })
}
