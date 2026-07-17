import type { Page, Route } from '@playwright/test'

export const adminUser = {
  id: 1,
  username: 'admin',
  email: 'admin@cau.edu.cn',
  first_name: '',
  last_name: '',
  is_active: true,
  is_staff: true,
  is_superuser: true,
  roles: ['admin', 'editor', 'document_manager', 'instrument_manager'],
  profile: {
    real_name: '测试管理员',
    avatar: '',
    phone: '',
    school_identity: 'supervisor',
    school_identity_label: '硕博导师',
    membership_status: 'active',
    membership_status_label: '在组',
    bio: '',
    is_approved: true,
  },
}

const siteSetting = {
  id: 1,
  site_name: '中农雨磷',
  site_subtitle: '中国农业大学资源与环境学院',
  hero_title: '中农雨磷',
  hero_subtitle: '堆肥微生物与农业有机废弃物资源化研究',
  home_intro: '围绕农业有机废弃物资源化和堆肥微生物过程开展研究。',
  footer_description: '中国农业大学资源与环境学院课题组。',
  address: '北京市海淀区圆明园西路2号',
  external_links: [],
  logo: '',
  favicon: '',
  hero_image: '',
  banner_interval_seconds: 6,
}

export const instruments = Array.from({ length: 14 }, (_, index) => ({
  id: index + 1,
  name: `堆肥设备 ${String(index + 1).padStart(2, '0')}`,
  model: `Model-${index + 1}`,
  category: null,
  location_detail: `实验楼 ${200 + index}`,
  manager: 1,
  manager_name: '测试管理员',
  image: '',
  image_size: 0,
  status: index === 13 ? 'maintenance' : 'normal',
  status_label: index === 13 ? '维护中' : '正常',
  notes: '用于堆肥样品处理，使用前请阅读操作说明。',
  sort_order: index + 1,
}))

export const students = Array.from({ length: 13 }, (_, index) => ({
  id: index + 1,
  user: index + 10,
  user_email: `student${index + 1}@cau.edu.cn`,
  user_username: `student${index + 1}`,
  name: `学生 ${String(index + 1).padStart(2, '0')}`,
  avatar: '',
  avatar_size: 0,
  degree_type: index % 3 === 0 ? 'phd' : 'master',
  degree_label: index % 3 === 0 ? '博士' : '硕士',
  grade: '2025',
  research_direction: '堆肥微生物过程',
  advisors: [],
  advisor_details: [],
  can_edit: true,
  can_delete: true,
  archive_files: index === 0 ? [{
    id: 1,
    student: 1,
    file_type: 'proposal',
    file_type_label: '开题报告',
    title: '开题报告',
    file: '/media/students/proposal.pdf',
    file_size: 2_048_000,
    preview_pdf: '/media/students/proposal-preview.pdf',
    preview_status: 'ready',
    preview_error: '',
    original_filename: '2025级学生01农业有机废弃物堆肥微生物过程研究开题报告最终归档版本.pdf',
    uploaded_at: '2026-07-17T10:00:00Z',
    description: '开题报告归档文件',
    can_delete: true,
  }] : [],
}))

export const documents = Array.from({ length: 13 }, (_, index) => ({
  id: index + 1,
  title: `实验方法 ${String(index + 1).padStart(2, '0')}`,
  category: { id: 1, name: '实验方法', slug: 'methods', parent: null, description: '', sort_order: 1 },
  description: '堆肥实验操作方法。',
  allow_download: true,
  status: 'active',
  status_label: '有效',
  updated_at: '2026-07-17T10:00:00Z',
  original_filename: `method-${index + 1}.pdf`,
  uploaded_by_name: '测试管理员',
  uploaded_at: '2026-07-17T10:00:00Z',
  file_size: 1024,
  file_type: 'application/pdf',
  preview_status: 'ready',
  preview_error: '',
  can_view: true,
  can_preview: true,
  can_download: true,
  can_edit: true,
  can_delete: true,
}))

const publications = Array.from({ length: 13 }, (_, index) => ({
  id: index + 1,
  title: `Composting microbial study ${index + 1}`,
  authors: 'Wei, Y.; Li, J.',
  journal: 'Bioresource Technology',
  year: 2026 - (index % 3),
  volume: '436',
  issue: '',
  pages: `${132900 + index}`,
  doi: `10.1000/labhub.${index + 1}`,
  abstract: 'A study of microbial succession during composting.',
  pdf_file: index === 0 ? '/media/papers/demo.pdf' : '',
  pdf_file_size: index === 0 ? 2048 : 0,
  impact_factor: null,
  jcr_partition: '',
  cas_partition: '',
  is_representative: false,
  visibility: 'public',
  sort_order: 0,
}))

const projects = Array.from({ length: 13 }, (_, index) => ({
  id: index + 1,
  title: `堆肥微生物研究项目 ${index + 1}`,
  project_number: `CAU-${index + 1}`,
  funding_source: '国家自然科学基金',
  principal_investigator: '团队负责人',
  start_date: '2025-01-01',
  end_date: '2027-12-31',
  status: '在研',
  description: '围绕堆肥微生物过程开展研究。',
}))

