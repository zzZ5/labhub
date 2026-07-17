import { reactive, ref } from 'vue'

import { cmsApi } from '../../../api/cms'
import type { ContactInfo, SiteSetting } from '../../../api/publicPortal'
import { useSiteBrandStore } from '../../../stores/siteBrand'
import { useCmsEditorMutation } from './useCmsEditorMutation'

type CmsForm = Record<string, unknown>

export function useCmsSiteSettings(afterChange: () => void | Promise<void>) {
  const siteBrand = useSiteBrandStore()
  const editingSiteId = ref<number | null>(null)
  const editingContactId = ref<number | null>(null)
  const logo = ref('')
  const favicon = ref('')
  const heroImage = ref('')
  const logoSize = ref(0)
  const faviconSize = ref(0)
  const heroImageSize = ref(0)
  const siteForm = reactive<CmsForm>({
    site_name: '',
    site_subtitle: '',
    hero_subtitle: '',
    banner_interval_seconds: 6,
    description: '', footer_text: '', contact_email: '', contact_phone: '', address: '',
    logo: undefined, favicon: undefined, hero_image: undefined,
  })
  const contactForm = reactive<CmsForm>({
    title: '',
    content: '', email: '', phone: '', address: '', map_url: '',
  })
  const externalLinks = reactive(Array.from({ length: 3 }, () => ({ label: '', url: '' })))
  const { saving, progress, save } = useCmsEditorMutation(async () => {
    await afterChange()
    await siteBrand.load(true)
  })

  function fill(setting?: SiteSetting, contact?: ContactInfo) {
    editingSiteId.value = setting?.id || null
    editingContactId.value = contact?.id || null
    logo.value = setting?.logo || ''
    favicon.value = setting?.favicon || ''
    heroImage.value = setting?.hero_image || ''
    logoSize.value = setting?.logo_size || 0
    faviconSize.value = setting?.favicon_size || 0
    heroImageSize.value = setting?.hero_image_size || 0
    Object.assign(siteForm, {
      site_name: setting?.site_name || '',
      site_subtitle: setting?.site_subtitle || '',
      hero_subtitle: setting?.hero_subtitle || '',
      banner_interval_seconds: setting?.banner_interval_seconds ?? 6,
      description: setting?.description || '',
      footer_text: setting?.footer_text || '',
      contact_email: setting?.contact_email || '',
      contact_phone: setting?.contact_phone || '',
      address: setting?.address || '',
      logo: undefined,
      favicon: undefined,
      hero_image: undefined,
    })
    fillExternalLinks(setting?.external_links)
    Object.assign(contactForm, {
      title: contact?.title || '',
      content: contact?.content || '',
      email: contact?.email || setting?.contact_email || '',
      phone: contact?.phone || setting?.contact_phone || '',
      address: contact?.address || setting?.address || '',
      map_url: contact?.map_url || '',
    })
  }

  function fillExternalLinks(links?: SiteSetting['external_links']) {
    const nextLinks = links || []
    externalLinks.splice(0, externalLinks.length, ...nextLinks.slice(0, 5).map((link) => ({ label: link.label || '', url: link.url || '' })))
    while (externalLinks.length < 3) externalLinks.push({ label: '', url: '' })
  }

  function applyExternalLinks() {
    siteForm.external_links = externalLinks
      .map((link) => ({ label: link.label.trim(), url: link.url.trim() }))
      .filter((link) => link.label && link.url)
  }

  function pickFields(source: CmsForm, fields: string[]) {
    return Object.fromEntries(fields.map((field) => [field, source[field]]))
  }

  async function saveHome() {
    siteForm.contact_email = contactForm.email || siteForm.contact_email || ''
    contactForm.phone = ''
    contactForm.address = siteForm.address || ''
    contactForm.map_url = ''
    const homePayload = pickFields(siteForm, [
      'site_name', 'site_subtitle', 'hero_subtitle', 'banner_interval_seconds', 'description', 'contact_email',
    ])
    const contactPayload = pickFields(contactForm, ['title', 'content', 'email', 'phone', 'address', 'map_url'])
    await save((onUploadProgress) => Promise.all([
      editingContactId.value
        ? cmsApi.updateContactInfo(editingContactId.value, contactPayload, onUploadProgress)
        : cmsApi.createContactInfo(contactPayload, onUploadProgress),
      editingSiteId.value
        ? cmsApi.updateSiteSetting(editingSiteId.value, homePayload, onUploadProgress)
        : cmsApi.createSiteSetting(homePayload, onUploadProgress),
    ]))
  }

  async function saveFooter() {
    applyExternalLinks()
    const footerPayload = pickFields(siteForm, [
      'logo', 'favicon', 'hero_image', 'footer_text', 'address', 'external_links',
    ])
    await save((onUploadProgress) => editingSiteId.value
      ? cmsApi.updateSiteSetting(editingSiteId.value, footerPayload, onUploadProgress)
      : cmsApi.createSiteSetting(footerPayload, onUploadProgress))
  }

  return {
    siteForm, contactForm, externalLinks,
    logo, favicon, heroImage, logoSize, faviconSize, heroImageSize,
    saving, progress, fill, saveHome, saveFooter,
  }
}
