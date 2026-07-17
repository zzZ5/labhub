<template>
  <section class="editor-grid" :class="{ 'mobile-editor-open': mobileEditorOpen }">
    <CmsContentList title="首页横幅" action-label="新增横幅" :items="rows" :active-key="editingId || ''" @create="createBanner" @edit="openBanner" />
    <article class="card form-panel">
      <CmsMobileEditorBack @back="mobileEditorOpen = false" />
      <div class="form-heading">
        <div>
          <span>{{ editingId ? '正在编辑' : '新增内容' }}</span>
          <h2>{{ form.title || '首页横幅' }}</h2>
          <p>标题和副标题会显示在对应图片上；留空时首页使用站点名称和副标题。</p>
        </div>
      </div>
      <div v-if="defaultHero" class="legacy-banner-note">
        <img :src="defaultHero" alt="默认横幅预览" />
        <div>
          <strong>默认横幅</strong>
          <span v-if="siteName">{{ siteName }}</span>
          <small v-if="siteSubtitle">{{ siteSubtitle }}</small>
          <small>{{ displayFileLabel(defaultHero) }}</small>
          <small>没有轮播横幅时首页使用此图；新增横幅后优先展示列表中的横幅。</small>
        </div>
      </div>
      <el-form label-position="top">
        <div class="form-section-label"><strong>文字内容</strong><span>显示在横幅安全区域内</span></div>
        <el-form-item label="标题"><el-input v-model="form.title" /></el-form-item>
        <el-form-item label="副标题"><el-input v-model="form.subtitle" type="textarea" :rows="2" /></el-form-item>
        <div class="form-section-label"><strong>横幅图片</strong><span>裁剪并核对桌面与手机显示效果</span></div>
        <el-form-item label="横幅图片">
          <ImageCropField v-model="form.image" :disabled="saving" :existing-url="currentImage" :existing-size="currentImageSize" :aspect-ratio="12 / 5" :output-width="1920" :output-height="800" :max-size-mb="20" hint="按首页横幅比例裁剪，主体尽量居中" @preview="bannerPreview = $event" />
        </el-form-item>
        <div v-if="bannerPreview || currentImage" class="banner-preview-section">
          <div class="banner-preview-heading">
            <div><strong>首页显示预览</strong><span>白色虚线区域为标题安全区</span></div>
            <small>1920 × 800 px · 排序 {{ form.sort_order }}</small>
          </div>
          <div class="banner-preview-grid">
            <figure>
              <div class="banner-preview desktop-preview">
                <img :src="bannerPreview || currentImage" alt="桌面端横幅预览" />
                <div class="banner-safe-area"><strong>{{ form.title || siteName }}</strong><span>{{ form.subtitle || siteSubtitle }}</span></div>
              </div>
              <figcaption>桌面端</figcaption>
            </figure>
            <figure>
              <div class="banner-preview mobile-preview">
                <img :src="bannerPreview || currentImage" alt="手机端横幅预览" />
                <div class="banner-safe-area"><strong>{{ form.title || siteName }}</strong><span>{{ form.subtitle || siteSubtitle }}</span></div>
              </div>
              <figcaption>手机端</figcaption>
            </figure>
          </div>
        </div>
        <div class="form-section-label"><strong>展示设置</strong><span>跳转链接、顺序和启用状态</span></div>
        <el-form-item label="跳转链接"><el-input v-model="form.link" placeholder="可选，https://..." /></el-form-item>
        <div class="form-two-col">
          <el-form-item label="排序"><el-input-number v-model="form.sort_order" :min="0" /></el-form-item>
          <el-form-item label="启用"><el-switch v-model="form.is_active" /></el-form-item>
        </div>
      </el-form>
      <CmsFormActions :saving="saving" :progress="progress" :deletable="Boolean(editingId)" @save="saveBanner" @delete="deleteBanner" />
    </article>
  </section>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'

import { cmsApi } from '../../../api/cms'
import type { HomeBanner } from '../../../api/publicPortal'
import CmsContentList from './CmsContentList.vue'
import CmsFormActions from './CmsFormActions.vue'
import CmsMobileEditorBack from './CmsMobileEditorBack.vue'
import ImageCropField from '../../../components/ImageCropField.vue'
import type { CmsListRow } from '../composables/useCmsContentData'
import { useCmsEditorMutation } from '../composables/useCmsEditorMutation'

defineProps<{
  rows: CmsListRow<HomeBanner>[]
  siteName: string
  siteSubtitle: string
  defaultHero: string
  displayFileLabel: (value: string) => string
}>()

