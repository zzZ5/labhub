import { expect, test } from '@playwright/test'

import { installMockApi } from './mockApi'

test('未登录访问内部页面后可登录并回到原页面', async ({ page }) => {
  await installMockApi(page, { authenticated: false })
  await page.goto('/instruments?q=堆肥&page=2')
  await expect(page).toHaveURL(/\/login\?redirect=/)

  await page.getByLabel('账号名或邮箱').fill('admin@cau.edu.cn')
  await page.getByLabel('密码').fill('test-password')
  await page.getByRole('button', { name: '登录' }).click()

  await expect(page).toHaveURL(/\/instruments\?q=.*page=2/)
  await expect(page.getByRole('heading', { name: '仪器平台', exact: true })).toBeVisible()

  await page.locator('.account-trigger').click()
  await page.getByRole('menuitem', { name: '退出登录' }).click()
  await expect(page).toHaveURL('/login')
})

test('科研成果翻页进入详情后保留标签、页码和搜索条件', async ({ page }) => {
  await installMockApi(page)
  await page.goto('/publications?tab=projects&page=2&q=堆肥')
  await expect(page.getByText('堆肥微生物研究项目 13')).toBeVisible()
  await page.getByText('堆肥微生物研究项目 13').click()
  await expect(page).toHaveURL(/\/publications\/projects\/13\?from=/)
  await page.getByRole('link', { name: '返回科研成果' }).click()
  await expect(page).toHaveURL(/tab=projects/)
  await expect(page).toHaveURL(/page=2/)
  await expect(page).toHaveURL(/q=/)
})

test('论文、专利和获奖附件可查看，详情返回恢复列表滚动位置', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name !== 'desktop', '滚动位置在桌面项目验证一次')
  await installMockApi(page)
  await page.goto('/publications')
  await expect(page.getByText('Composting microbial study 1', { exact: true })).toBeVisible()
  await page.evaluate(() => window.scrollTo(0, 700))
  const before = await page.evaluate(() => window.scrollY)
  await page.evaluate(() => (document.querySelector('.paper-row') as HTMLElement | null)?.click())
  await expect(page.getByRole('link', { name: '在线查看 PDF' })).toBeVisible()
  await expect(page.getByRole('link', { name: '下载 PDF' })).toBeVisible()
  await page.getByRole('link', { name: '返回科研成果' }).click()
  await expect.poll(() => page.evaluate(() => window.scrollY)).toBeGreaterThanOrEqual(Math.max(0, before - 20))

  await page.getByRole('button', { name: '专利', exact: true }).click()
  await page.getByText('一种堆肥微生物调控方法').click()
  await expect(page.getByRole('link', { name: '在线查看 PDF' })).toBeVisible()
  await page.getByRole('link', { name: '返回科研成果' }).click()

  await page.getByRole('button', { name: '获奖', exact: true }).click()
  await page.getByText('农业资源环境科技成果奖').click()
  await expect(page.getByRole('link', { name: '在线查看附件' })).toBeVisible()
  await expect(page.getByRole('link', { name: '下载附件' })).toBeVisible()
})

test('仪器搜索、分页、详情返回和编辑入口可用', async ({ page }) => {
  await installMockApi(page)
  await page.goto('/instruments')
  await expect(page.getByText('堆肥设备 01')).toBeVisible()

  await page.getByRole('button', { name: '新建设备' }).click()
  const instrumentDialog = page.getByRole('dialog', { name: '新建设备' })
  await instrumentDialog.getByLabel('仪器名称').fill('E2E 堆肥设备')
  const createRequest = page.waitForRequest((request) => request.url().endsWith('/api/instruments/instruments/') && request.method() === 'POST')
  await instrumentDialog.getByRole('button', { name: '保存设备' }).click()
  expect((await createRequest).postDataJSON().name).toBe('E2E 堆肥设备')

  await page.getByRole('button', { name: '下一页' }).click()
  await expect(page).toHaveURL(/page=2/)
  await expect(page.getByText('堆肥设备 13')).toBeVisible()

  await page.getByText('堆肥设备 13').click()
  await expect(page.getByRole('heading', { name: '堆肥设备 13' })).toBeVisible()
  await expect(page.getByRole('button', { name: '编辑设备' })).toBeVisible()
  await page.getByRole('link', { name: '返回仪器平台' }).click()
  await expect(page).toHaveURL(/page=2/)

  await page.getByPlaceholder('搜索仪器名称、型号、位置或说明').fill('设备 02')
  await expect(page.getByText('堆肥设备 02')).toBeVisible()
  await expect(page.getByText('堆肥设备 01')).toHaveCount(0)
})

