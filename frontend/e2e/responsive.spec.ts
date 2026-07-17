import { expect, test } from '@playwright/test'

import { installMockApi } from './mockApi'

test('公开导航在手机端完整展开', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name !== 'mobile', '仅在手机项目执行')
  await installMockApi(page)
  await page.goto('/')
  await page.getByRole('button', { name: '打开导航菜单' }).click()

  const navigation = page.getByRole('navigation', { name: '主导航' })
  for (const name of ['首页', '研究方向', '团队成员', '科研成果', '新闻活动', '内部平台']) {
    await expect(navigation.getByRole('link', { name, exact: true })).toBeVisible()
  }
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth)
  expect(overflow).toBeLessThanOrEqual(1)
})

test('内部侧栏在手机端转换为完整菜单', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name !== 'mobile', '仅在手机项目执行')
  await installMockApi(page)
  await page.goto('/dashboard')
  await page.getByRole('button', { name: /菜单/ }).click()

  for (const name of ['工作台', '内部资料', '仪器平台', '学生档案', '门户内容', '成员管理', '返回官网']) {
    await expect(page.getByRole('link', { name, exact: true })).toBeVisible()
  }
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth)
  expect(overflow).toBeLessThanOrEqual(1)
})

test('core pages do not overflow at common phone widths', async ({ page }, testInfo) => {
  test.setTimeout(90_000)
  test.skip(testInfo.project.name !== 'mobile', 'mobile viewport coverage')
  await installMockApi(page)
  const routes = ['/', '/research', '/team', '/publications', '/news', '/dashboard', '/documents', '/instruments', '/students', '/cms', '/members']

  for (const width of [320, 360, 390]) {
    await page.setViewportSize({ width, height: 760 })
    for (const route of routes) {
      await page.goto(route, { waitUntil: 'domcontentloaded' })
      const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth)
      expect(overflow, `${route} overflowed at ${width}px`).toBeLessThanOrEqual(1)
    }
  }
})

test('mobile menus lock the page and close with Escape', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name !== 'mobile', 'mobile menu behavior')
  await installMockApi(page)

  await page.goto('/')
  await page.getByRole('button', { name: '打开导航菜单' }).click()
  await expect.poll(() => page.evaluate(() => document.body.style.overflow)).toBe('hidden')
  await page.keyboard.press('Escape')
  await expect.poll(() => page.evaluate(() => document.body.style.overflow)).toBe('')

  await page.goto('/dashboard')
  await page.getByRole('button', { name: /菜单/ }).click()
  await expect.poll(() => page.evaluate(() => document.body.style.overflow)).toBe('hidden')
  await page.keyboard.press('Escape')
  await expect.poll(() => page.evaluate(() => document.body.style.overflow)).toBe('')
})

test('missing images never hide card content', async ({ page }) => {
  await installMockApi(page)

  await page.goto('/instruments')
  const instrument = page.locator('.instrument-card').first()
  await expect(instrument.getByText('暂无设备图片')).toBeVisible()
  await expect(instrument.locator('h2')).not.toHaveText('')
  await expect(instrument.locator('.instrument-body')).toBeVisible()

  await page.goto('/news')
  const news = page.locator('.news-card').filter({ hasText: '普通新闻稿' })
  await expect(news.getByRole('img', { name: '普通新闻稿暂无封面' })).toBeVisible()
  await expect(news.locator('h2')).not.toHaveText('')
  await expect(news.locator('.news-card-content')).toBeVisible()
})

test('科研成果筛选在手机端按需展开', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name !== 'mobile', 'mobile filter behavior')
  await installMockApi(page)
  await page.goto('/publications')

  const search = page.getByPlaceholder('搜索论文题名、作者、期刊或 DOI')
  await expect(search).toBeHidden()
  await page.getByRole('button', { name: '筛选论文' }).click()
  await expect(search).toBeVisible()
  await expect(page.getByRole('button', { name: '收起筛选' })).toBeVisible()
})

test('认证状态页提供清晰返回路径', async ({ page }) => {
  await installMockApi(page)

  await page.goto('/pending')
  await expect(page.getByRole('heading', { name: '账号等待审核' })).toBeVisible()
  await expect(page.getByRole('link', { name: '返回官网' }).first()).toBeVisible()

  await page.goto('/access-denied')
  await expect(page.getByRole('heading', { name: '当前账号没有访问权限' })).toBeVisible()
  await expect(page.getByRole('link', { name: '返回工作台' })).toBeVisible()
})

test('个人设置与资料阅读在手机端优先展示主要内容', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name !== 'mobile', 'mobile content order')
  await installMockApi(page)

  await page.goto('/account')
  const formTop = await page.locator('.account-panels').evaluate((node) => node.getBoundingClientRect().top)
  const summaryTop = await page.locator('.account-summary').evaluate((node) => node.getBoundingClientRect().top)
  expect(formTop).toBeLessThan(summaryTop)
  await expect(page.getByText('账号安全', { exact: true })).toBeVisible()

  await page.goto('/documents')
  await page.getByText('实验方法 01', { exact: true }).click()
  await expect(page.locator('.embedded-reader')).toBeVisible()
  const readerTop = await page.locator('.document-main').evaluate((node) => node.getBoundingClientRect().top)
  const sidebarTop = await page.locator('.category-tree').evaluate((node) => node.getBoundingClientRect().top)
  expect(readerTop).toBeLessThan(sidebarTop)
})