const emit = defineEmits<{ changed: [] }>()
const mobileEditorOpen = ref(false)
const editingId = ref<number | null>(null)
const currentImage = ref('')
const currentImageSize = ref(0)
const bannerPreview = ref('')
type BannerForm = Record<string, unknown> & {
  title: string
  subtitle: string
  image?: File
  link: string
  sort_order: number
  is_active: boolean
}
const form = reactive<BannerForm>({
  title: '',
  subtitle: '',
  image: undefined,
  link: '',
  sort_order: 0,
  is_active: true,
})
const { saving, progress, save, remove } = useCmsEditorMutation(async () => emit('changed'))

function resetBanner() {
  editingId.value = null
  currentImage.value = ''
  currentImageSize.value = 0
  bannerPreview.value = ''
  Object.assign(form, { title: '', subtitle: '', image: undefined, link: '', sort_order: 0, is_active: true })
}

function createBanner() {
  resetBanner()
  mobileEditorOpen.value = true
}

function openBanner(item: HomeBanner) {
  editBanner(item)
  mobileEditorOpen.value = true
}

function editBanner(item: HomeBanner) {
  editingId.value = item.id
  currentImage.value = item.image || ''
  currentImageSize.value = item.image_size || 0
  bannerPreview.value = ''
  Object.assign(form, {
    title: item.title || '',
    subtitle: item.subtitle || '',
    image: undefined,
    link: item.link || '',
    sort_order: item.sort_order || 0,
    is_active: item.is_active !== false,
  })
}

async function saveBanner() {
  if (!currentImage.value && !(form.image instanceof File)) {
    ElMessage.warning('请选择横幅图片。')
    return
  }
  const id = editingId.value
  const succeeded = await save((onUploadProgress) =>
    id ? cmsApi.updateHomeBanner(id, form, onUploadProgress) : cmsApi.createHomeBanner(form, onUploadProgress),
  )
  if (succeeded) {
    resetBanner()
    mobileEditorOpen.value = false
  }
}

async function deleteBanner() {
  const id = editingId.value
  if (!id) return
  const succeeded = await remove('确定删除这张首页横幅吗？', () => cmsApi.deleteHomeBanner(id))
  if (succeeded) {
    resetBanner()
    mobileEditorOpen.value = false
  }
}
</script>

<style scoped>
.banner-preview-section {
  margin-bottom: 16px;
  border: 1px solid var(--color-line);
  border-radius: var(--radius-md);
  padding: 14px;
  background: var(--color-panel);
}

.banner-preview-heading {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 10px;
}

.banner-preview-heading div,
.banner-preview-heading strong,
.banner-preview-heading span {
  display: block;
}

.banner-preview-heading strong {
  color: var(--color-deep-green);
  font-size: 14px;
}

.banner-preview-heading span,
.banner-preview-heading small,
.banner-preview-grid figcaption {
  color: var(--color-muted);
  font-size: 12px;
}

.banner-preview-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.7fr) minmax(150px, .7fr);
  align-items: end;
  gap: 12px;
}

.banner-preview-grid figure {
  min-width: 0;
  margin: 0;
}

.banner-preview {
  position: relative;
  overflow: hidden;
  border-radius: var(--radius-sm);
  background: var(--color-panel-strong);
}

.desktop-preview {
  aspect-ratio: 12 / 5;
}

.mobile-preview {
  aspect-ratio: 3 / 2;
}

.banner-preview img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
}

.banner-safe-area {
  position: absolute;
  right: 8%;
  bottom: 10%;
  left: 8%;
  display: grid;
  max-width: 52%;
  gap: 3px;
  border: 1px dashed rgba(255, 255, 255, .8);
  padding: 7px 9px;
  color: #fff;
  text-shadow: 0 1px 5px rgba(17, 31, 23, .55);
}

.banner-safe-area strong,
.banner-safe-area span {
  display: -webkit-box;
  overflow: hidden;
  -webkit-box-orient: vertical;
}

.banner-safe-area strong {
  font-size: 12px;
  -webkit-line-clamp: 1;
}

.banner-safe-area span {
  font-size: 9px;
  -webkit-line-clamp: 2;
}

.banner-preview-grid figcaption {
  margin-top: 5px;
}

@media (max-width: 720px) {
  .banner-preview-heading {
    display: grid;
    align-items: start;
  }

  .banner-preview-grid {
    grid-template-columns: 1fr;
  }

  .mobile-preview {
    aspect-ratio: 16 / 10;
  }
}
</style>
