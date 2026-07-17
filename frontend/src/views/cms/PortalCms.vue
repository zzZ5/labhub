<template>
  <InternalLayout title="门户内容管理">
    <section class="cms-page">
      <LoadErrorNotice v-if="cmsLoadError" :description="cmsLoadError" :retrying="cmsLoading" @retry="loadAll" />

      <div class="cms-mobile-nav">
        <label for="cms-section-select">内容栏目</label>
        <select id="cms-section-select" v-model="activeTab">
          <option v-for="item in cmsSections" :key="item.value" :value="item.value">{{ item.label }}</option>
        </select>
      </div>

      <el-tabs v-model="activeTab" v-loading="cmsLoading" class="cms-tabs">
        <el-tab-pane label="站点首页" name="site">
          <CmsSiteEditor :site-form="siteForm" :contact-form="contactForm" :saving="siteSaving" :progress="siteProgress" @save="saveHome" />
        </el-tab-pane>

        <el-tab-pane label="页脚设置" name="footer">
          <CmsFooterEditor
            :site-form="siteForm"
            :external-links="externalLinks"
            :logo="siteLogo"
            :favicon="siteFavicon"
            :hero-image="siteHeroImage"
            :logo-size="siteLogoSize"
            :favicon-size="siteFaviconSize"
            :hero-image-size="siteHeroImageSize"
            :saving="siteSaving"
            :progress="siteProgress"
            :display-file-label="displayFileLabel"
            @save="saveFooter"
          />
        </el-tab-pane>

        <el-tab-pane label="首页横幅" name="banners">
          <CmsBannerEditor
            :rows="bannerRows"
            :site-name="String(siteForm.site_name || '')"
            :site-subtitle="String(siteForm.hero_subtitle || '')"
            :default-hero="siteHeroImage"
            :display-file-label="displayFileLabel"
            @changed="loadAll"
          />
        </el-tab-pane>

        <el-tab-pane label="研究方向" name="research">
          <CmsResearchEditor :rows="researchRows" @changed="loadAll" />
        </el-tab-pane>

        <el-tab-pane label="团队成员" name="members">
          <CmsMemberEditor
            :rows="memberRows" :importing="importingKind === 'members'" :import-progress="importProgress"
            @import="importCmsFile($event, 'members')" @changed="loadAll"
          />
        </el-tab-pane>

        <el-tab-pane label="新闻活动" name="news">
          <CmsNewsEditor
            :rows="newsRows" :categories="newsCategories" :display-file-label="displayFileLabel" @changed="loadAll"
          />
        </el-tab-pane>

        <el-tab-pane label="论文成果" name="publications">
          <CmsPublicationEditor
            :rows="publicationRows" :importing="importingKind === 'publications'" :import-progress="importProgress"
            :display-file-label="displayFileLabel" @import="importCmsFile($event, 'publications')" @changed="loadAll"
          />
        </el-tab-pane>

        <el-tab-pane label="科研项目" name="projects">
          <CmsProjectEditor
            :rows="projectRows" :importing="importingKind === 'projects'" :import-progress="importProgress"
            @import="importCmsFile($event, 'projects')" @changed="loadAll"
          />
        </el-tab-pane>

        <el-tab-pane label="专利成果" name="patents">
          <CmsPatentEditor
            :rows="patentRows" :importing="importingKind === 'patents'" :import-progress="importProgress"
            :display-file-label="displayFileLabel" @import="importCmsFile($event, 'patents')" @changed="loadAll"
          />
        </el-tab-pane>

        <el-tab-pane label="获奖成果" name="awards">
          <CmsAwardEditor
            :rows="awardRows" :importing="importingKind === 'awards'" :import-progress="importProgress"
            :display-file-label="displayFileLabel" @import="importCmsFile($event, 'awards')" @changed="loadAll"
          />
        </el-tab-pane>


      </el-tabs>
    </section>
  </InternalLayout>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import InternalLayout from '../../layouts/InternalLayout.vue'
