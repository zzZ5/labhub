import { expect, test } from '@playwright/test'
import { installMockApi } from './mockApi'

const paper = {
  id: 1, title: 'Composting improves nutrient recovery from organic residues', chinese_title: '堆肥促进有机废弃物养分回收',
  authors: 'Test Author', journal: 'Nature Sustainability', year: 2026, doi: '10.1234/test',
  topic: 'compost', topic_label: '堆肥与腐殖化', publisher_url: 'https://doi.org/10.1234/test', wechat_url: '',
  preview_url: '/api/wechat/papers/1/preview/', download_url: '/api/wechat/papers/1/download/',
}

test('论文原文支持搜索筛选及手机浏览', async ({ page }, testInfo) => {
  await installMockApi(page)
  await page.route('**/api/wechat/papers/**', route => {
    const params = new URL(route.request().url()).searchParams
    const rows = params.get('topic') === 'soil' || params.get('search') === 'missing' ? [] : [paper]
    return route.fulfill({ json: { count: rows.length, results: rows } })
  })
  await page.goto('/papers')
  await expect(page).toHaveURL(/\/literature-digest\?tab=papers$/)
  await expect(page.getByRole('heading', { name: '公众号速递', exact: true })).toBeVisible()
  await expect(page.getByRole('heading', { name: paper.chinese_title })).toBeVisible()
  await expect(page.getByRole('link', { name: '在线阅读 PDF' })).toHaveAttribute('href', paper.preview_url)
  await expect(page.getByRole('link', { name: '下载 PDF' })).toHaveAttribute('href', paper.download_url)
  expect(await page.evaluate(() => document.documentElement.scrollWidth - innerWidth)).toBeLessThanOrEqual(1)
  await page.screenshot({ path: `test-results/original-papers-${testInfo.project.name}.png`, fullPage: true })
  await page.getByRole('searchbox').fill('missing')
  await page.getByRole('button', { name: '搜索', exact: true }).click()
  await expect(page.getByText('暂无匹配的论文')).toBeVisible()
  await page.getByRole('searchbox').fill('')
  await page.getByRole('button', { name: '搜索', exact: true }).click()
  await expect(page.getByRole('heading', { name: paper.chinese_title })).toBeVisible()
  await page.getByRole('combobox').selectOption('soil')
  await expect(page.getByText('暂无匹配的论文')).toBeVisible()
})

test('没有分享许可的文献不展示PDF按钮', async ({ page }) => {
  await installMockApi(page)
  await page.route('**/api/wechat/papers/**', route => route.fulfill({ json: { count: 1, results: [{ ...paper, preview_url: '', download_url: '' }] } }))
  await page.goto('/papers')
  await expect(page.getByText('本站未提供 PDF', { exact: true })).toBeVisible()
  await expect(page.getByRole('link', { name: '下载 PDF' })).toHaveCount(0)
  await expect(page.getByRole('link', { name: '原文入口' })).toBeVisible()
})

test('公众号速递在解读和原文间切换且兼容旧入口参数', async ({ page }) => {
  await installMockApi(page)
  await page.route('**/api/wechat/papers/**', route => route.fulfill({ json: { count: 1, results: [paper] } }))
  await page.route('**/api/wechat/accounts/**', route => route.fulfill({ json: [{ id: 1, name: '有机循环前沿' }] }))
  await page.route('**/api/wechat/articles/**', route => route.fulfill({ json: { count: 1, results: [{
    id: 2, account: { id: 1, name: '有机循环前沿' }, title: '最新堆肥文献解读', summary: '堆肥研究进展',
    source_url: 'https://mp.weixin.qq.com/s/test', cover_url: '', published_at: '2026-11-11T08:00:00Z',
  }] } }))
  await page.goto('/papers?q=composting&topic=compost')
  await expect(page).toHaveURL(/literature-digest.*tab=papers/)
  await expect(page.getByRole('searchbox')).toHaveValue('composting')
  const tabs = page.getByRole('navigation', { name: '公众号速递栏目' })
  await tabs.getByRole('link', { name: '文章解读' }).click()
  await expect(page.getByRole('heading', { name: '最新堆肥文献解读' })).toBeVisible()
  await expect(page.getByRole('searchbox')).toHaveValue('')
  await tabs.getByRole('link', { name: '论文原文' }).click()
  await expect(page.getByRole('heading', { name: paper.chinese_title })).toBeVisible()
  await expect(page.getByRole('searchbox')).toHaveValue('')
  expect(await page.evaluate(() => document.querySelectorAll('.portal-shell').length)).toBe(1)
})

