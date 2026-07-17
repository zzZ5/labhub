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
  await expect(navigation.getByRole('link', { name: '首页', exact: true })).toHaveAttribute('aria-current', 'page')
  const internalEntry = navigation.getByRole('link', { name: '内部平台', exact: true })
  await expect(internalEntry).toBeVisible()
  expect(await internalEntry.evaluate((node) => node.getBoundingClientRect().height)).toBeGreaterThanOrEqual(44)
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth)
  expect(overflow).toBeLessThanOrEqual(1)
})

test('公开页脚在桌面和手机端保持清晰分组', async ({ page }, testInfo) => {
  await installMockApi(page)
  await page.goto('/')

  const footer = page.locator('.portal-footer')
  await expect(footer.getByText('联系信息', { exact: true })).toBeVisible()
  await expect(footer.getByRole('navigation', { name: '相关链接' })).toBeVisible()
  await expect(footer.getByText('北京市海淀区圆明园西路2号', { exact: false })).toBeVisible()

  const columns = footer.locator('.footer-about, .footer-contact, .footer-resources')
  if (testInfo.project.name === 'mobile') {
    const links = footer.locator('.footer-links a')
    for (const height of await links.evaluateAll((nodes) => nodes.map((node) => node.getBoundingClientRect().height))) {
      expect(height).toBeGreaterThanOrEqual(44)
    }
    const boxes = await columns.evaluateAll((nodes) => nodes.map((node) => node.getBoundingClientRect()))
    expect(boxes[1].y).toBeGreaterThan(boxes[0].y)
    expect(boxes[2].y).toBeGreaterThan(boxes[1].y)
  } else {
    const boxes = await columns.evaluateAll((nodes) => nodes.map((node) => node.getBoundingClientRect()))
    expect(boxes[1].x).toBeGreaterThan(boxes[0].x)
    expect(boxes[2].x).toBeGreaterThan(boxes[1].x)
  }
})

test('首页研究方向和科研成果在桌面端使用紧凑布局', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name !== 'desktop', 'desktop home rhythm checked once')
  await installMockApi(page)
  await page.goto('/')

  const researchCards = page.locator('.research-card')
  await expect(researchCards).toHaveCount(6)
  const researchBoxes = await researchCards.evaluateAll((nodes) => nodes.map((node) => node.getBoundingClientRect()))
  expect(researchBoxes[1].y).toBe(researchBoxes[0].y)
  expect(researchBoxes[2].y).toBeGreaterThan(researchBoxes[0].y)

  const achievements = page.locator('.paper-compact')
  await expect(achievements).toHaveCount(4)
  const achievementBoxes = await achievements.evaluateAll((nodes) => nodes.map((node) => node.getBoundingClientRect()))
  expect(achievementBoxes[1].y).toBe(achievementBoxes[0].y)
  expect(achievementBoxes[1].x).toBeGreaterThan(achievementBoxes[0].x)
  const summaryWidth = await page.locator('.publication-summary').evaluate((node) => node.getBoundingClientRect().width)
  const panelWidth = await page.locator('.latest-paper-panel').evaluate((node) => node.getBoundingClientRect().width)
  expect(Math.abs(summaryWidth - panelWidth)).toBeLessThanOrEqual(1)
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
  test.setTimeout(150_000)
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
  await expect(page.getByRole('link', { name: '首页', exact: true })).toBeFocused()
  await expect.poll(() => page.evaluate(() => document.body.style.overflow)).toBe('hidden')
  await page.keyboard.press('Escape')
  await expect.poll(() => page.evaluate(() => document.body.style.overflow)).toBe('')
  await expect(page.getByRole('button', { name: '打开导航菜单' })).toBeFocused()

  await page.goto('/dashboard')
  await page.getByRole('button', { name: /菜单/ }).click()
  await expect(page.getByRole('navigation', { name: '移动端内部平台导航' }).getByRole('link', { name: '工作台', exact: true })).toBeFocused()
  await expect.poll(() => page.evaluate(() => document.body.style.overflow)).toBe('hidden')
  await page.keyboard.press('Escape')
  await expect.poll(() => page.evaluate(() => document.body.style.overflow)).toBe('')
  await expect(page.getByRole('button', { name: '打开内部平台菜单' })).toBeFocused()
})

