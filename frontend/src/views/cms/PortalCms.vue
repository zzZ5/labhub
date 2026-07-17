<template>
  <InternalLayout title="门户内容管理">
    <section class="cms-page">
      <InternalPageHeader class="cms-heading">
        <p>维护官网首页、横幅、研究方向、团队、新闻和科研成果。</p>
        <template #summary><div class="cms-stat-strip">
            <span v-for="item in cmsOverview" :key="item.label">{{ item.label }} {{ item.value }}</span>
        </div></template>
        <template #actions>
          <RouterLink class="preview-link" to="/">预览官网</RouterLink>
        </template>
      </InternalPageHeader>

      <LoadErrorNotice v-if="cmsLoadError" :description="cmsLoadError" :retrying="cmsLoading" @retry="loadAll" />

      <label class="cms-mobile-nav">
        <span>内容栏目</span>
        <select v-model="activeTab">
          <option v-for="item in cmsSections" :key="item.value" :value="item.value">{{ item.label }}</option>
        </select>
      </label>

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
import InternalPageHeader from '../../components/InternalPageHeader.vue'
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
  cmsOverview,
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

.cms-heading {
  align-items: center;
  box-shadow: none;
}

.cms-heading > p {
  margin: 0;
  color: var(--color-muted);
  font-size: 14px;
}

.heading-actions {
  display: flex;
  align-items: center;
  min-width: 0;
  gap: 12px;
}

.cms-stat-strip {
  display: flex;
  flex: 1 1 auto;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 6px;
}

.cms-stat-strip span {
  border: 1px solid var(--color-line);
  border-radius: 999px;
  padding: 5px 9px;
  background: var(--color-panel);
  color: var(--color-muted);
  font-size: 12px;
  font-weight: 600;
}

.preview-link {
  border: 1px solid rgba(0, 135, 60, 0.28);
  border-radius: var(--radius-sm);
  padding: 8px 13px;
  background: #fff;
  color: var(--color-cau-green);
  font-weight: 700;
  white-space: nowrap;
}

.preview-link.subtle {
  border-color: var(--color-border);
  color: var(--color-muted);
}

.cms-tabs {
  min-width: 0;
  max-width: 100%;
  overflow: hidden;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 10px 14px 16px;
  background: #fff;
  box-shadow: none;
}

.cms-tabs .el-tabs__header {
  margin-bottom: 12px;
}

.cms-tabs .el-tabs__nav-wrap::after {
  height: 1px;
  background: var(--color-line);
}