test('后台可录入原文并以默认不公开方式上传PDF', async ({ page }, testInfo) => {
  await installMockApi(page, { authenticated: true })
  let saved = false
  await page.route('**/api/wechat/manage/papers/**', async route => {
    if (route.request().method() === 'POST') {
      const body = route.request().postData() || ''
      expect(body).toContain('name="doi"\r\n\r\n10.1234/test')
      expect(body).toContain('name="is_visible"\r\n\r\nfalse')
      expect(body).toContain('name="sharing"\r\n\r\nlink_only')
      expect(body).toContain('filename="paper.pdf"')
      saved = true
      return route.fulfill({ status: 201, json: { ...paper, has_pdf: true, is_visible: false } })
    }
    return route.fulfill({ json: { count: 0, results: [] } })
  })
  await page.goto('/cms')
  if (testInfo.project.name === 'mobile') await page.locator('#cms-section-select').selectOption('wechat')
  else await page.getByRole('tab', { name: '公众号速递', exact: true }).click()
  await page.getByRole('tab', { name: '论文原文', exact: true }).click()
  await page.getByRole('button', { name: '添加原文' }).click()
  const dialog = page.getByRole('dialog')
  await dialog.getByRole('textbox', { name: 'DOI', exact: true }).fill('10.1234/test')
  await expect(dialog.getByRole('textbox', { name: '原文标题', exact: true })).not.toBeVisible()
  await dialog.locator('input[type=file]').setInputFiles({ name: 'paper.pdf', mimeType: 'application/pdf', buffer: Buffer.from('%PDF-1.4\n%%EOF') })
  await dialog.screenshot({ path: `test-results/original-paper-form-${testInfo.project.name}.png` })
  await dialog.getByRole('button', { name: '保存', exact: true }).click()
  await expect(dialog).not.toBeVisible()
  expect(saved).toBe(true)
})

test('DOI识别填入元数据，更换DOI会清除旧文献信息', async ({ page }, testInfo) => {
  await installMockApi(page, { authenticated: true })
  await page.route('**/api/wechat/manage/papers/**', async route => {
    if (route.request().url().endsWith('/lookup/')) {
      return route.fulfill({ json: { ...paper, metadata_source: 'Crossref' } })
    }
    return route.fulfill({ json: { count: 0, results: [] } })
  })
  await page.goto('/cms')
  if (testInfo.project.name === 'mobile') await page.locator('#cms-section-select').selectOption('wechat')
  else await page.getByRole('tab', { name: '公众号速递', exact: true }).click()
  await page.getByRole('tab', { name: '论文原文', exact: true }).click()
  await page.getByRole('button', { name: '添加原文' }).click()
  const dialog = page.getByRole('dialog')
  const doi = dialog.getByRole('textbox', { name: 'DOI', exact: true })
  await doi.fill('10.1234/test')
  await dialog.getByRole('button', { name: '识别信息', exact: true }).click()
  await expect(dialog.locator('.metadata-summary')).toContainText(paper.title)
  await expect(dialog.locator('.metadata-summary')).toContainText('Crossref')
  await doi.fill('10.1234/another')
  await expect(dialog.locator('.metadata-summary')).toHaveCount(0)
  await dialog.getByText('补充信息与分享设置（可选）', { exact: true }).click()
  await expect(dialog.getByRole('textbox', { name: '原文标题', exact: true })).toHaveValue('')
})