test('研究详情和富文本新闻在窄屏保持完整阅读边界', async ({ page }) => {
  await installMockApi(page)
  await page.setViewportSize({ width: 360, height: 760 })

  await page.goto('/research/research-1?from=/research')
  await expect(page.getByRole('link', { name: '返回研究方向' }).first()).toBeVisible()
  await expect(page.getByText('研究内容', { exact: true })).toBeVisible()
  expect(await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth)).toBeLessThanOrEqual(1)

  await page.goto('/news/word-news?from=/news')
  const richContent = page.locator('.rich-content')
  await expect(richContent.getByRole('heading', { name: '实验进展' })).toBeVisible()
  await expect(richContent.locator('table')).toHaveCSS('overflow-x', 'auto')
  expect(await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth)).toBeLessThanOrEqual(1)
})

test('科研成果标签支持可读状态和键盘切换', async ({ page }) => {
  await installMockApi(page)
  await page.goto('/publications')

  const tablist = page.getByRole('tablist', { name: '科研成果类型' })
  const paperTab = tablist.getByRole('tab', { name: '论文' })
  const projectTab = tablist.getByRole('tab', { name: '项目' })
  await expect(paperTab).toHaveAttribute('aria-selected', 'true')
  await paperTab.focus()
  await page.keyboard.press('ArrowRight')
  await expect(projectTab).toBeFocused()
  await expect(projectTab).toHaveAttribute('aria-selected', 'true')
  await expect(page.getByRole('tabpanel', { name: '项目' })).toBeVisible()
})

test('高数据量列表保持分页、长文本边界和页面宽度', async ({ page }) => {
  await installMockApi(page, { highData: true })

  await page.goto('/members')
  await expect(page.getByText('50个账号', { exact: true })).toBeVisible()
  const longMember = page.locator('.account-row-card').filter({ hasText: '农业资源环境与堆肥微生物研究方向超长姓名测试成员' })
  await expect(longMember).toBeVisible()
  expect(await longMember.evaluate((node) => node.scrollWidth - node.clientWidth)).toBeLessThanOrEqual(1)
  await expect(page.getByLabel('当前页码，修改后跳转')).toBeVisible()

  await page.goto('/instruments')
  await expect(page.getByText('50设备总数', { exact: true })).toBeVisible()
  await expect(page.getByLabel('当前页码，修改后跳转')).toBeVisible()

  await page.goto('/documents')
  await expect(page.getByText('60份资料', { exact: true })).toBeVisible()
  await expect(page.getByLabel('当前页码，修改后跳转')).toBeVisible()

  await page.goto('/publications')
  await expect(page.locator('.stats-panel strong').first()).toHaveText('200')
  await expect(page.getByLabel('当前页码，修改后跳转')).toBeVisible()

  expect(await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth)).toBeLessThanOrEqual(1)
})