test('内部资料与学生列表可搜索、翻页并打开详情', async ({ page }) => {
  await installMockApi(page)

  await page.goto('/documents')
  await page.getByRole('button', { name: '上传资料' }).click()
  const documentDialog = page.getByRole('dialog', { name: '上传内部资料' })
  await documentDialog.getByLabel('资料标题').fill('E2E 实验资料')
  await documentDialog.locator('input[type="file"]').setInputFiles({ name: 'e2e.pdf', mimeType: 'application/pdf', buffer: Buffer.from('%PDF-1.4') })
  const documentRequest = page.waitForRequest((request) => request.url().endsWith('/api/documents/documents/') && request.method() === 'POST')
  await documentDialog.getByRole('button', { name: '保存资料' }).click()
  await documentRequest

  await page.getByRole('button', { name: '下一页' }).click()
  await expect(page).toHaveURL(/page=2/)
  await page.getByText('实验方法 13').click()
  await expect(page).toHaveURL(/document=13/)
  await expect(page.getByText(/^method-13\.pdf（/)).toBeVisible()

  await page.goto('/students')
  await page.getByPlaceholder('搜索姓名、年级、方向').fill('学生 13')
  await expect(page.getByRole('heading', { name: '学生 13' })).toBeVisible()
  await expect(page.getByText('学生 01', { exact: true })).toHaveCount(0)
  await page.getByRole('button', { name: '上传资料' }).click()
  const archiveDialog = page.getByRole('dialog', { name: '上传学生资料' })
  await archiveDialog.getByLabel('标题').fill('E2E 开题报告')
  await archiveDialog.locator('input[type="file"]').setInputFiles({ name: 'proposal.pdf', mimeType: 'application/pdf', buffer: Buffer.from('%PDF-1.4') })
  const archiveRequest = page.waitForRequest((request) => request.url().endsWith('/api/students/archive-files/') && request.method() === 'POST')
  await archiveDialog.getByRole('button', { name: '保存资料' }).click()
  await archiveRequest
})

test('成员管理可创建账号并为学生账号生成唯一档案', async ({ page }) => {
  await installMockApi(page)
  await page.goto('/members')

  await page.getByRole('button', { name: '新建账号' }).click()
  await page.getByLabel('姓名').fill('新成员')
  await page.getByLabel('邮箱').fill('new-member@cau.edu.cn')
  await page.getByLabel('初始密码').fill('StrongPassword123')
  await page.getByRole('button', { name: '创建账号' }).click()
  await expect(page.getByText('新成员', { exact: true })).toBeVisible()

  const studentRow = page.locator('.account-row-card').filter({ hasText: '待建档学生' })
  await studentRow.getByRole('button', { name: '生成档案' }).click()
  await expect(studentRow.getByRole('link', { name: '待建档学生' })).toBeVisible()
  await expect(studentRow.getByRole('button', { name: '生成档案' })).toHaveCount(0)

  await studentRow.getByRole('button', { name: '编辑' }).click()
  const drawer = page.locator('.el-drawer').filter({ hasText: '编辑成员账号' })
  await drawer.getByText('已毕业/离组', { exact: true }).click()
  await drawer.getByText('网站编辑', { exact: true }).click()
  const updateRequest = page.waitForRequest((request) => request.url().includes('/accounts/users/2/update/') && request.method() === 'PATCH')
  const roleRequest = page.waitForRequest((request) => request.url().includes('/accounts/users/2/roles/') && request.method() === 'POST')
  await drawer.getByRole('button', { name: '保存账号' }).click()
  const payload = (await updateRequest).postDataJSON()
  const rolePayload = (await roleRequest).postDataJSON()
  expect(payload.membership_status).toBe('former')
  expect(rolePayload.role_code).toBe('editor')
})

test('门户新闻切换不串联 Word 文件状态，成果 Excel 可导入', async ({ page }) => {
  await installMockApi(page)
  await page.goto('/cms')

  await page.getByRole('tab', { name: '新闻活动' }).click()
  const newsPane = page.locator('#pane-news')
  await newsPane.getByRole('button', { name: /Word 新闻稿/ }).click()
  await expect(page.getByText('first.docx')).toBeVisible()
  await newsPane.getByRole('button', { name: /普通新闻稿/ }).click()
  await expect(page.getByText('first.docx')).toHaveCount(0)
  await expect(page.locator('.rich-editor')).toContainText('第二条新闻')
  await newsPane.getByLabel('标题', { exact: true }).fill('更新后的普通新闻稿')
  const saveRequest = page.waitForRequest((request) => request.url().includes('/api/cms/news-articles/plain-news/') && request.method() === 'PATCH')
  await newsPane.getByRole('button', { name: '保存' }).click()
  expect((await saveRequest).postDataJSON().title).toBe('更新后的普通新闻稿')

  await page.getByRole('tab', { name: '论文成果' }).click()
  await page.locator('#pane-publications input[type="file"][accept=".xlsx"]').setInputFiles({
    name: 'publications.xlsx',
    mimeType: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    buffer: Buffer.from('test workbook'),
  })
  await expect(page.getByText(/导入完成/)).toBeVisible()
})

test('门户横幅列表可读取当前图片和文件信息', async ({ page }) => {
  await installMockApi(page)
  await page.goto('/cms')
  await page.getByRole('tab', { name: '首页横幅' }).click()
  await page.getByRole('button', { name: /团队合影/ }).click()
  await expect(page.getByRole('img', { name: '图片预览' })).toBeVisible()
  await expect(page.locator('.file-meta').getByText(/8.0 KB/)).toBeVisible()
  await expect(page.locator('.desktop-preview')).toBeVisible()
  await expect(page.locator('.mobile-preview')).toBeVisible()
  await expect(page.locator('.banner-safe-area')).toHaveCount(2)
})

test('门户内容各栏目在窄屏可横向访问且不会被裁掉', async ({ page }) => {
  await installMockApi(page)
  await page.setViewportSize({ width: 390, height: 844 })
  await page.goto('/cms')

  await expect(page.getByRole('tab', { name: '站点首页' })).toBeVisible()
  await page.getByRole('tab', { name: '获奖成果' }).scrollIntoViewIfNeeded()
  await expect(page.getByRole('tab', { name: '获奖成果' })).toBeVisible()
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth)
  expect(overflow).toBeLessThanOrEqual(1)
})