import LoadErrorNotice from '../../components/LoadErrorNotice.vue'
import CmsBannerEditor from './components/CmsBannerEditor.vue'
import CmsAwardEditor from './components/CmsAwardEditor.vue'
import CmsFooterEditor from './components/CmsFooterEditor.vue'
import CmsMemberEditor from './components/CmsMemberEditor.vue'
import CmsNewsEditor from './components/CmsNewsEditor.vue'
import CmsPatentEditor from './components/CmsPatentEditor.vue'
import CmsProjectEditor from './components/CmsProjectEditor.vue'
import CmsPublicationEditor from './components/CmsPublicationEditor.vue'
import CmsResearchEditor from './components/CmsResearchEditor.vue'
import CmsSiteEditor from './components/CmsSiteEditor.vue'
import { useCmsContentData } from './composables/useCmsContentData'
import { useCmsImport } from './composables/useCmsImport'
import { useCmsSiteSettings } from './composables/useCmsSiteSettings'

const activeTab = ref('site')
const cmsSections = [
  { value: 'site', label: '站点首页' },
  { value: 'footer', label: '页脚设置' },
  { value: 'banners', label: '首页横幅' },
  { value: 'research', label: '研究方向' },
  { value: 'members', label: '团队成员' },
  { value: 'news', label: '新闻活动' },
  { value: 'publications', label: '论文成果' },
  { value: 'projects', label: '科研项目' },
  { value: 'patents', label: '专利成果' },
  { value: 'awards', label: '获奖成果' },
]
const {
  siteForm, contactForm, externalLinks,
  logo: siteLogo, favicon: siteFavicon, heroImage: siteHeroImage,
  logoSize: siteLogoSize, faviconSize: siteFaviconSize, heroImageSize: siteHeroImageSize,
  saving: siteSaving, progress: siteProgress,
  fill: fillSiteForms, saveHome, saveFooter,
} = useCmsSiteSettings(() => loadAll())
const {
  loading: cmsLoading,
  loadError: cmsLoadError,
  newsCategories,
  researchRows,
  bannerRows,
  memberRows,
  newsRows,
  publicationRows,
  projectRows,
  patentRows,
  awardRows,
  displayFileLabel,
  loadAll,
} = useCmsContentData(fillSiteForms)
const { importProgress, importingKind, importFile: importCmsFile } = useCmsImport(loadAll)

onMounted(loadAll)
</script>

<style>
.cms-page {
  display: grid;
  gap: 12px;
  min-width: 0;
  max-width: 100%;
}

.cms-tabs {
  min-width: 0;
  max-width: 100%;
  overflow: visible;
  border: 0;
  border-radius: 0;
  padding: 0;
  background: transparent;
  box-shadow: none;
}

.cms-tabs .el-tabs__header {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  margin-bottom: 14px;
  padding: 0 14px;
  background: #fff;
}

.cms-tabs .el-tabs__nav-wrap::after {
  height: 1px;
  background: var(--color-line);
}

.editor-grid {
  display: grid;
  grid-template-columns: minmax(330px, 380px) minmax(0, 1fr);
  gap: 14px;
  align-items: start;
}

.editor-single {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 16px;
  align-items: start;
}

.list-panel,
.form-panel {
  border-radius: var(--radius-md);
}

.form-panel {
  min-width: 0;
  max-width: 100%;
  padding: 18px 20px;
  box-shadow: none;
}

.cms-mobile-nav { display: none; }

.site-form-panel {
  min-height: 100%;
}

@media (min-width: 1280px) {
  .site-home-form {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 14px;
    align-items: start;
  }

  .site-home-form > .form-section {
    min-height: 0;
    margin-bottom: 0;
  }

  .site-home-form > .form-section:first-child {
    grid-column: 1 / -1;
  }
}

.form-section {
  min-width: 0;
  max-width: 100%;
  border: 1px solid var(--color-line);
  border-radius: var(--radius-md);
  margin-bottom: 14px;
  padding: 14px;
  background: rgba(251, 252, 251, 0.72);
}

.list-panel:hover,
.form-panel:hover {
  transform: none;
}

.panel-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 10px;
  border-bottom: 1px solid var(--color-line);
  padding-bottom: 10px;
}

.cms-page .el-button--primary,
.cms-page .el-button--primary span {
  color: #fff !important;
}

.panel-heading h2 {
  margin: 0;
  color: var(--color-deep-green);
  font-size: 19px;
  font-weight: 650;
}

.form-panel small {
  display: block;
}

.form-panel small {
  color: var(--color-muted);
  font-size: 13px;
}

.news-form-panel {
  min-width: 0;
}

.news-body-field .el-form-item__content {
  display: block;
}

.news-body-field .rich-editor {
  width: 100%;
}

.news-assets-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  margin: 2px 0 14px;
}

