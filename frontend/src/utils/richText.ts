export function richTextToPlainText(value?: string | null) {
  if (!value) return ''
  if (typeof DOMParser === 'undefined') return value.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim()
  const document = new DOMParser().parseFromString(value, 'text/html')
  return (document.body.textContent || '').replace(/\s+/g, ' ').trim()
}
