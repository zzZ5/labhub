export type VideoPlayback = {
  kind: 'embed' | 'direct' | 'external'
  source: string
  src: string
}

function safeUrl(value: string) {
  try {
    const url = new URL(value.trim())
    return ['http:', 'https:'].includes(url.protocol) ? url : null
  } catch {
    return null
  }
}

function bilibiliPlayback(url: URL): VideoPlayback | null {
  const host = url.hostname.toLowerCase()
  if (host === 'player.bilibili.com') return { kind: 'embed', source: '哔哩哔哩', src: url.toString() }
  if (!host.endsWith('bilibili.com')) return null

  const bvid = url.pathname.match(/\/video\/(BV[a-z0-9]+)/i)?.[1] || url.searchParams.get('bvid')
  const aid = url.pathname.match(/\/video\/av(\d+)/i)?.[1] || url.searchParams.get('aid')
  if (!bvid && !aid) return null
  const params = new URLSearchParams({ autoplay: '0', danmaku: '0', high_quality: '1' })
  if (bvid) params.set('bvid', bvid)
  if (aid) params.set('aid', aid)
  const page = url.searchParams.get('p')
  if (page && /^\d+$/.test(page)) params.set('page', page)
  return { kind: 'embed', source: '哔哩哔哩', src: `https://player.bilibili.com/player.html?${params}` }
}

function youtubePlayback(url: URL): VideoPlayback | null {
  const host = url.hostname.toLowerCase().replace(/^www\./, '')
  let id = ''
  if (host === 'youtu.be') id = url.pathname.split('/').filter(Boolean)[0] || ''
  if (host === 'youtube.com' || host === 'm.youtube.com') {
    id = url.searchParams.get('v') || url.pathname.match(/^\/(?:embed|shorts)\/([a-z0-9_-]+)/i)?.[1] || ''
  }
  if (!/^[a-z0-9_-]{6,}$/i.test(id)) return null
  return { kind: 'embed', source: 'YouTube', src: `https://www.youtube-nocookie.com/embed/${id}` }
}

function platformPlayback(url: URL): VideoPlayback | null {
  const host = url.hostname.toLowerCase().replace(/^www\./, '')
  if (host === 'vimeo.com' || host === 'player.vimeo.com') {
    const id = url.pathname.match(/(?:video\/)?(\d+)/)?.[1]
    return id ? { kind: 'embed', source: 'Vimeo', src: `https://player.vimeo.com/video/${id}` } : null
  }
  if (host === 'v.qq.com') {
    const id = url.pathname.match(/\/([a-z0-9]+)\.html$/i)?.[1] || url.searchParams.get('vid')
    return id ? { kind: 'embed', source: '腾讯视频', src: `https://v.qq.com/txp/iframe/player.html?vid=${encodeURIComponent(id)}` } : null
  }
  if (host.endsWith('youku.com')) {
    const id = url.pathname.match(/id_([a-z0-9=]+)/i)?.[1]
    return id ? { kind: 'embed', source: '优酷', src: `https://player.youku.com/embed/${encodeURIComponent(id)}` } : null
  }
  return null
}

export function resolveVideoPlayback(value: string): VideoPlayback {
  const url = safeUrl(value)
  if (!url) return { kind: 'external', source: '外部视频', src: value }
  if (/\.(mp4|webm|ogg|ogv)$/i.test(url.pathname)) return { kind: 'direct', source: '视频文件', src: url.toString() }
  return bilibiliPlayback(url)
    || youtubePlayback(url)
    || platformPlayback(url)
    || { kind: 'external', source: /b23\.tv$/i.test(url.hostname) ? '哔哩哔哩短链接' : '外部视频', src: url.toString() }
}