const patents = [{ id: 1, title: '一种堆肥微生物调控方法', patent_number: 'CN202600001', inventors: '团队成员', application_date: '2026-01-01', authorization_date: '', status: '申请中', pdf_file: '/media/patents/demo.pdf', pdf_file_size: 2048 }]
const awards = [{ id: 1, title: '农业资源环境科技成果奖', award_level: '省部级', award_date: '2026-01-01', participants: '团队成员', description: '团队科研成果。', image: '', image_size: 0, attachment: '/media/awards/demo.pdf', attachment_size: 2048 }]

function pageResult<T>(items: T[], url: URL) {
  const page = Math.max(1, Number(url.searchParams.get('page')) || 1)
  const size = Math.max(1, Number(url.searchParams.get('page_size')) || 12)
  const query = (url.searchParams.get('search') || '').toLowerCase()
  const filtered = query ? items.filter((item) => JSON.stringify(item).toLowerCase().includes(query)) : items
  const start = (page - 1) * size
  return { count: filtered.length, next: null, previous: null, results: filtered.slice(start, start + size) }
}

async function json(route: Route, data: unknown, status = 200) {
  await route.fulfill({ status, contentType: 'application/json', body: JSON.stringify(data) })
}

export async function installMockApi(page: Page, options: { authenticated?: boolean } = {}) {
  let authenticated = options.authenticated ?? true
  const instrumentState = instruments.map((item) => ({ ...item }))
  const studentState = students.map((item) => ({ ...item }))
  const userState = [
    adminUser,
    {
      ...adminUser,
      id: 2,
      username: 'student-user',
      email: 'student@cau.edu.cn',
      is_staff: false,
      is_superuser: false,
      roles: [],
      profile: { ...adminUser.profile, real_name: '待建档学生', school_identity: 'master', school_identity_label: '硕士生' },
    },
  ]
  const newsItems = [
    {
      id: 1, title: 'Word 新闻稿', slug: 'word-news', summary: '已上传 Word。', content: '<p>第一条新闻</p>', word_html: '<p>第一条新闻</p>',
      word_file: '/media/news/word/first.docx', word_file_size: 4096, cover_image: '/media/news/cover/first.jpg', cover_image_size: 2048,
      category: { id: 1, name: '科研进展', slug: 'research-progress', description: '', sort_order: 1 }, event_date: '2026-07-17', location: '', status: 'published', visibility: 'public', is_pinned: false, images: [],
    },
    {
      id: 2, title: '普通新闻稿', slug: 'plain-news', summary: '直接编辑正文。', content: '<p>第二条新闻</p>', word_html: '',
      word_file: '', word_file_size: 0, cover_image: '', cover_image_size: 0,
      category: { id: 1, name: '科研进展', slug: 'research-progress', description: '', sort_order: 1 }, event_date: '2026-07-16', location: '', status: 'published', visibility: 'public', is_pinned: false, images: [],
    },
  ]
  const banners = [{ id: 1, title: '团队合影', subtitle: '中农雨磷', image: '/media/banners/team.jpg', image_size: 8192, link_url: '', sort_order: 1, is_active: true }]

  await page.route((url) => url.pathname.startsWith('/api/'), async (route) => {
    const request = route.request()
    const url = new URL(request.url())
    const path = url.pathname.replace(/^\/api/, '')
    const method = request.method()

    if (path === '/csrf/') return json(route, {})
    if (path === '/accounts/auth/me/') return authenticated ? json(route, adminUser) : json(route, { detail: '未登录' }, 401)
    if (path === '/accounts/auth/login/' && method === 'POST') {
      authenticated = true
      return json(route, adminUser)
    }
    if (path === '/accounts/auth/logout/' && method === 'POST') {
      authenticated = false
      return json(route, {})
    }
    if (path === '/portal/site-setting/') return json(route, siteSetting)
    if (path === '/portal/contact/') return json(route, { email: 'lab@cau.edu.cn', address: siteSetting.address })
    if (path === '/news/articles/') return json(route, newsItems)
    if (path === '/news/categories/') return json(route, [{ id: 1, name: '科研进展', slug: 'research-progress', description: '', sort_order: 1 }])
    if (path === '/portal/banners/' || path === '/portal/research-directions/' || path === '/members/') return json(route, [])
    if (path === '/dashboard/') return json(route, { summary: [], instrument_status: [], latest_documents: [], todos: [], student_archives: [], recent_downloads: [] })
    if (path === '/accounts/roles/') return json(route, [
      { id: 1, name: '系统管理员', code: 'admin', description: '', is_system: true },
      { id: 2, name: '网站编辑', code: 'editor', description: '', is_system: true },
      { id: 3, name: '资料管理员', code: 'document_manager', description: '', is_system: true },
      { id: 4, name: '仪器管理员', code: 'instrument_manager', description: '', is_system: true },
    ])
    if (path === '/accounts/users/' || path === '/accounts/users/pending/') return json(route, path.includes('pending') ? [] : userState)
    if (path === '/accounts/users/create/' && method === 'POST') {
      const payload = request.postDataJSON() as Record<string, unknown>
      const created = {
        ...adminUser,
        id: 3,
        username: String(payload.username || payload.email || 'new-user'),
        email: String(payload.email || ''),
        is_staff: false,
        is_superuser: false,
        roles: Array.isArray(payload.system_roles) ? payload.system_roles : [],
        profile: {
          ...adminUser.profile,
          real_name: String(payload.real_name || '新成员'),
          school_identity: String(payload.school_identity || 'other'),
          school_identity_label: '其他成员',
        },
      }
      userState.push(created)
      return json(route, created, 201)
    }
    if (/^\/accounts\/users\/\d+\/update\/$/.test(path) && method === 'PATCH') return json(route, userState.find((item) => item.id === Number(path.split('/')[3])) || userState[0])
    if (/^\/accounts\/users\/\d+\/(roles|approve|reset-password)\/?/.test(path)) return json(route, userState.find((item) => item.id === Number(path.split('/')[3])) || userState[0])
    if (path === '/students/profiles/' && method === 'GET') return json(route, studentState)
    if (path === '/students/profiles/' && method === 'POST') {
      const created = { ...students[0], id: 99, user: 2, name: '待建档学生', user_email: 'student@cau.edu.cn', user_username: 'student-user' }
      studentState.push(created)
      return json(route, created, 201)
    }
    if (path === '/documents/categories/') return json(route, [{ id: 1, name: '实验方法', slug: 'methods', parent: null, description: '', sort_order: 1 }])
    if (path === '/documents/documents/') return json(route, documents)
    if (/^\/documents\/documents\/\d+\/$/.test(path)) return json(route, documents.find((item) => item.id === Number(path.split('/')[3])) || documents[0])
    if (path === '/instruments/instruments/' && method === 'GET') return json(route, instrumentState)
    if (path === '/instruments/instruments/' && method === 'POST') {
      const created = { ...instruments[0], id: 99, name: '新建设备' }
      instrumentState.push(created)
      return json(route, created, 201)
    }
    if (/^\/instruments\/instruments\/\d+\/$/.test(path)) {
      const id = Number(path.split('/')[3])
      if (method === 'DELETE') {
        const index = instrumentState.findIndex((item) => item.id === id)
        if (index >= 0) instrumentState.splice(index, 1)
        return route.fulfill({ status: 204, body: '' })
      }
      return json(route, instrumentState.find((item) => item.id === id) || instrumentState[0])
    }
    if (path === '/publications/publications/') {
      const year = Number(url.searchParams.get('year')) || 0
      const rows = year ? publications.filter((item) => item.year === year) : publications
      return json(route, pageResult(rows, url))
    }
    if (path === '/publications/projects/') return json(route, pageResult(projects, url))
    if (path === '/publications/patents/') return json(route, pageResult(patents, url))
    if (path === '/publications/awards/') return json(route, pageResult(awards, url))
    if (path === '/publications/stats/') return json(route, { publications: publications.length, projects: projects.length, patents: patents.length, awards: awards.length })
    if (/^\/publications\/publications\/\d+\/$/.test(path)) return json(route, publications.find((item) => item.id === Number(path.split('/')[3])) || publications[0])
    if (/^\/publications\/projects\/\d+\/$/.test(path)) return json(route, projects.find((item) => item.id === Number(path.split('/')[3])) || projects[0])
    if (/^\/publications\/patents\/\d+\/$/.test(path)) return json(route, patents[0])
    if (/^\/publications\/awards\/\d+\/$/.test(path)) return json(route, awards[0])
    if (path.startsWith('/cms/')) {
      if (method === 'GET') {
        if (path === '/cms/site-settings/') return json(route, [siteSetting])
        if (path === '/cms/contact-info/') return json(route, [{ id: 1, email: 'lab@cau.edu.cn', address: siteSetting.address }])
        if (path === '/cms/news-categories/') return json(route, [{ id: 1, name: '科研进展', slug: 'research-progress', description: '', sort_order: 1 }])
        if (path === '/cms/news-articles/') return json(route, newsItems)
        if (path === '/cms/home-banners/') return json(route, banners)
        return json(route, [])
      }
      if (path.endsWith('/import-file/')) return json(route, { created: 1, updated: 0, skipped: 0, images: 0, total: 1 })
      if (/^\/cms\/news-articles\/[^/]+\/$/.test(path) && method === 'PATCH') {
        const slug = path.split('/')[3]
        return json(route, newsItems.find((item) => item.slug === slug) || newsItems[0])
      }
      return json(route, { id: 1, ...siteSetting })
    }
    return json(route, method === 'GET' ? [] : {})
  })
}