.editor-grid {
  display: grid;
  grid-template-columns: minmax(340px, 400px) minmax(0, 1fr);
  gap: 16px;
  align-items: stretch;
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

.list-panel {
  position: relative;
  display: grid;
  grid-template-rows: auto auto minmax(0, 1fr) auto;
  height: 100%;
  overflow: hidden;
  padding: 18px;
  box-shadow: none;
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
    grid-template-columns: minmax(0, 1.25fr) minmax(360px, 0.75fr);
    gap: 14px;
    align-items: stretch;
  }

  .site-home-form > .form-section {
    min-height: 0;
    margin-bottom: 0;
  }

  .site-home-form > .form-section:first-child {
    grid-row: 1 / span 2;
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

.panel-heading,
.list-toolbar {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 10px;
  border-bottom: 1px solid var(--color-line);
  padding-bottom: 10px;
}

.list-panel .list-toolbar {
  align-items: flex-start;
  border-bottom: 1px solid var(--color-line);
  margin-bottom: 12px;
  min-height: 58px;
  padding-bottom: 12px;
}

.list-panel .list-toolbar strong,
.list-panel .list-toolbar span {
  display: block;
}

.list-panel .list-toolbar > div {
  min-width: 0;
}

.list-panel .list-toolbar strong {
  color: var(--color-deep-green);
  font-size: 19px;
  font-weight: 650;
}

.list-panel .list-toolbar span {
  margin-top: 2px;
  color: var(--color-muted);
  font-size: 12px;
}

.list-panel .list-toolbar .el-button {
  --el-button-size: 32px;
  flex: 0 0 auto;
  min-height: 32px;
  padding: 7px 12px;
  color: #fff !important;
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

.list-panel .list-search {
  width: 100%;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  min-height: 36px;
  margin-bottom: 10px;
  padding: 0 11px;
  background: #fff;
  color: var(--color-text);
  font: inherit;
}

.list-panel .list-search:focus {
  border-color: rgba(0, 135, 60, 0.35);
  outline: none;
  box-shadow: 0 0 0 3px rgba(0, 135, 60, 0.08);
}

.list-panel .content-list-scroll {
  min-width: 0;
  min-height: 0;
  overflow-y: auto;
  overflow-x: hidden;
  padding-right: 6px;
}

.list-panel .content-row {
  display: block;
  width: 100%;
  min-width: 0;
  max-width: 100%;
  box-sizing: border-box;
  border: 1px solid var(--color-line);
  border-radius: 8px;
  margin-bottom: 10px;
  padding: 12px 13px;
  background: #fff;
  cursor: pointer;
  text-align: left;
}

.list-panel .content-row:hover,
.list-panel .content-row.active {
  border-color: rgba(0, 135, 60, 0.14);
  background: var(--color-eco-green);
}

.list-panel .content-row:hover strong,
.list-panel .content-row.active strong {
  color: var(--color-cau-green);
}

.list-panel .content-row strong,
.list-panel .content-row span,
.form-panel small {
  display: block;
}

.list-panel .content-row strong {
  display: block;
  overflow: hidden;
  color: var(--color-text);
  font-size: 14px;
  line-height: 1.45;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.list-panel .content-row span,
.form-panel small,
.empty-list {
  color: var(--color-muted);
  font-size: 13px;
}

.list-panel .content-row span {
  margin-top: 7px;
  overflow: hidden;
  line-height: 1.4;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.list-panel .empty-list {
  border-top: 1px solid var(--color-line);
  padding-top: 16px;
}

.list-panel .list-pager {
  display: grid;
  justify-items: center;
  align-items: center;
  gap: 10px;
  border-top: 1px solid var(--color-line);
  margin-top: 10px;
  padding-top: 10px;
  background: #fff;
}

.list-panel .pager-summary {
  flex: 0 0 auto;
  color: var(--color-text);
  font-size: 13px;
  font-weight: 700;
  white-space: nowrap;
}

.list-panel .pager-controls {
  display: grid;
  grid-template-columns: 68px minmax(54px, 1fr) 68px;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
}

.news-editor-grid {
  grid-template-columns: minmax(290px, 340px) minmax(0, 1fr);
  align-items: start;
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

.list-panel .page-size-select {
  flex: 0 0 108px;
  width: 116px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  min-height: 30px;
  padding: 0 8px;
  background: #fff;
  color: var(--color-text);
  font-size: 13px;
}

.list-panel .list-pager button {
  border: 1px solid rgba(0, 135, 60, 0.22);
  border-radius: var(--radius-sm);
  min-height: 30px;
  padding: 0 10px;
  background: #fff;
  color: var(--color-cau-green);
  cursor: pointer;
  font-size: 13px;
  font-weight: 700;
}

.list-panel .list-pager button:disabled {
  border-color: var(--color-border);
  color: var(--color-muted);
  cursor: not-allowed;
  opacity: 0.6;
}

.list-panel .pager-controls span {
  color: var(--color-muted);
  font-size: 13px;
  font-variant-numeric: tabular-nums;
  text-align: center;
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

.news-content-list .content-list-scroll { gap: 4px; }
.news-content-list .content-row { margin-bottom: 0; padding: 7px 9px; }
.news-content-list .content-row strong { display: block; overflow: hidden; font-size: 13px; line-height: 1.35; text-overflow: ellipsis; white-space: nowrap; }
.news-content-list .content-row span { margin-top: 3px; font-size: 11px; line-height: 1.3; }

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

.list-panel .list-pager .pager-nav {
  display: inline-grid;
  place-items: center;
  width: 68px;
  padding: 0;
  line-height: 1;
  text-align: center;
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

  .cms-heading {
    align-items: center;
  }

  .heading-actions {
    width: 100%;
  }

  .list-panel {
    max-height: none;
  }

  .list-panel .content-list-scroll {
    max-height: 420px;
  }
}

@media (max-width: 720px) {
  .cms-page {
    gap: 10px;
  }

  .cms-heading {
    display: grid;
    gap: 10px;
    padding: 0 0 12px;
  }

  .heading-actions,
  .cms-stat-strip {
    display: grid;
    grid-template-columns: 1fr;
    width: 100%;
    justify-content: stretch;
  }

  .cms-stat-strip {
    display: none !important;
  }

  .cms-stat-strip span,
  .preview-link {
    width: 100%;
    text-align: center;
  }

  .cms-tabs {
    width: 100%;
    border-radius: var(--radius-sm);
    padding: 6px;
  }

  .cms-mobile-nav {
    display: grid;
    grid-template-columns: auto minmax(0, 1fr);
    align-items: center;
    gap: 10px;
    border: 1px solid var(--color-border);
    border-radius: var(--radius-sm);
    padding: 9px 10px;
    background: #fff;
  }

  .cms-mobile-nav span { color: var(--color-deep-green); font-size: 13px; font-weight: 650; }
  .cms-mobile-nav select { width: 100%; min-height: 38px; border: 1px solid var(--color-border); border-radius: var(--radius-sm); padding: 0 10px; background: #fff; color: var(--color-text); font: inherit; }

  .cms-tabs .el-tabs__header {
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

  .list-panel {
    display: block;
    height: auto;
    overflow: visible;
  }

  .list-panel .list-toolbar {
    display: grid;
    grid-template-columns: 1fr;
    gap: 9px;
    min-height: 0;
    margin-bottom: 10px;
    padding-bottom: 10px;
  }

  .list-panel .list-toolbar strong {
    font-size: 17px;
  }

  .list-panel .list-toolbar .el-button {
    width: 100%;
    min-height: 36px;
  }

  .list-panel .list-search {
    min-height: 38px;
    margin-bottom: 10px;
  }

  .list-panel .content-list-scroll {
    max-height: 48vh;
    overflow-y: auto;
    padding-right: 2px;
  }

  .list-panel .content-row {
    margin-bottom: 8px;
    padding: 10px 11px;
  }

  .list-panel .content-row strong,
  .list-panel .content-row span {
    white-space: normal;
  }

  .list-panel .content-row strong {
    display: -webkit-box;
    overflow: hidden;
    line-height: 1.45;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 2;
  }

  .list-panel .content-row span {
    display: -webkit-box;
    margin-top: 5px;
    overflow: hidden;
    line-height: 1.45;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 2;
  }

  .list-panel .list-pager {
    gap: 8px;
  }

  .list-panel .list-pager button {
    min-height: 34px;
    padding: 0 8px;
  }

  .list-panel .list-pager span {
    align-self: center;
    white-space: nowrap;
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
