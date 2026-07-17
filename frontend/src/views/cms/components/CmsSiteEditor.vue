<template>
  <section class="editor-single">
    <article class="card form-panel site-form-panel">
      <div class="form-heading">
        <div>
          <span>站点首页</span>
          <h2>{{ siteForm.site_name || '中农雨磷' }}</h2>
          <p>维护首页基础文案、课题组简介和加入我们；网站标识与页脚内容请到“页脚设置”维护。</p>
        </div>
      </div>
      <el-form class="site-home-form" label-position="top">
        <div class="form-section">
          <div class="subsection-heading">
            <strong>基础信息</strong>
            <span>用于导航栏、页脚和没有单独标题的默认横幅。</span>
          </div>
          <div class="form-two-col">
            <el-form-item label="实验室名称"><el-input v-model="siteForm.site_name" /></el-form-item>
            <el-form-item label="归属单位"><el-input v-model="siteForm.site_subtitle" /></el-form-item>
          </div>
          <el-form-item label="横幅副标题"><el-input v-model="siteForm.hero_subtitle" /></el-form-item>
          <el-form-item label="横幅切换间隔">
            <el-input-number v-model="siteForm.banner_interval_seconds" :min="3" :max="30" />
            <small>单位：秒。仅首页横幅有多张图片时生效。</small>
          </el-form-item>
        </div>
        <div class="form-section">
          <div class="subsection-heading">
            <strong>课题组简介</strong>
            <span>这里会直接显示在首页“课题组简介”模块中。</span>
          </div>
          <el-form-item label="简介正文"><el-input v-model="siteForm.description" type="textarea" :rows="4" /></el-form-item>
        </div>
        <div class="form-section">
          <div class="subsection-heading">
            <strong>加入我们</strong>
            <span>用于首页底部“加入我们”模块。</span>
          </div>
          <el-form-item label="说明"><el-input v-model="contactForm.content" type="textarea" :rows="3" /></el-form-item>
          <el-form-item label="联系邮箱"><el-input v-model="contactForm.email" /></el-form-item>
        </div>
      </el-form>
      <CmsFormActions :saving="saving" :progress="progress" @save="$emit('save')" />
    </article>
  </section>
</template>

<script setup lang="ts">
import CmsFormActions from './CmsFormActions.vue'

defineProps<{
  siteForm: Record<string, any>
  contactForm: Record<string, any>
  saving: boolean
  progress: number
}>()

defineEmits<{ save: [] }>()
</script>
