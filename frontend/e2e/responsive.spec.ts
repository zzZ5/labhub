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