test('平板到宽屏的代表页面无横向溢出和按钮裁切', async ({ page }, testInfo) => {
  test.setTimeout(120_000)
  test.skip(testInfo.project.name !== 'desktop', 'desktop viewport matrix checked once')
  await installMockApi(page, { highData: true })

  for (const width of [768, 1024, 1440, 1920]) {
    await page.setViewportSize({ width, height: 900 })
    for (const route of ['/', '/publications', '/dashboard', '/cms']) {
      await page.goto(route, { waitUntil: 'domcontentloaded' })
      const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth)
      expect(overflow, `${route} overflowed at ${width}px`).toBeLessThanOrEqual(1)

      const clippedButtons = await page.locator('button:visible').evaluateAll((buttons) => buttons.filter((button) => {
        const style = window.getComputedStyle(button)
        if (style.visibility === 'hidden' || style.display === 'none') return false
        return button.scrollWidth - button.clientWidth > 1 || button.scrollHeight - button.clientHeight > 1
      }).map((button) => button.textContent?.trim() || button.getAttribute('aria-label') || '未命名按钮'))
      expect(clippedButtons, `${route} clipped buttons at ${width}px: ${clippedButtons.join(', ')}`).toEqual([])
    }
  }
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

test('科研成果可按年份筛选', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name !== 'desktop', '桌面端验证一次筛选请求和结果')
  await installMockApi(page)
  await page.goto('/publications')

  await page.locator('.result-tools select').first().selectOption('2025')
  await expect(page).toHaveURL(/year=2025/)
  const years = page.locator('.paper-row time')
  await expect(years).not.toHaveCount(0)
  for (const value of await years.allTextContents()) expect(value.trim()).toBe('2025')
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
  const longDocumentCard = page.locator('.document-card').nth(1)
  await expect(longDocumentCard).toBeVisible()
  const documentOverflow = await longDocumentCard.evaluate((node) => node.scrollWidth - node.clientWidth)
  expect(documentOverflow).toBeLessThanOrEqual(1)
  await expect(longDocumentCard.locator('.compact-data-row__title')).toHaveCSS('text-overflow', 'ellipsis')
  await page.getByText('实验方法 01', { exact: true }).click()
  await expect(page.locator('.embedded-reader')).toBeVisible()
  const readerTop = await page.locator('.document-main').evaluate((node) => node.getBoundingClientRect().top)
  const sidebarTop = await page.locator('.category-tree').evaluate((node) => node.getBoundingClientRect().top)
  expect(readerTop).toBeLessThan(sidebarTop)
})

test('学生档案与成员管理在手机端使用主从视图和摘要卡', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name !== 'mobile', 'mobile master detail behavior')
  await installMockApi(page)

  await page.goto('/students')
  await expect(page.locator('.student-directory')).toBeVisible()
  await page.locator('.student-directory').getByText('学生 01', { exact: true }).click()
  await expect(page.locator('.student-directory')).toBeHidden()
  await expect(page.getByRole('button', { name: '返回学生列表' })).toBeVisible()
  await expect(page.getByRole('button', { name: '上传资料' })).toBeVisible()
  await expect(page.getByText('开题报告', { exact: true })).toBeVisible()

  await page.goto('/members')
  await expect(page.getByRole('button', { name: '筛选' })).toBeVisible()
  const firstMember = page.locator('.account-row-card').first()
  await expect(firstMember).toBeVisible()
  const cardOverflow = await firstMember.evaluate((node) => node.scrollWidth - node.clientWidth)
  expect(cardOverflow).toBeLessThanOrEqual(1)
})

test('内部布局在平板宽度使用紧凑图标侧栏', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name !== 'desktop', 'tablet viewport checked once')
  await installMockApi(page)
  await page.setViewportSize({ width: 1024, height: 768 })
  await page.goto('/dashboard')

  const sidebarWidth = await page.locator('.internal-sidebar').evaluate((node) => Math.round(node.getBoundingClientRect().width))
  expect(sidebarWidth).toBe(76)
  await expect(page.getByRole('button', { name: '菜单' })).toBeHidden()
})

test('门户内容在大屏下使用宽内容区和紧凑双栏表单', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name !== 'desktop', 'large desktop layout checked once')
  await installMockApi(page)
  await page.setViewportSize({ width: 1920, height: 1080 })
  await page.goto('/cms')

  const contentWidth = await page.locator('.internal-content').evaluate((node) => node.getBoundingClientRect().width)
  expect(contentWidth).toBeGreaterThanOrEqual(1690)
  expect(contentWidth).toBeLessThanOrEqual(1697)

  const sections = page.locator('.site-home-form > .form-section')
  const first = await sections.nth(0).boundingBox()
  const second = await sections.nth(1).boundingBox()
  const third = await sections.nth(2).boundingBox()
  expect(first).not.toBeNull()
  expect(second).not.toBeNull()
  expect(third).not.toBeNull()
  expect(first!.width).toBeGreaterThan(second!.width + third!.width)
  expect(second!.y).toBeGreaterThan(first!.y + first!.height)
  expect(third!.y).toBe(second!.y)
  expect(third!.x).toBeGreaterThan(second!.x + second!.width)
})