.news-asset-field {
  display: grid;
  align-content: start;
  gap: 7px;
  min-width: 0;
  border: 1px solid var(--color-line);
  border-radius: var(--radius-sm);
  padding: 12px;
  background: #fafcfb;
}

.news-asset-field strong {
  color: var(--color-deep-green);
  font-size: 14px;
}

.news-asset-field small {
  overflow: hidden;
  color: var(--color-muted);
  text-overflow: ellipsis;
  white-space: nowrap;
}

.news-save-progress {
  margin-top: 0;
}

.member-avatar-field {
  display: grid;
  grid-template-columns: 104px minmax(0, 1fr);
  align-items: center;
  gap: 16px;
  width: 100%;
  border: 1px solid var(--color-line);
  border-radius: var(--radius-sm);
  padding: 12px;
  background: #fafcfb;
}

.member-avatar-preview {
  display: grid;
  place-items: center;
  width: 104px;
  aspect-ratio: 4 / 5;
  overflow: hidden;
  border: 1px solid rgba(31, 61, 43, 0.12);
  border-radius: 7px;
  background: var(--color-eco-green);
  color: var(--color-deep-green);
  font-size: 22px;
  font-weight: 650;
}

.member-avatar-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center top;
}

.member-avatar-control {
  display: grid;
  min-width: 0;
  gap: 7px;
}

