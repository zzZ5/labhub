<template>
  <section class="editor-single">
    <article class="card form-panel site-form-panel">
      <div class="form-heading">
        <div>
          <span>页脚设置</span>
          <h2>网站标识与页脚内容</h2>
          <p>维护课题组网站的标识图片、底部地址和相关链接。</p>
        </div>
      </div>
      <el-form label-position="top">
        <div class="form-section">
          <div class="subsection-heading">
            <strong>网站标识</strong>
            <span>用于导航栏、浏览器图标和没有轮播图时的默认横幅。</span>
          </div>
          <div class="form-two-col">
            <el-form-item label="Logo">
              <ImageCropField v-model="siteForm.logo" :disabled="saving" :existing-url="logo" :aspect-ratio="1" :output-width="1000" :output-height="1000" :max-size-mb="5" preview-shape="circle" hint="按正方形裁剪，支持透明背景" />
            </el-form-item>
            <el-form-item label="网站图标">
              <ImageCropField v-model="siteForm.favicon" :disabled="saving" :existing-url="favicon" :aspect-ratio="1" :output-width="512" :output-height="512" :max-size-mb="2" preview-shape="circle" hint="按正方形裁剪，用于浏览器图标" />
            </el-form-item>
          </div>
          <el-form-item label="默认横幅图">
            <ImageCropField v-model="siteForm.hero_image" :disabled="saving" :existing-url="heroImage" :aspect-ratio="12 / 5" :output-width="1920" :output-height="800" :max-size-mb="20" hint="没有轮播横幅时首页使用此图" />
          </el-form-item>
        </div>
        <div class="form-section">
          <div class="subsection-heading"><strong>页脚信息</strong><span>用于公开网站底部展示。</span></div>
          <el-form-item label="地址"><el-input v-model="siteForm.address" /></el-form-item>
        </div>
        <div class="external-link-editor">
          <div class="subsection-heading">
            <strong>相关链接</strong>
            <span>用于网站底部跳转入口，可放学校、学院或相关平台链接。</span>
          </div>
          <div v-for="(link, index) in externalLinks" :key="index" class="form-two-col">
            <el-form-item :label="`链接 ${index + 1} 名称`"><el-input v-model="link.label" placeholder="如：中国农业大学" /></el-form-item>
            <el-form-item :label="`链接 ${index + 1} 地址`"><el-input v-model="link.url" placeholder="https://..." /></el-form-item>
          </div>
        </div>
      </el-form>
      <CmsFormActions :saving="saving" :progress="progress" @save="$emit('save')" />
    </article>
  </section>
</template>

<script setup lang="ts">
import CmsFormActions from './CmsFormActions.vue'
import ImageCropField from '../../../components/ImageCropField.vue'

defineProps<{
  siteForm: Record<string, any>
  externalLinks: Array<{ label: string; url: string }>
  logo: string
  favicon: string
  heroImage: string
  saving: boolean
  progress: number
  displayFileLabel: (value: string) => string
}>()

defineEmits<{ save: [] }>()
</script>