test('门户内容左侧列表按内容高度显示且不被长表单拉伸', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name !== 'desktop', 'desktop editor columns checked once')
  await installMockApi(page)
  await page.goto('/cms')

  await page.getByRole('tab', { name: '新闻活动' }).click()
  const list = page.locator('.news-content-list')
  const form = page.locator('.news-form-panel')
  await expect(list.locator('.content-row')).toHaveCount(2)
  const listBox = await list.evaluate((node) => node.getBoundingClientRect())
  const formBox = await form.evaluate((node) => node.getBoundingClientRect())
  const lastRowBox = await list.locator('.content-row').last().evaluate((node) => node.getBoundingClientRect())
  expect(listBox.height).toBeLessThan(420)
  expect(listBox.height).toBeLessThan(formBox.height)
  expect(listBox.bottom - lastRowBox.bottom).toBeLessThan(36)

  await page.getByRole('tab', { name: '研究方向' }).click()
  const emptyList = page.locator('.editor-grid:visible .list-panel')
  await expect(emptyList.getByText('暂无内容，点击右上角新增。')).toBeVisible()
  expect(await emptyList.evaluate((node) => node.getBoundingClientRect().height)).toBeLessThan(260)
})

test('门户内容高数据列表紧邻搜索框并由分页控制长度', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name !== 'desktop', 'desktop CMS list layout checked once')
  await installMockApi(page, { highData: true })
  await page.setViewportSize({ width: 1440, height: 900 })
  await page.goto('/cms')
  await page.getByRole('tab', { name: '团队成员' }).click()

  const pane = page.locator('#pane-members')
  const listPanel = pane.locator('.list-panel')
  const search = listPanel.locator('.list-search')
  const rows = listPanel.locator('.content-row')
  await expect(rows).toHaveCount(12)

  const searchBox = await search.boundingBox()
  const firstRowBox = await rows.first().boundingBox()
  expect(searchBox).not.toBeNull()
  expect(firstRowBox).not.toBeNull()
  expect(firstRowBox!.y - (searchBox!.y + searchBox!.height)).toBeLessThanOrEqual(14)

  const listState = await listPanel.locator('.content-list-scroll').evaluate((node) => ({
    clientHeight: node.clientHeight,
    scrollHeight: node.scrollHeight,
    overflowY: window.getComputedStyle(node).overflowY,
  }))
  expect(listState.scrollHeight).toBe(listState.clientHeight)
  expect(listState.overflowY).toBe('visible')
  expect(listState.clientHeight).toBeGreaterThan(560)

  const importDetails = listPanel.locator('.list-extra')
  await expect(importDetails).toContainText('数据导入')
  const paginationBox = await listPanel.locator('.app-pagination').boundingBox()
  const importBox = await importDetails.boundingBox()
  expect(importBox!.y).toBeGreaterThanOrEqual(paginationBox!.y + paginationBox!.height)
})

test('门户内容手机端可从栏目列表进入编辑并返回', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name !== 'mobile', 'mobile CMS master detail flow')
  await installMockApi(page)
  await page.goto('/cms')

  await page.locator('.cms-mobile-nav select').selectOption('news')
  const pane = page.locator('#pane-news')
  await expect(pane.locator('.list-panel')).toBeVisible()
  await expect(pane.locator('.form-panel')).toBeHidden()

  await pane.locator('.content-row').first().click()
  await expect(pane.locator('.list-panel')).toBeHidden()
  await expect(pane.locator('.form-panel')).toBeVisible()
  await expect(pane.getByRole('button', { name: '返回内容列表' })).toBeVisible()

  await pane.getByLabel('标题', { exact: true }).fill('手机端编辑后的新闻标题')
  const saveRequest = page.waitForRequest((request) => request.url().includes('/cms/news-articles/') && request.method() === 'PATCH')
  await pane.getByRole('button', { name: '保存' }).click()
  expect((await saveRequest).postDataJSON().title).toBe('手机端编辑后的新闻标题')
  await expect(pane.locator('.form-panel')).toBeVisible()

  await pane.getByRole('button', { name: '返回内容列表' }).click()
  await expect(pane.locator('.list-panel')).toBeVisible()
  await expect(pane.locator('.form-panel')).toBeHidden()
})