.member-avatar-control small {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.editor-hint {
  border: 1px solid rgba(0, 135, 60, 0.12);
  border-radius: var(--radius-sm);
  margin: -4px 0 18px;
  padding: 12px 14px;
  background: var(--color-eco-green);
}

.editor-hint strong {
  color: var(--color-deep-green);
  font-size: 14px;
}

.editor-hint p {
  margin: 4px 0 0;
  color: var(--color-muted);
  font-size: 13px;
  line-height: 1.65;
}

.import-strip {
  grid-column: 1 / -1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  border: 1px solid rgba(0, 135, 60, 0.12);
  border-radius: var(--radius-sm);
  padding: 10px 12px;
  background: var(--color-panel);
}

.cms-import-block {
  grid-column: 1 / -1;
}

.import-progress {
  grid-column: 1 / -1;
  margin: -4px 0 0;
}

.import-strip span {
  min-width: 0;
  overflow: hidden;
  color: var(--color-muted);
  font-size: 12px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.import-strip input {
  display: none;
}

.import-strip a,
.import-strip button {
  flex: 0 0 auto;
  border: 1px solid rgba(0, 135, 60, 0.22);
  border-radius: 999px;
  padding: 5px 12px;
  background: #fff;
  color: var(--color-primary);
  cursor: pointer;
  font-size: 12px;
  font-weight: 700;
  line-height: 1.4;
  text-decoration: none;
  white-space: nowrap;
}

.import-strip a:hover,
.import-strip button:hover {
  border-color: var(--color-primary);
  background: rgba(0, 135, 60, 0.06);
}

.news-gallery-manager {
  display: grid;
  gap: 12px;
  border: 1px solid var(--color-line);
  border-radius: var(--radius-md);
  margin: 0 0 18px;
  padding: 14px;
  background: var(--color-panel);
}

.gallery-heading {
  display: flex;
  justify-content: space-between;
  gap: 14px;
}

.gallery-heading strong {
  color: var(--color-deep-green);
}

.gallery-heading p {
  margin: 3px 0 0;
  color: var(--color-muted);
  font-size: 13px;
  line-height: 1.6;
}

.gallery-heading span {
  flex: 0 0 auto;
  color: var(--color-cau-green);
  font-size: 13px;
  font-weight: 700;
}

.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 10px;
}

.gallery-grid article {
  overflow: hidden;
  border: 1px solid var(--color-line);
  border-radius: var(--radius-sm);
  background: #fff;
}

.gallery-grid img {
  display: block;
  width: 100%;
  aspect-ratio: 4 / 3;
  object-fit: cover;
}

.gallery-grid article > div {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 8px 9px;
}

.gallery-grid article span {
  min-width: 0;
  overflow: hidden;
  color: var(--color-muted);
  font-size: 12px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.gallery-grid article button {
  border: 0;
  background: transparent;
  color: #9f312f;
  cursor: pointer;
  font-size: 12px;
  font-weight: 700;
}

.gallery-upload {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(0, 1fr) auto auto;
  gap: 10px;
  align-items: center;
}

.form-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
  border-bottom: 1px solid var(--color-line);
  margin-bottom: 14px;
  padding-bottom: 12px;
}

.form-heading span {
  color: var(--color-cau-green);
  font-size: 13px;
  font-weight: 700;
}

.form-heading h2 {
  margin: 4px 0 0;
  color: var(--color-deep-green);
  font-size: 20px;
  font-weight: 650;
  line-height: 1.3;
}

.form-heading p {
  max-width: 620px;
  margin: 8px 0 0;
  color: var(--color-muted);
  font-size: 13px;
  line-height: 1.6;
}

.legacy-banner-note {
  display: grid;
  grid-template-columns: 132px minmax(0, 1fr);
  gap: 12px;
  border: 1px solid rgba(0, 135, 60, 0.16);
  border-radius: var(--radius-md);
  margin-bottom: 16px;
  padding: 12px;
  background: rgba(234, 245, 238, 0.62);
}

.legacy-banner-note img {
  width: 132px;
  height: 78px;
  border-radius: 8px;
  background: var(--color-line);
  object-fit: cover;
}

.legacy-banner-note div {
  display: grid;
  align-content: center;
  gap: 3px;
  min-width: 0;
}

.legacy-banner-note strong {
  color: var(--color-deep-green);
  font-size: 14px;
  font-weight: 650;
}

.legacy-banner-note span,
.legacy-banner-note small {
  overflow: hidden;
  color: var(--color-muted);
  font-size: 13px;
  line-height: 1.55;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.form-panel .el-form-item {
  margin-bottom: 14px;
}

.form-panel .el-textarea__inner {
  line-height: 1.7;
}

.form-two-col {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.form-three-col {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.secondary-inline-action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(0, 135, 60, 0.24);
  border-radius: var(--radius-xs);
  margin: -4px 0 14px;
  padding: 6px 12px;
  background: #fff;
  color: var(--color-primary);
  cursor: pointer;
  font-size: 13px;
  font-weight: 700;
}

.secondary-inline-action:hover {
  border-color: var(--color-primary);
  background: rgba(0, 135, 60, 0.06);
}

.citation-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: -4px 0 12px;
}

.citation-actions .secondary-inline-action {
  margin: 0;
}

.citation-actions span {
  color: var(--color-muted);
  font-size: 13px;
}

.citation-preview {
  border: 1px solid rgba(0, 135, 60, 0.16);
  border-radius: var(--radius-md);
  margin-bottom: 16px;
  padding: 12px 14px;
  background: rgba(234, 245, 238, 0.52);
}

.citation-preview__title {
  margin-bottom: 10px;
  color: var(--color-deep-green);
  font-size: 14px;
  font-weight: 700;
}

.citation-preview dl {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px 16px;
  margin: 0;
}

.citation-preview div {
  min-width: 0;
}

.citation-preview dt {
  margin-bottom: 2px;
  color: var(--color-muted);
  font-size: 12px;
}

.citation-preview dd {
  margin: 0;
  overflow-wrap: anywhere;
  color: var(--color-text);
  font-size: 13px;
  line-height: 1.55;
}

.external-link-editor {
  display: grid;
  gap: 8px;
  border: 1px solid var(--color-line);
  border-radius: var(--radius-md);
  margin-bottom: 14px;
  padding: 14px;
  background: rgba(245, 247, 246, 0.72);
}

.subsection-heading {
  display: grid;
  gap: 4px;
  margin-bottom: 2px;
}

.subsection-heading strong {
  color: var(--color-deep-green);
  font-size: 15px;
}

.subsection-heading span {
  color: var(--color-muted);
  font-size: 13px;
  line-height: 1.5;
}

.file-input {
  width: 100%;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: 10px 11px;
  background: #fff;
}

.upload-progress {
  display: grid;
  gap: 6px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  margin-bottom: 14px;
  padding: 12px;
  background: var(--color-soft-gray);
}

.upload-progress span {
  color: var(--color-muted);
  font-size: 13px;
}

.form-actions {
  position: sticky;
  bottom: 0;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  border-top: 1px solid var(--color-line);
  margin: 18px -20px -18px;
  padding: 12px 20px;
  background: rgba(251, 252, 251, 0.96);
  backdrop-filter: blur(8px);
}

.inline-upload-progress {
  width: 100%;
  margin-bottom: 2px;
}

@media (max-width: 980px) {
  .editor-grid,
  .editor-single,
  .form-two-col,
  .form-three-col,
  .gallery-upload {
    grid-template-columns: 1fr;
  }

  .news-assets-grid {
    grid-template-columns: 1fr;
  }

  .member-avatar-field {
    grid-template-columns: 84px minmax(0, 1fr);
  }

  .member-avatar-preview {
    width: 84px;
  }

}

@media (max-width: 720px) {
  .cms-page {
    gap: 10px;
  }

  .cms-tabs {
    width: 100%;
    padding: 0;
  }

  .cms-mobile-nav {
    display: grid;
    grid-template-columns: auto minmax(0, 1fr);
    align-items: center;
    gap: 10px;
    border: 1px solid var(--color-border);
    border-radius: var(--radius-sm);
    padding: 8px 10px;
    background: #fff;
  }

  .cms-mobile-nav label { color: var(--color-deep-green); font-size: 13px; font-weight: 650; }
  .cms-mobile-nav select { width: 100%; min-height: 38px; border: 1px solid var(--color-border); border-radius: var(--radius-sm); padding: 0 10px; background: #fff; color: var(--color-text); font: inherit; }

  .cms-tabs .el-tabs__header {
    display: none;
  }

  .editor-grid:not(.mobile-editor-open) > .form-panel {
    display: none;
  }

  .editor-grid.mobile-editor-open > .list-panel {
    display: none;
  }

  .cms-tabs .el-tabs__nav-wrap {
    width: 100%;
    min-width: 0;
    overflow: hidden;
    padding: 0;
  }

  .cms-tabs .el-tabs__nav-prev,
  .cms-tabs .el-tabs__nav-next,
  .cms-tabs .el-tabs__active-bar {
    display: none;
  }

  .cms-tabs .el-tabs__nav-scroll {
    width: 100%;
    min-width: 0;
    overflow-x: auto;
    overflow-y: hidden;
    scrollbar-width: none;
    -webkit-overflow-scrolling: touch;
  }

  .cms-tabs .el-tabs__nav {
    display: flex;
    width: max-content;
    float: none;
    gap: 6px;
    transform: none !important;
    white-space: nowrap;
  }

  .cms-tabs .el-tabs__content,
  .cms-tabs .el-tab-pane,
  .editor-grid,
  .editor-single,
  .list-panel,
  .form-panel,
  .form-section {
    width: 100%;
    min-width: 0;
    max-width: 100%;
  }

  .cms-tabs .el-form,
  .cms-tabs .el-form-item,
  .cms-tabs .el-form-item__content,
  .cms-tabs .el-input,
  .cms-tabs .el-select,
  .cms-tabs .el-input-number,
  .cms-tabs .el-textarea,
  .cms-tabs .el-upload,
  .cms-tabs .el-upload-dragger {
    min-width: 0;
    max-width: 100%;
  }

  .cms-tabs .el-tabs__item {
    justify-content: center;
    width: auto;
    height: 36px;
    border: 1px solid var(--color-line);
    border-radius: var(--radius-sm);
    padding: 0 8px;
    background: var(--color-panel);
    font-size: 13px;
  }

  .cms-tabs .el-tabs__item.is-active {
    border-color: rgba(0, 135, 60, 0.2);
    background: var(--color-eco-green);
  }

  .editor-grid,
  .editor-single {
    gap: 10px;
  }

  .list-panel,
  .form-panel {
    border-radius: var(--radius-sm);
    padding: 12px;
  }

  .import-strip {
    display: grid;
    grid-template-columns: 1fr;
    gap: 8px;
    padding: 10px;
  }

  .import-strip span {
    white-space: normal;
  }

  .import-strip a,
  .import-strip button {
    width: 100%;
    flex: none;
  }

  .form-heading {
    display: grid;
    gap: 8px;
  }

  .form-heading h2 {
    font-size: 18px;
  }

  .citation-actions {
    align-items: flex-start;
    flex-direction: column;
  }

  .citation-preview dl {
    grid-template-columns: 1fr;
  }

  .form-three-col {
    grid-template-columns: 1fr;
    gap: 0;
  }

  .form-actions {
    position: static;
    display: grid;
    grid-template-columns: 1fr;
    margin: 14px 0 0;
    padding: 12px 0 0;
  }

  .form-actions .el-button {
    width: 100%;
    margin: 0;
  }
}
</style>
