<template>
  <InternalLayout title="门户内容管理">
    <section class="cms-page">
      <div class="cms-heading">
        <div>
          <span>门户内容</span>
          <h1>官网内容维护</h1>
        </div>
        <div class="heading-actions">
          <div class="cms-stat-strip">
            <span v-for="item in cmsOverview" :key="item.label">{{ item.label }} {{ item.value }}</span>
          </div>
          <RouterLink class="preview-link" to="/">预览官网</RouterLink>
        </div>
      </div>

      <el-tabs v-model="activeTab" class="cms-tabs">
        <el-tab-pane label="站点首页" name="site">
          <section class="editor-single">
            <article class="card form-panel site-form-panel">
              <div class="form-heading">
                <div>
                  <span>首页基础内容</span>
                  <h2>{{ siteForm.site_name || '站点首页' }}</h2>
                </div>
              </div>
              <el-form label-position="top">
                <div class="form-two-col">
                  <el-form-item label="实验室名称"><el-input v-model="siteForm.site_name" /></el-form-item>
                  <el-form-item label="归属单位"><el-input v-model="siteForm.site_subtitle" /></el-form-item>
                </div>
                <el-form-item label="首页主标题下方短句"><el-input v-model="siteForm.keywords" /></el-form-item>
                <el-form-item label="首页简介"><el-input v-model="siteForm.description" type="textarea" :rows="4" /></el-form-item>
                <el-form-item label="课题组简介模块文字"><el-input v-model="siteForm.footer_text" type="textarea" :rows="4" /></el-form-item>
                <div class="form-two-col">
                  <el-form-item label="联系邮箱"><el-input v-model="siteForm.contact_email" /></el-form-item>
                  <el-form-item label="联系电话"><el-input v-model="siteForm.contact_phone" /></el-form-item>
                </div>
                <el-form-item label="地址"><el-input v-model="siteForm.address" /></el-form-item>
                <el-form-item label="Logo">
                  <input class="file-input" type="file" accept="image/*" @change="setFile($event, siteForm, 'logo')" />
                  <small v-if="editingSiteLogo">当前 Logo：{{ displayFileLabel(editingSiteLogo) }}</small>
                </el-form-item>
                <el-form-item label="网站图标">
                  <input class="file-input" type="file" accept="image/*" @change="setFile($event, siteForm, 'favicon')" />
                  <small v-if="editingSiteFavicon">当前图标：{{ displayFileLabel(editingSiteFavicon) }}</small>
                </el-form-item>
                <el-form-item label="首页横幅图">
                  <input class="file-input" type="file" accept="image/*" @change="setFile($event, siteForm, 'hero_image')" />
                  <small v-if="editingSiteHeroImage">当前横幅：{{ displayFileLabel(editingSiteHeroImage) }}</small>
                </el-form-item>
              </el-form>
              <FormActions :saving="saving" @save="saveSiteSetting" />
            </article>

            <article class="card form-panel site-form-panel">
              <div class="form-heading">
                <div>
                  <span>加入我们 / 联系方式</span>
                  <h2>{{ contactForm.title || '联系我们' }}</h2>
                </div>
              </div>
              <el-form label-position="top">
                <el-form-item label="标题"><el-input v-model="contactForm.title" /></el-form-item>
                <el-form-item label="说明"><el-input v-model="contactForm.content" type="textarea" :rows="4" /></el-form-item>
                <div class="form-two-col">
                  <el-form-item label="邮箱"><el-input v-model="contactForm.email" /></el-form-item>
                  <el-form-item label="电话"><el-input v-model="contactForm.phone" /></el-form-item>
                </div>
                <el-form-item label="地址"><el-input v-model="contactForm.address" /></el-form-item>
                <el-form-item label="地图链接"><el-input v-model="contactForm.map_url" /></el-form-item>
                <div class="external-link-editor">
                  <div class="subsection-heading">
                    <strong>页脚外链</strong>
                    <span>用于公开网站底部跳转入口，可按需改成学校、学院或相关平台链接。</span>
                  </div>
                  <div v-for="(link, index) in externalLinks" :key="index" class="form-two-col">
                    <el-form-item :label="`链接 ${index + 1} 名称`"><el-input v-model="link.label" placeholder="如：中国农业大学" /></el-form-item>
                    <el-form-item :label="`链接 ${index + 1} 地址`"><el-input v-model="link.url" placeholder="https://..." /></el-form-item>
                  </div>
                </div>
              </el-form>
              <FormActions :saving="saving" @save="saveContactSection" />
            </article>
          </section>
        </el-tab-pane>

        <el-tab-pane label="研究方向" name="research">
          <section class="editor-grid">
            <ContentList title="研究方向" action-label="新增方向" :items="researchRows" :active-key="editingResearchSlug" @create="resetResearch" @edit="editResearch" />
            <article class="card form-panel">
              <div class="form-heading">
                <div>
                  <span>{{ editingResearchSlug ? '正在编辑' : '新增内容' }}</span>
                  <h2>{{ researchForm.title || '研究方向' }}</h2>
                </div>
              </div>
              <el-form label-position="top">
                <el-form-item label="标题"><el-input v-model="researchForm.title" /></el-form-item>
                <el-form-item label="摘要"><el-input v-model="researchForm.summary" type="textarea" :rows="3" /></el-form-item>
                <el-form-item label="关键词"><el-input v-model="researchForm.keywords" placeholder="多个关键词用逗号、顿号或空格分隔" /></el-form-item>
                <el-form-item label="详细内容"><el-input v-model="researchForm.content" type="textarea" :rows="5" /></el-form-item>
                <el-form-item label="封面图">
                  <input class="file-input" type="file" accept="image/*" @change="setFile($event, researchForm, 'cover_image')" />
                  <small v-if="editingResearchCover">当前图片：{{ displayFileLabel(editingResearchCover) }}</small>
                </el-form-item>
                <el-form-item label="排序"><el-input-number v-model="researchForm.sort_order" :min="0" /></el-form-item>
              </el-form>
              <FormActions :saving="saving" :deletable="Boolean(editingResearchSlug)" @save="saveResearch" @delete="deleteResearch" />
            </article>
          </section>
        </el-tab-pane>

        <el-tab-pane label="团队成员" name="members">
          <section class="editor-grid">
            <ContentList title="团队成员" action-label="新增成员" :items="memberRows" :active-key="editingMemberId || ''" @create="resetMember" @edit="editMember" />
            <article class="card form-panel">
              <div class="form-heading">
                <div>
                  <span>{{ editingMemberId ? '正在编辑' : '新增内容' }}</span>
                  <h2>{{ memberForm.name || '团队成员' }}</h2>
                </div>
              </div>
              <el-form label-position="top">
                <el-form-item label="姓名"><el-input v-model="memberForm.name" /></el-form-item>
                <div class="form-two-col">
                  <el-form-item label="身份头衔">
                    <el-input v-model="memberForm.role_type" placeholder="如：副教授 / 博士生导师、博士研究生、硕士研究生" />
                  </el-form-item>
                  <el-form-item label="邮箱"><el-input v-model="memberForm.email" /></el-form-item>
                </div>
                <el-form-item label="研究方向"><el-input v-model="memberForm.research_direction" /></el-form-item>
                <el-form-item label="头像">
                  <input class="file-input" type="file" accept="image/*" @change="setFile($event, memberForm, 'avatar')" />
                  <small v-if="editingMemberAvatar">当前头像：{{ displayFileLabel(editingMemberAvatar) }}</small>
                </el-form-item>
                <el-form-item label="简介"><el-input v-model="memberForm.profile" type="textarea" :rows="4" /></el-form-item>
                <el-form-item label="展示排序">
                  <el-input-number v-model="memberForm.sort_order" :min="0" />
                  <small>0 表示不在公开网站展示；大于 0 时按数字从小到大排序。</small>
                </el-form-item>
              </el-form>
              <FormActions :saving="saving" :deletable="Boolean(editingMemberId)" @save="saveMember" @delete="deleteMember" />
            </article>
          </section>
        </el-tab-pane>

        <el-tab-pane label="新闻活动" name="news">
          <section class="editor-grid">
            <ContentList title="新闻活动" action-label="新增新闻" :items="newsRows" :active-key="editingNewsSlug" @create="resetNews" @edit="editNews" />
            <article class="card form-panel">
              <div class="form-heading">
                <div>
                  <span>{{ editingNewsSlug ? '正在编辑' : '新增内容' }}</span>
                  <h2>{{ newsForm.title || '新闻活动' }}</h2>
                </div>
              </div>
              <el-form label-position="top">
                <el-form-item label="标题"><el-input v-model="newsForm.title" /></el-form-item>
                <div class="form-two-col">
                  <el-form-item label="活动日期"><el-date-picker v-model="newsForm.event_date" type="date" value-format="YYYY-MM-DD" /></el-form-item>
                  <el-form-item label="地点"><el-input v-model="newsForm.location" /></el-form-item>
                </div>
                <div class="form-two-col">
                  <el-form-item label="分类">
                    <el-select v-model="newsForm.category_id" clearable placeholder="选择分类">
                      <el-option v-for="category in newsCategories" :key="category.id" :label="category.name" :value="category.id" />
                    </el-select>
                  </el-form-item>
                  <el-form-item label="状态">
                    <el-select v-model="newsForm.status">
                      <el-option label="草稿" value="draft" />
                      <el-option label="发布" value="published" />
                      <el-option label="归档" value="archived" />
                    </el-select>
                  </el-form-item>
                </div>
                <el-form-item label="摘要"><el-input v-model="newsForm.summary" type="textarea" :rows="3" /></el-form-item>
                <el-form-item label="Word 稿件">
                  <input :key="newsFileInputKey" class="file-input" type="file" accept=".docx" @change="setFile($event, newsForm, 'word_file')" />
                  <small v-if="selectedNewsWordFile">{{ selectedNewsWordFile.name }}（{{ formatFileSize(selectedNewsWordFile.size) }}）</small>
                  <small v-else-if="editingNewsWordFile">当前 Word 稿件：{{ displayFileLabel(editingNewsWordFile) }}</small>
                  <small>上传 .docx 后保存，新闻详情页会优先展示 Word 转 HTML 的内容；下方正文可作为不用 Word 时的备用正文。</small>
                </el-form-item>
                <div v-if="newsUploadProgress > 0 || (saving && activeTab === 'news')" class="upload-progress">
                  <el-progress :percentage="newsUploadProgress" :status="newsUploadProgress === 100 ? 'success' : undefined" />
                  <span>{{ newsUploadProgress < 100 ? '正在上传新闻文件，请不要关闭页面。' : '上传完成，正在保存新闻内容。' }}</span>
                </div>
                <el-form-item label="正文"><el-input v-model="newsForm.content" type="textarea" :rows="8" /></el-form-item>
                <el-form-item label="封面图">
                  <input class="file-input" type="file" accept="image/*" @change="setFile($event, newsForm, 'cover_image')" />
                  <small v-if="editingNewsCover">当前封面：{{ displayFileLabel(editingNewsCover) }}</small>
                </el-form-item>
                <div class="form-two-col">
                  <el-form-item label="可见范围">
                    <el-select v-model="newsForm.visibility">
                      <el-option label="公开" value="public" />
                      <el-option label="成员可见" value="members" />
                      <el-option label="管理员可见" value="admins" />
                    </el-select>
                  </el-form-item>
                  <el-form-item label="置顶"><el-switch v-model="newsForm.is_pinned" /></el-form-item>
                </div>
              </el-form>
              <FormActions :saving="saving" :deletable="Boolean(editingNewsSlug)" @save="saveNews" @delete="deleteNews" />
            </article>
          </section>
        </el-tab-pane>

        <el-tab-pane label="论文成果" name="publications">
          <section class="editor-grid">
            <div class="import-strip">
              <span>批量导入：title, authors, journal, year, doi, abstract, visibility, sort_order</span>
              <a href="/import-templates/publications-template.csv?v=20260702-utf8" download="publications-template.csv">下载模板</a>
              <input type="file" accept=".csv,.tsv,.txt" @change="importResults($event, 'publications')" />
            </div>
            <ContentList title="论文成果" action-label="新增论文" :items="publicationRows" :active-key="editingPublicationId || ''" @create="resetPublication" @edit="editPublication" />
            <article class="card form-panel">
              <div class="form-heading">
                <div>
                  <span>{{ editingPublicationId ? '正在编辑' : '新增内容' }}</span>
                  <h2>{{ publicationForm.title || '论文成果' }}</h2>
                </div>
              </div>
              <el-form label-position="top">
                <el-form-item label="论文题目"><el-input v-model="publicationForm.title" /></el-form-item>
                <el-form-item label="作者"><el-input v-model="publicationForm.authors" type="textarea" :rows="2" /></el-form-item>
                <div class="form-two-col">
                  <el-form-item label="期刊"><el-input v-model="publicationForm.journal" /></el-form-item>
                  <el-form-item label="年份"><el-input-number v-model="publicationForm.year" :min="1990" :max="2100" /></el-form-item>
                </div>
                <div class="form-two-col">
                  <el-form-item label="DOI"><el-input v-model="publicationForm.doi" /></el-form-item>
                  <el-form-item label="可见范围">
                    <el-select v-model="publicationForm.visibility">
                      <el-option label="公开" value="public" />
                      <el-option label="成员可见" value="members" />
                      <el-option label="管理员可见" value="admins" />
                    </el-select>
                  </el-form-item>
                </div>
                <el-form-item label="摘要"><el-input v-model="publicationForm.abstract" type="textarea" :rows="4" /></el-form-item>
                <el-form-item label="PDF 附件">
                  <input class="file-input" type="file" accept="application/pdf" @change="setFile($event, publicationForm, 'pdf_file')" />
                  <small v-if="editingPublicationPdf">当前 PDF：{{ displayFileLabel(editingPublicationPdf) }}</small>
                </el-form-item>
                <div class="form-two-col">
                  <el-form-item label="排序"><el-input-number v-model="publicationForm.sort_order" :min="0" /></el-form-item>
                </div>
              </el-form>
              <FormActions :saving="saving" :deletable="Boolean(editingPublicationId)" @save="savePublication" @delete="deletePublication" />
            </article>
          </section>
        </el-tab-pane>

        <el-tab-pane label="科研项目" name="projects">
          <section class="editor-grid">
            <div class="import-strip">
              <span>批量导入：title, project_number, funding_source, principal_investigator, status, description, visibility, sort_order</span>
              <a href="/import-templates/projects-template.csv?v=20260702-utf8" download="projects-template.csv">下载模板</a>
              <input type="file" accept=".csv,.tsv,.txt" @change="importResults($event, 'projects')" />
            </div>
            <ContentList title="科研项目" action-label="新增项目" :items="projectRows" :active-key="editingProjectId || ''" @create="resetProject" @edit="editProject" />
            <article class="card form-panel">
              <div class="form-heading">
                <div>
                  <span>{{ editingProjectId ? '正在编辑' : '新增内容' }}</span>
                  <h2>{{ projectForm.title || '科研项目' }}</h2>
                </div>
              </div>
              <el-form label-position="top">
                <el-form-item label="项目名称"><el-input v-model="projectForm.title" /></el-form-item>
                <div class="form-two-col">
                  <el-form-item label="项目编号"><el-input v-model="projectForm.project_number" /></el-form-item>
                  <el-form-item label="资助来源"><el-input v-model="projectForm.funding_source" /></el-form-item>
                </div>
                <div class="form-two-col">
                  <el-form-item label="负责人"><el-input v-model="projectForm.principal_investigator" /></el-form-item>
                  <el-form-item label="状态"><el-input v-model="projectForm.status" /></el-form-item>
                </div>
                <div class="form-two-col">
                  <el-form-item label="开始日期"><el-date-picker v-model="projectForm.start_date" type="date" value-format="YYYY-MM-DD" clearable /></el-form-item>
                  <el-form-item label="结束日期"><el-date-picker v-model="projectForm.end_date" type="date" value-format="YYYY-MM-DD" clearable /></el-form-item>
                </div>
                <el-form-item label="可见范围">
                  <el-select v-model="projectForm.visibility">
                    <el-option label="公开" value="public" />
                    <el-option label="成员可见" value="members" />
                    <el-option label="管理员可见" value="admins" />
                  </el-select>
                </el-form-item>
                <el-form-item label="说明"><el-input v-model="projectForm.description" type="textarea" :rows="4" /></el-form-item>
                <el-form-item label="首页排序"><el-input-number v-model="projectForm.sort_order" :min="0" /></el-form-item>
              </el-form>
              <FormActions :saving="saving" :deletable="Boolean(editingProjectId)" @save="saveProject" @delete="deleteProject" />
            </article>
          </section>
        </el-tab-pane>

        <el-tab-pane label="专利成果" name="patents">
          <section class="editor-grid">
            <div class="import-strip">
              <span>批量导入：title, patent_number, inventors, status, application_date, authorization_date, visibility, sort_order</span>
              <a href="/import-templates/patents-template.csv?v=20260702-utf8" download="patents-template.csv">下载模板</a>
              <input type="file" accept=".csv,.tsv,.txt" @change="importResults($event, 'patents')" />
            </div>
            <ContentList title="专利成果" action-label="新增专利" :items="patentRows" :active-key="editingPatentId || ''" @create="resetPatent" @edit="editPatent" />
            <article class="card form-panel">
              <div class="form-heading">
                <div>
                  <span>{{ editingPatentId ? '正在编辑' : '新增内容' }}</span>
                  <h2>{{ patentForm.title || '专利成果' }}</h2>
                </div>
              </div>
              <el-form label-position="top">
                <el-form-item label="专利名称"><el-input v-model="patentForm.title" /></el-form-item>
                <div class="form-two-col">
                  <el-form-item label="专利号"><el-input v-model="patentForm.patent_number" /></el-form-item>
                  <el-form-item label="状态"><el-input v-model="patentForm.status" /></el-form-item>
                </div>
                <el-form-item label="发明人"><el-input v-model="patentForm.inventors" type="textarea" :rows="2" /></el-form-item>
                <el-form-item label="PDF 附件">
                  <input class="file-input" type="file" accept="application/pdf" @change="setFile($event, patentForm, 'pdf_file')" />
                  <small v-if="editingPatentPdf">当前 PDF：{{ displayFileLabel(editingPatentPdf) }}</small>
                </el-form-item>
                <div class="form-two-col">
                  <el-form-item label="申请日期"><el-date-picker v-model="patentForm.application_date" type="date" value-format="YYYY-MM-DD" clearable /></el-form-item>
                  <el-form-item label="授权日期"><el-date-picker v-model="patentForm.authorization_date" type="date" value-format="YYYY-MM-DD" clearable /></el-form-item>
                </div>
                <el-form-item label="可见范围">
                  <el-select v-model="patentForm.visibility">
                    <el-option label="公开" value="public" />
                    <el-option label="成员可见" value="members" />
                    <el-option label="管理员可见" value="admins" />
                  </el-select>
                </el-form-item>
                <el-form-item label="首页排序"><el-input-number v-model="patentForm.sort_order" :min="0" /></el-form-item>
              </el-form>
              <FormActions :saving="saving" :deletable="Boolean(editingPatentId)" @save="savePatent" @delete="deletePatent" />
            </article>
          </section>
        </el-tab-pane>

        <el-tab-pane label="获奖成果" name="awards">
          <section class="editor-grid">
            <div class="import-strip">
              <span>批量导入：title, award_level, award_date, participants, description, visibility, sort_order</span>
              <a href="/import-templates/awards-template.csv?v=20260702-utf8" download="awards-template.csv">下载模板</a>
              <input type="file" accept=".csv,.tsv,.txt" @change="importResults($event, 'awards')" />
            </div>
            <ContentList title="获奖成果" action-label="新增获奖" :items="awardRows" :active-key="editingAwardId || ''" @create="resetAward" @edit="editAward" />
            <article class="card form-panel">
              <div class="form-heading">
                <div>
                  <span>{{ editingAwardId ? '正在编辑' : '新增内容' }}</span>
                  <h2>{{ awardForm.title || '获奖成果' }}</h2>
                </div>
              </div>
              <el-form label-position="top">
                <el-form-item label="奖项名称"><el-input v-model="awardForm.title" /></el-form-item>
                <div class="form-two-col">
                  <el-form-item label="奖项等级"><el-input v-model="awardForm.award_level" /></el-form-item>
                  <el-form-item label="获奖日期"><el-date-picker v-model="awardForm.award_date" type="date" value-format="YYYY-MM-DD" clearable /></el-form-item>
                </div>
                <el-form-item label="参与人员"><el-input v-model="awardForm.participants" type="textarea" :rows="2" /></el-form-item>
                <div class="form-two-col">
                  <el-form-item label="获奖图片">
                    <input class="file-input" type="file" accept="image/*" @change="setFile($event, awardForm, 'image')" />
                    <small v-if="editingAwardImage">当前图片：{{ displayFileLabel(editingAwardImage) }}</small>
                  </el-form-item>
                  <el-form-item label="附件 PDF">
                    <input class="file-input" type="file" accept="application/pdf,image/*" @change="setFile($event, awardForm, 'attachment')" />
                    <small v-if="editingAwardAttachment">当前附件：{{ displayFileLabel(editingAwardAttachment) }}</small>
                  </el-form-item>
                </div>
                <el-form-item label="可见范围">
                  <el-select v-model="awardForm.visibility">
                    <el-option label="公开" value="public" />
                    <el-option label="成员可见" value="members" />
                    <el-option label="管理员可见" value="admins" />
                  </el-select>
                </el-form-item>
                <el-form-item label="说明"><el-input v-model="awardForm.description" type="textarea" :rows="4" /></el-form-item>
                <el-form-item label="首页排序"><el-input-number v-model="awardForm.sort_order" :min="0" /></el-form-item>
              </el-form>
              <FormActions :saving="saving" :deletable="Boolean(editingAwardId)" @save="saveAward" @delete="deleteAward" />
            </article>
          </section>
        </el-tab-pane>

      </el-tabs>
    </section>
  </InternalLayout>
</template>

<script setup lang="ts">
import { computed, defineComponent, h, onMounted, reactive, ref, watch } from 'vue'
import { ElButton, ElMessage, ElMessageBox, ElProgress } from 'element-plus'

import { cmsApi, type CmsNewsArticle, type CmsNewsImage } from '../../api/cms'
import type { Award, ContactInfo, Member, NewsCategory, Patent, Project, Publication, ResearchDirection, SiteSetting } from '../../api/publicPortal'
import InternalLayout from '../../layouts/InternalLayout.vue'
import { useSiteBrandStore } from '../../stores/siteBrand'

type FileField = 'cover_image' | 'avatar' | 'pdf_file' | 'image' | 'attachment' | 'word_file' | 'logo' | 'favicon' | 'hero_image'
type CmsForm = Record<string, unknown>
type Row<T> = {
  key: string | number
  title: string
  meta: string
  source: T
}

const ContentList = defineComponent({
  props: {
    title: { type: String, required: true },
    actionLabel: { type: String, required: true },
    items: { type: Array as () => Row<unknown>[], required: true },
    activeKey: { type: [String, Number], default: '' },
  },
  emits: ['create', 'edit'],
  setup(props, { emit }) {
    const keyword = ref('')
    const page = ref(1)
    const pageSize = 12
    const filteredItems = computed(() => {
      const q = keyword.value.trim().toLowerCase()
      if (!q) return props.items
      return props.items.filter((item) => `${item.title} ${item.meta}`.toLowerCase().includes(q))
    })
    const totalPages = computed(() => Math.max(1, Math.ceil(filteredItems.value.length / pageSize)))
    const pagedItems = computed(() => filteredItems.value.slice((page.value - 1) * pageSize, page.value * pageSize))
    const setPage = (nextPage: number) => {
      page.value = Math.min(totalPages.value, Math.max(1, nextPage))
    }
    watch([filteredItems, totalPages], () => {
      setPage(page.value)
    }, { flush: 'sync' })
    return () =>
      h('article', { class: 'card list-panel' }, [
        h('div', { class: 'list-toolbar' }, [
          h('div', [h('strong', props.title), h('span', `${filteredItems.value.length} / ${props.items.length}`)]),
          h(ElButton, { type: 'primary', onClick: () => emit('create') }, () => props.actionLabel),
        ]),
        h('input', {
          class: 'list-search',
          value: keyword.value,
          placeholder: `搜索${props.title}`,
          onInput: (event: Event) => {
            keyword.value = (event.target as HTMLInputElement).value
            page.value = 1
          },
        }),
        filteredItems.value.length
          ? h('div', { class: 'content-list-scroll' }, pagedItems.value.map((item) =>
              h('button', { key: item.key, class: ['content-row', { active: item.key === props.activeKey }], type: 'button', onClick: () => emit('edit', item.source) }, [
                h('strong', item.title),
                h('span', item.meta),
              ]),
            ))
          : h('div', { class: 'empty-list' }, keyword.value ? '没有找到匹配内容。' : '暂无内容，点击右上角新增。'),
        filteredItems.value.length > pageSize
          ? h('div', { class: 'list-pager' }, [
              h('button', { type: 'button', disabled: page.value === 1, onClick: () => setPage(page.value - 1) }, '上一页'),
              h('span', `第 ${page.value} / ${totalPages.value} 页`),
              h('button', { type: 'button', disabled: page.value === totalPages.value, onClick: () => setPage(page.value + 1) }, '下一页'),
            ])
          : null,
      ])
  },
})

const FormActions = defineComponent({
  props: {
    saving: { type: Boolean, default: false },
    deletable: { type: Boolean, default: false },
  },
  emits: ['save', 'delete'],
  setup(props, { emit }) {
    return () =>
      h('div', { class: 'form-actions' }, [
        cmsUploadProgress.value > 0 && activeTab.value !== 'news'
          ? h('div', { class: 'upload-progress inline-upload-progress' }, [
              h(ElProgress, { percentage: cmsUploadProgress.value, status: cmsUploadProgress.value === 100 ? 'success' : undefined }),
              h('span', cmsUploadProgress.value < 100 ? '正在上传附件，请不要关闭页面。' : '上传完成，正在保存内容。'),
            ])
          : null,
        h(ElButton, { type: 'primary', loading: props.saving, onClick: () => emit('save') }, () => '保存'),
        props.deletable ? h(ElButton, { plain: true, onClick: () => emit('delete') }, () => '删除') : null,
      ])
  },
})

const activeTab = ref('site')
const saving = ref(false)
const uploadingNewsImage = ref(false)
const siteBrand = useSiteBrandStore()
const cmsUploadProgress = ref(0)
const newsUploadProgress = ref(0)
const newsImageUploadProgress = ref(0)
const newsFileInputKey = ref(0)

const researchItems = ref<ResearchDirection[]>([])
const siteSettings = ref<SiteSetting[]>([])
const contactInfoItems = ref<ContactInfo[]>([])
const memberItems = ref<Member[]>([])
const newsItems = ref<CmsNewsArticle[]>([])
const newsCategories = ref<NewsCategory[]>([])
const publicationItems = ref<Publication[]>([])
const projectItems = ref<Project[]>([])
const patentItems = ref<Patent[]>([])
const awardItems = ref<Award[]>([])

const editingResearchSlug = ref('')
const editingSiteId = ref<number | null>(null)
const editingContactId = ref<number | null>(null)
const editingSiteLogo = ref('')
const editingSiteFavicon = ref('')
const editingSiteHeroImage = ref('')
const editingResearchCover = ref('')
const editingMemberId = ref<number | null>(null)
const editingMemberAvatar = ref('')
const editingNewsSlug = ref('')
const editingNewsId = ref<number | null>(null)
const editingNewsCover = ref('')
const editingNewsWordFile = ref('')
const editingNewsImages = ref<CmsNewsImage[]>([])
const editingPublicationId = ref<number | null>(null)
const editingPublicationPdf = ref('')
const editingProjectId = ref<number | null>(null)
const editingPatentId = ref<number | null>(null)
const editingAwardId = ref<number | null>(null)
const editingPatentPdf = ref('')
const editingAwardImage = ref('')
const editingAwardAttachment = ref('')

const researchForm = reactive<CmsForm>({ title: '', summary: '', keywords: '', content: '', cover_image: undefined, sort_order: 0 })
const siteForm = reactive<CmsForm>({
  site_name: '中农雨磷',
  site_subtitle: '中国农业大学资源与环境学院',
  keywords: '聚焦微生物生态、有机废弃物资源转化与高值产品开发',
  description: '',
  footer_text: '',
  contact_email: '',
  contact_phone: '',
  address: '',
  logo: undefined,
  favicon: undefined,
  hero_image: undefined,
})
const externalLinks = reactive([
  { label: '中国农业大学', url: 'https://www.cau.edu.cn/' },
  { label: '资源与环境学院', url: 'https://zihuan.cau.edu.cn/' },
  { label: '教师个人主页', url: 'https://faculty.cau.edu.cn/' },
])
const contactForm = reactive<CmsForm>({
  title: '欢迎对微生物生态与农业资源循环感兴趣的同学加入',
  content: '',
  email: '',
  phone: '',
  address: '',
  map_url: '',
})
const memberForm = reactive<CmsForm>({
  name: '',
  role_type: '',
  research_direction: '',
  email: '',
  avatar: undefined,
  profile: '',
  sort_order: 0,
})
const newsForm = reactive<CmsForm>({
  title: '',
  summary: '',
  content: '',
  cover_image: undefined,
  word_file: undefined,
  event_date: '',
  location: '',
  category_id: null,
  status: 'published',
  visibility: 'public',
  is_pinned: false,
})
const newsImageForm = reactive({
  file: undefined as File | undefined,
  caption: '',
  sort_order: 0,
})
const publicationForm = reactive<CmsForm>({
  title: '',
  authors: '',
  journal: '',
  year: new Date().getFullYear(),
  doi: '',
  abstract: '',
  pdf_file: undefined,
  visibility: 'public',
  sort_order: 0,
})
const projectForm = reactive<CmsForm>({
  title: '',
  project_number: '',
  funding_source: '',
  principal_investigator: '',
  start_date: '',
  end_date: '',
  status: '',
  visibility: 'public',
  description: '',
  sort_order: 0,
})
const patentForm = reactive<CmsForm>({
  title: '',
  patent_number: '',
  inventors: '',
  application_date: '',
  authorization_date: '',
  status: '',
  pdf_file: undefined,
  visibility: 'public',
  sort_order: 0,
})
const awardForm = reactive<CmsForm>({
  title: '',
  award_level: '',
  award_date: '',
  participants: '',
  description: '',
  image: undefined,
  attachment: undefined,
  visibility: 'public',
  sort_order: 0,
})

const researchRows = computed<Row<ResearchDirection>[]>(() =>
  researchItems.value.map((item) => ({ key: item.slug, title: item.title, meta: item.keywords || item.summary || item.slug, source: item })),
)
const memberRows = computed<Row<Member>[]>(() =>
  memberItems.value.map((item) => ({
    key: item.id,
    title: item.name,
    meta: `${item.sort_order ? `排序 ${item.sort_order}` : '不展示'} · ${roleText(item.role_type) || '身份头衔待补充'} · ${item.research_direction || '研究方向待补充'}`,
    source: item,
  })),
)
const newsRows = computed<Row<CmsNewsArticle>[]>(() =>
  newsItems.value.map((item) => ({
    key: item.slug,
    title: item.title,
    meta: `${item.event_date || '未设置日期'} · ${statusText(item.status)}`,
    source: item,
  })),
)
const selectedNewsWordFile = computed(() => (newsForm.word_file instanceof File ? newsForm.word_file : null))
const publicationRows = computed<Row<Publication>[]>(() =>
  publicationItems.value.map((item) => ({ key: item.id, title: item.title, meta: `${visibilityText(item.visibility)} · ${item.year} · ${item.journal || '期刊待补充'}`, source: item })),
)
const projectRows = computed<Row<Project>[]>(() =>
  projectItems.value.map((item) => ({ key: item.id, title: item.title, meta: `${visibilityText(item.visibility)} · ${item.funding_source || '资助来源待补充'} · ${item.status || '状态待补充'}`, source: item })),
)
const patentRows = computed<Row<Patent>[]>(() =>
  patentItems.value.map((item) => ({ key: item.id, title: item.title, meta: `${visibilityText(item.visibility)} · ${item.patent_number || '专利号待补充'} · ${item.status || '状态待补充'}`, source: item })),
)
const awardRows = computed<Row<Award>[]>(() =>
  awardItems.value.map((item) => ({ key: item.id, title: item.title, meta: `${visibilityText(item.visibility)} · ${item.award_level || '等级待补充'} · ${item.award_date || '日期待补充'}`, source: item })),
)
const cmsOverview = computed(() => [
  { label: '首页设置', value: siteSettings.value.length ? 1 : 0, note: '基础文案与联系信息' },
  { label: '研究方向', value: researchItems.value.length, note: '公开门户展示' },
  { label: '团队成员', value: memberItems.value.length, note: '师生与校友信息' },
  { label: '新闻活动', value: newsItems.value.length, note: '组内动态与活动' },
  { label: '论文成果', value: publicationItems.value.length, note: '科研成果维护' },
  { label: '科研项目', value: projectItems.value.length, note: '项目维护' },
  { label: '专利成果', value: patentItems.value.length, note: '专利维护' },
  { label: '获奖成果', value: awardItems.value.length, note: '获奖维护' },
])

async function loadAll() {
  const [settings, contacts, research, members, categories, news, publications, projects, patents, awards] = await Promise.allSettled([
    cmsApi.listSiteSettings(),
    cmsApi.listContactInfo(),
    cmsApi.listResearch(),
    cmsApi.listMembers(),
    cmsApi.listNewsCategories(),
    cmsApi.listNews(),
    cmsApi.listPublications(),
    cmsApi.listProjects(),
    cmsApi.listPatents(),
    cmsApi.listAwards(),
  ])
  const settingsValue = resultValue(settings, siteSettings.value)
  const contactsValue = resultValue(contacts, contactInfoItems.value)
  siteSettings.value = settingsValue
  contactInfoItems.value = contactsValue
  fillSiteForms(settingsValue[0], contactsValue[0])
  researchItems.value = resultValue(research, researchItems.value)
  memberItems.value = resultValue(members, memberItems.value)
  newsCategories.value = resultValue(categories, newsCategories.value)
  newsItems.value = resultValue(news, newsItems.value)
  publicationItems.value = resultValue(publications, publicationItems.value)
  projectItems.value = resultValue(projects, projectItems.value)
  patentItems.value = resultValue(patents, patentItems.value)
  awardItems.value = resultValue(awards, awardItems.value)

  if ([settings, contacts, research, members, categories, news, publications, projects, patents, awards].some((item) => item.status === 'rejected')) {
    ElMessage.warning('部分门户内容加载失败，请刷新或检查当前账号是否有门户编辑权限。')
  }
}

function resultValue<T>(result: PromiseSettledResult<T[]>, fallback: T[]) {
  return result.status === 'fulfilled' ? result.value : fallback
}

function fillSiteForms(setting?: SiteSetting, contact?: ContactInfo) {
  editingSiteId.value = setting?.id || null
  editingContactId.value = contact?.id || null
  editingSiteLogo.value = setting?.logo || ''
  editingSiteFavicon.value = setting?.favicon || ''
  editingSiteHeroImage.value = setting?.hero_image || ''
  Object.assign(siteForm, {
    site_name: setting?.site_name || '中农雨磷',
    site_subtitle: setting?.site_subtitle || '中国农业大学资源与环境学院',
    keywords: setting?.keywords || '聚焦微生物生态、有机废弃物资源转化与高值产品开发',
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
    title: contact?.title || '欢迎对微生物生态与农业资源循环感兴趣的同学加入',
    content: contact?.content || '',
    email: contact?.email || setting?.contact_email || '',
    phone: contact?.phone || setting?.contact_phone || '',
    address: contact?.address || setting?.address || '',
    map_url: contact?.map_url || '',
  })
}

async function saveSiteSetting() {
  applyExternalLinksToSiteForm()
  await save((onUploadProgress) =>
    editingSiteId.value ? cmsApi.updateSiteSetting(editingSiteId.value, siteForm, onUploadProgress) : cmsApi.createSiteSetting(siteForm, onUploadProgress),
  )
  await siteBrand.load(true)
}

function applyExternalLinksToSiteForm() {
  siteForm.external_links = externalLinks
    .map((link) => ({ label: link.label.trim(), url: link.url.trim() }))
    .filter((link) => link.label && link.url)
}

function fillExternalLinks(links?: SiteSetting['external_links']) {
  const defaults = [
    { label: '中国农业大学', url: 'https://www.cau.edu.cn/' },
    { label: '资源与环境学院', url: 'https://zihuan.cau.edu.cn/' },
    { label: '教师个人主页', url: 'https://faculty.cau.edu.cn/' },
  ]
  const nextLinks = links?.length ? links : defaults
  externalLinks.splice(0, externalLinks.length, ...nextLinks.slice(0, 5).map((link) => ({
    label: link.label || '',
    url: link.url || '',
  })))
  while (externalLinks.length < 3) externalLinks.push({ label: '', url: '' })
}

async function saveContactInfo() {
  await save((onUploadProgress) =>
    editingContactId.value ? cmsApi.updateContactInfo(editingContactId.value, contactForm, onUploadProgress) : cmsApi.createContactInfo(contactForm, onUploadProgress),
  )
}

async function saveContactSection() {
  saving.value = true
  cmsUploadProgress.value = 0
  const onUploadProgress = createCmsUploadProgressHandler()
  try {
    applyExternalLinksToSiteForm()
    await Promise.all([
      editingContactId.value ? cmsApi.updateContactInfo(editingContactId.value, contactForm, onUploadProgress) : cmsApi.createContactInfo(contactForm, onUploadProgress),
      editingSiteId.value ? cmsApi.updateSiteSetting(editingSiteId.value, siteForm, onUploadProgress) : cmsApi.createSiteSetting(siteForm, onUploadProgress),
    ])
    if (cmsUploadProgress.value > 0) cmsUploadProgress.value = 100
    await loadAll()
    await siteBrand.load(true)
    ElMessage.success('内容已保存')
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '保存失败，请检查权限和表单内容')
  } finally {
    saving.value = false
    resetCmsUploadProgressSoon()
  }
}

function setFile(event: Event, form: CmsForm, field: FileField) {
  const input = event.target as HTMLInputElement
  form[field] = input.files?.[0]
  if (form === newsForm && (field === 'word_file' || field === 'cover_image')) newsUploadProgress.value = 0
}

function displayFileName(value: string) {
  const withoutQuery = value.split('?')[0]
  const filename = withoutQuery.split('/').filter(Boolean).pop() || value
  let decoded = filename
  try {
    decoded = decodeURIComponent(filename)
  } catch {
    decoded = filename
  }
  return decoded.length > 42 ? `${decoded.slice(0, 18)}...${decoded.slice(-18)}` : decoded
}

function displayFileLabel(value: string) {
  const size = findUploadedFileSize(value)
  return size ? `${displayFileName(value)}（${formatFileSize(size)}）` : displayFileName(value)
}

function findUploadedFileSize(value: string) {
  const match = (url?: string) => Boolean(url && value && (url === value || url.split('?')[0] === value.split('?')[0]))
  const site = siteSettings.value.find((item) => match(item.logo) || match(item.favicon) || match(item.hero_image))
  if (site) {
    if (match(site.logo)) return site.logo_size || 0
    if (match(site.favicon)) return site.favicon_size || 0
    if (match(site.hero_image)) return site.hero_image_size || 0
  }
  const research = researchItems.value.find((item) => match(item.cover_image))
  if (research) return research.cover_image_size || 0
  const member = memberItems.value.find((item) => match(item.avatar))
  if (member) return member.avatar_size || 0
  const news = newsItems.value.find((item) => match(item.cover_image) || match(item.word_file))
  if (news) {
    if (match(news.cover_image)) return news.cover_image_size || 0
    if (match(news.word_file)) return news.word_file_size || 0
  }
  const publication = publicationItems.value.find((item) => match(item.pdf_file))
  if (publication) return publication.pdf_file_size || 0
  const patent = patentItems.value.find((item) => match(item.pdf_file))
  if (patent) return patent.pdf_file_size || 0
  const award = awardItems.value.find((item) => match(item.image) || match(item.attachment))
  if (award) {
    if (match(award.image)) return award.image_size || 0
    if (match(award.attachment)) return award.attachment_size || 0
  }
  return 0
}

function formatFileSize(size: number) {
  if (size >= 1024 * 1024) return `${(size / 1024 / 1024).toFixed(1)} MB`
  if (size >= 1024) return `${(size / 1024).toFixed(1)} KB`
  return `${size} B`
}

function createCmsUploadProgressHandler() {
  return (event: { loaded: number; total?: number }) => {
    if (!event.total) return
    cmsUploadProgress.value = Math.min(99, Math.round((event.loaded / event.total) * 100))
  }
}

function resetCmsUploadProgressSoon() {
  setTimeout(() => {
    if (!saving.value) cmsUploadProgress.value = 0
  }, 800)
}

function uploadErrorMessage(error: any, fallback: string) {
  const data = error?.response?.data
  if (data?.detail) return data.detail
  if (data?.word_file?.length) return data.word_file[0]
  if (data?.image?.length) return data.image[0]
  if (data?.cover_image?.length) return data.cover_image[0]
  if (error?.code === 'ECONNABORTED') return '上传超时，请检查网络后重试。'
  if (!error?.response) return '上传连接失败，请检查网络或服务器上传限制。'
  return fallback
}

function resetResearch() {
  editingResearchSlug.value = ''
  editingResearchCover.value = ''
  Object.assign(researchForm, { title: '', summary: '', keywords: '', content: '', cover_image: undefined, sort_order: 0 })
}

function editResearch(item: ResearchDirection) {
  editingResearchSlug.value = item.slug
  editingResearchCover.value = item.cover_image || ''
  Object.assign(researchForm, {
    title: item.title,
    summary: item.summary,
    keywords: item.keywords || '',
    content: item.content || '',
    cover_image: undefined,
    sort_order: item.sort_order || 0,
  })
}

async function saveResearch() {
  await save((onUploadProgress) => (editingResearchSlug.value ? cmsApi.updateResearch(editingResearchSlug.value, researchForm, onUploadProgress) : cmsApi.createResearch(researchForm, onUploadProgress)))
  resetResearch()
}

async function deleteResearch() {
  await removeAfterConfirm('确定删除这个研究方向吗？', () => cmsApi.deleteResearch(editingResearchSlug.value), resetResearch)
}

function resetMember() {
  editingMemberId.value = null
  editingMemberAvatar.value = ''
  Object.assign(memberForm, {
    name: '',
    role_type: '',
    research_direction: '',
    email: '',
    avatar: undefined,
    profile: '',
    sort_order: 0,
  })
}

function editMember(item: Member) {
  editingMemberId.value = item.id
  editingMemberAvatar.value = item.avatar || ''
  Object.assign(memberForm, {
    name: item.name,
    role_type: item.role_label || item.role_type || '',
    research_direction: item.research_direction || '',
    email: item.email || '',
    avatar: undefined,
    profile: item.profile || '',
    sort_order: (item as Member & { sort_order?: number }).sort_order || 0,
  })
}

async function saveMember() {
  await save((onUploadProgress) => (editingMemberId.value ? cmsApi.updateMember(editingMemberId.value, memberForm, onUploadProgress) : cmsApi.createMember(memberForm, onUploadProgress)))
  resetMember()
}

async function deleteMember() {
  if (!editingMemberId.value) return
  await removeAfterConfirm('确定删除这个团队成员吗？', () => cmsApi.deleteMember(editingMemberId.value as number), resetMember)
}

function resetNews() {
  editingNewsSlug.value = ''
  editingNewsId.value = null
  editingNewsCover.value = ''
  editingNewsWordFile.value = ''
  editingNewsImages.value = []
  newsFileInputKey.value += 1
  newsUploadProgress.value = 0
  Object.assign(newsForm, {
    title: '',
    summary: '',
    content: '',
    cover_image: undefined,
    word_file: undefined,
    event_date: '',
    location: '',
    category_id: null,
    status: 'published',
    visibility: 'public',
    is_pinned: false,
  })
  resetNewsImageForm()
}

function editNews(item: CmsNewsArticle) {
  editingNewsSlug.value = item.slug
  editingNewsId.value = item.id
  editingNewsCover.value = item.cover_image || ''
  editingNewsWordFile.value = item.word_file || ''
  editingNewsImages.value = (item.images || []) as CmsNewsImage[]
  newsFileInputKey.value += 1
  newsUploadProgress.value = 0
  Object.assign(newsForm, {
    title: item.title,
    summary: item.summary || '',
    content: item.content || '',
    cover_image: undefined,
    word_file: undefined,
    event_date: item.event_date || '',
    location: item.location || '',
    category_id: item.category?.id || null,
    status: item.status || 'published',
    visibility: item.visibility || 'public',
    is_pinned: item.is_pinned || false,
  })
}

async function saveNews() {
  saving.value = true
  newsUploadProgress.value = 0
  try {
    const onUploadProgress = (event: { loaded: number; total?: number }) => {
      if (!event.total) return
      newsUploadProgress.value = Math.min(99, Math.round((event.loaded / event.total) * 100))
    }
    const saved = editingNewsSlug.value
      ? await cmsApi.updateNews(editingNewsSlug.value, newsForm, onUploadProgress)
      : await cmsApi.createNews(newsForm, onUploadProgress)
    newsUploadProgress.value = 100
    newsFileInputKey.value += 1
    await loadAll()
    editNews(saved)
    ElMessage.success('新闻已保存')
  } catch (error: any) {
    ElMessage.error(uploadErrorMessage(error, '保存失败，请检查权限和表单内容。'))
  } finally {
    saving.value = false
    setTimeout(() => {
      if (!saving.value) newsUploadProgress.value = 0
    }, 800)
  }
}

async function deleteNews() {
  await removeAfterConfirm('确定删除这条新闻吗？', () => cmsApi.deleteNews(editingNewsSlug.value), resetNews)
}

function setNewsImageFile(event: Event) {
  const input = event.target as HTMLInputElement
  newsImageForm.file = input.files?.[0]
  newsImageUploadProgress.value = 0
}

function resetNewsImageForm() {
  newsImageForm.file = undefined
  newsImageForm.caption = ''
  newsImageForm.sort_order = 0
}

async function uploadNewsImage() {
  if (!editingNewsId.value) {
    ElMessage.warning('请先保存新闻正文，再添加活动图片。')
    return
  }
  if (!newsImageForm.file) {
    ElMessage.warning('请选择要上传的图片。')
    return
  }
  uploadingNewsImage.value = true
  newsImageUploadProgress.value = 0
  try {
    await cmsApi.createNewsImage({
      article_id: editingNewsId.value,
      image: newsImageForm.file,
      caption: newsImageForm.caption,
      sort_order: newsImageForm.sort_order,
    }, (event) => {
      if (!event.total) return
      newsImageUploadProgress.value = Math.min(99, Math.round((event.loaded / event.total) * 100))
    })
    newsImageUploadProgress.value = 100
    resetNewsImageForm()
    await loadAll()
    const updated = newsItems.value.find((item) => item.id === editingNewsId.value)
    if (updated) editNews(updated)
    ElMessage.success('活动图片已添加')
  } catch (error: any) {
    ElMessage.error(uploadErrorMessage(error, '图片上传失败'))
  } finally {
    uploadingNewsImage.value = false
    setTimeout(() => {
      if (!uploadingNewsImage.value) newsImageUploadProgress.value = 0
    }, 800)
  }
}

async function deleteNewsImage(id: number) {
  try {
    await cmsApi.deleteNewsImage(id)
    await loadAll()
    const updated = newsItems.value.find((item) => item.id === editingNewsId.value)
    if (updated) editNews(updated)
    ElMessage.success('图片已删除')
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '图片删除失败')
  }
}

function resetPublication() {
  editingPublicationId.value = null
  editingPublicationPdf.value = ''
  Object.assign(publicationForm, {
    title: '',
    authors: '',
    journal: '',
    year: new Date().getFullYear(),
    doi: '',
    abstract: '',
    pdf_file: undefined,
    visibility: 'public',
    sort_order: 0,
  })
}

function editPublication(item: Publication) {
  editingPublicationId.value = item.id
  editingPublicationPdf.value = item.pdf_file || ''
  Object.assign(publicationForm, {
    title: item.title,
    authors: item.authors,
    journal: item.journal || '',
    year: item.year,
    doi: item.doi || '',
    abstract: item.abstract || '',
    pdf_file: undefined,
    visibility: item.visibility || 'public',
    sort_order: (item as Publication & { sort_order?: number }).sort_order || 0,
  })
}

async function savePublication() {
  await save((onUploadProgress) =>
    editingPublicationId.value ? cmsApi.updatePublication(editingPublicationId.value, publicationForm, onUploadProgress) : cmsApi.createPublication(publicationForm, onUploadProgress),
  )
  resetPublication()
}

async function deletePublication() {
  if (!editingPublicationId.value) return
  await removeAfterConfirm('确定删除这篇论文吗？', () => cmsApi.deletePublication(editingPublicationId.value as number), resetPublication)
}

function resetProject() {
  editingProjectId.value = null
  Object.assign(projectForm, {
    title: '',
    project_number: '',
    funding_source: '',
    principal_investigator: '',
    start_date: '',
    end_date: '',
    status: '',
    visibility: 'public',
    description: '',
    sort_order: 0,
  })
}

function editProject(item: Project) {
  editingProjectId.value = item.id
  Object.assign(projectForm, {
    title: item.title,
    project_number: item.project_number || '',
    funding_source: item.funding_source || '',
    principal_investigator: item.principal_investigator || '',
    start_date: item.start_date || '',
    end_date: item.end_date || '',
    status: item.status || '',
    visibility: (item as Project & { visibility?: string }).visibility || 'public',
    description: item.description || '',
    sort_order: item.sort_order || 0,
  })
}

async function saveProject() {
  await save((onUploadProgress) => (editingProjectId.value ? cmsApi.updateProject(editingProjectId.value, projectForm, onUploadProgress) : cmsApi.createProject(projectForm, onUploadProgress)))
  resetProject()
}

async function deleteProject() {
  if (!editingProjectId.value) return
  await removeAfterConfirm('确定删除这个科研项目吗？', () => cmsApi.deleteProject(editingProjectId.value as number), resetProject)
}

function resetPatent() {
  editingPatentId.value = null
  editingPatentPdf.value = ''
  Object.assign(patentForm, {
    title: '',
    patent_number: '',
    inventors: '',
    application_date: '',
    authorization_date: '',
    status: '',
    pdf_file: undefined,
    visibility: 'public',
    sort_order: 0,
  })
}

function editPatent(item: Patent) {
  editingPatentId.value = item.id
  editingPatentPdf.value = item.pdf_file || ''
  Object.assign(patentForm, {
    title: item.title,
    patent_number: item.patent_number || '',
    inventors: item.inventors || '',
    application_date: item.application_date || '',
    authorization_date: item.authorization_date || '',
    status: item.status || '',
    pdf_file: undefined,
    visibility: (item as Patent & { visibility?: string }).visibility || 'public',
    sort_order: item.sort_order || 0,
  })
}

async function savePatent() {
  await save((onUploadProgress) => (editingPatentId.value ? cmsApi.updatePatent(editingPatentId.value, patentForm, onUploadProgress) : cmsApi.createPatent(patentForm, onUploadProgress)))
  resetPatent()
}

async function deletePatent() {
  if (!editingPatentId.value) return
  await removeAfterConfirm('确定删除这个专利成果吗？', () => cmsApi.deletePatent(editingPatentId.value as number), resetPatent)
}

function resetAward() {
  editingAwardId.value = null
  editingAwardImage.value = ''
  editingAwardAttachment.value = ''
  Object.assign(awardForm, {
    title: '',
    award_level: '',
    award_date: '',
    participants: '',
    description: '',
    image: undefined,
    attachment: undefined,
    visibility: 'public',
    sort_order: 0,
  })
}

function editAward(item: Award) {
  editingAwardId.value = item.id
  editingAwardImage.value = item.image || ''
  editingAwardAttachment.value = item.attachment || ''
  Object.assign(awardForm, {
    title: item.title,
    award_level: item.award_level || '',
    award_date: item.award_date || '',
    participants: item.participants || '',
    description: item.description || '',
    image: undefined,
    attachment: undefined,
    visibility: item.visibility || 'public',
    sort_order: item.sort_order || 0,
  })
}

async function saveAward() {
  await save((onUploadProgress) => (editingAwardId.value ? cmsApi.updateAward(editingAwardId.value, awardForm, onUploadProgress) : cmsApi.createAward(awardForm, onUploadProgress)))
  resetAward()
}

async function deleteAward() {
  if (!editingAwardId.value) return
  await removeAfterConfirm('确定删除这个获奖成果吗？', () => cmsApi.deleteAward(editingAwardId.value as number), resetAward)
}

type ResultImportKind = 'publications' | 'projects' | 'patents' | 'awards'

async function importResults(event: Event, kind: ResultImportKind) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  input.value = ''
  if (!file) return
  if (file.name.toLowerCase().endsWith('.xlsx') || file.name.toLowerCase().endsWith('.xls')) {
    ElMessage.warning('请先在 Excel 中另存为 CSV，再导入。')
    return
  }
  try {
    const rows = parseDelimited(await file.text())
    if (!rows.length) {
      ElMessage.warning('没有读取到可导入的数据。')
      return
    }
    saving.value = true
    for (const row of rows) {
      const payload = normalizeImportRow(row, kind)
      if (!payload.title) continue
      if (kind === 'publications') await cmsApi.createPublication(payload)
      if (kind === 'projects') await cmsApi.createProject(payload)
      if (kind === 'patents') await cmsApi.createPatent(payload)
      if (kind === 'awards') await cmsApi.createAward(payload)
    }
    await loadAll()
    ElMessage.success(`已导入 ${rows.length} 条记录`)
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '导入失败，请检查表头和日期格式。')
  } finally {
    saving.value = false
  }
}

function parseDelimited(text: string) {
  const lines = text.replace(/^\uFEFF/, '').split(/\r?\n/).filter((line) => line.trim())
  if (lines.length < 2) return []
  const delimiter = lines[0].includes('\t') ? '\t' : ','
  const headers = splitDelimitedLine(lines[0], delimiter).map((item) => item.trim())
  return lines.slice(1).map((line) => {
    const values = splitDelimitedLine(line, delimiter)
    return headers.reduce<Record<string, string>>((row, header, index) => {
      row[header] = values[index]?.trim() || ''
      return row
    }, {})
  })
}

function splitDelimitedLine(line: string, delimiter: string) {
  const result: string[] = []
  let value = ''
  let quoted = false
  for (let index = 0; index < line.length; index += 1) {
    const char = line[index]
    if (char === '"' && line[index + 1] === '"') {
      value += '"'
      index += 1
    } else if (char === '"') {
      quoted = !quoted
    } else if (char === delimiter && !quoted) {
      result.push(value)
      value = ''
    } else {
      value += char
    }
  }
  result.push(value)
  return result
}

function normalizeImportRow(row: Record<string, string>, kind: ResultImportKind) {
  const visibility = row.visibility || 'public'
  if (kind === 'publications') {
    return {
      title: row.title || row.论文题目 || '',
      authors: row.authors || row.作者 || '',
      journal: row.journal || row.期刊 || '',
      year: Number(row.year || row.年份 || new Date().getFullYear()),
      doi: row.doi || row.DOI || '',
      abstract: row.abstract || row.摘要 || '',
      visibility,
      sort_order: Number(row.sort_order || 0),
    }
  }
  if (kind === 'projects') {
    return {
      title: row.title || row.项目名称 || '',
      project_number: row.project_number || row.项目编号 || '',
      funding_source: row.funding_source || row.资助来源 || row.来源 || '',
      principal_investigator: row.principal_investigator || row.负责人 || '',
      status: row.status || row.状态 || '',
      description: row.description || row.说明 || '',
      visibility,
      sort_order: Number(row.sort_order || 0),
    }
  }
  if (kind === 'patents') {
    return {
      title: row.title || row.专利名称 || '',
      patent_number: row.patent_number || row.专利号 || '',
      inventors: row.inventors || row.发明人 || '',
      status: row.status || row.状态 || '',
      application_date: row.application_date || row.申请日期 || '',
      authorization_date: row.authorization_date || row.授权日期 || '',
      visibility,
      sort_order: Number(row.sort_order || 0),
    }
  }
  return {
    title: row.title || row.奖项名称 || '',
    award_level: row.award_level || row.奖项等级 || '',
    award_date: row.award_date || row.获奖日期 || '',
    participants: row.participants || row.参与人员 || '',
    description: row.description || row.说明 || '',
    visibility,
    sort_order: Number(row.sort_order || 0),
  }
}

async function save(action: (onUploadProgress?: (event: { loaded: number; total?: number }) => void) => Promise<unknown>) {
  saving.value = true
  cmsUploadProgress.value = 0
  const onUploadProgress = createCmsUploadProgressHandler()
  try {
    await action(onUploadProgress)
    if (cmsUploadProgress.value > 0) cmsUploadProgress.value = 100
    await loadAll()
    ElMessage.success('内容已保存')
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '保存失败，请检查权限和表单内容')
  } finally {
    saving.value = false
    resetCmsUploadProgressSoon()
  }
}

async function removeAfterConfirm(message: string, action: () => Promise<unknown>, reset: () => void) {
  try {
    await ElMessageBox.confirm(message, '删除确认', { type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消' })
    await save(action)
    reset()
  } catch (error: any) {
    if (error !== 'cancel') ElMessage.error('删除失败')
  }
}

function roleText(role: string) {
  return (
    {
      PI: '硕博导师',
      teacher: '教师',
      postdoc: '博士后',
      phd: '博士生',
      master: '硕士生',
      undergraduate: '本科生',
      alumni: '已毕业学生',
      visitor: '访问学生',
    }[role] || role
  )
}

function statusText(status: string) {
  return ({ draft: '草稿', published: '已发布', archived: '已归档' }[status] || status)
}

function visibilityText(visibility?: string) {
  return ({ public: '公开', members: '成员可见', admins: '管理员可见' }[visibility || ''] || '未设置')
}

onMounted(loadAll)
</script>

<style scoped>
.cms-page {
  display: grid;
  gap: 12px;
}

.cms-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  border: 1px solid rgba(0, 135, 60, 0.12);
  border-radius: var(--radius-md);
  padding: 14px 18px;
  background: #fff;
  box-shadow: none;
}

.cms-heading span {
  color: var(--color-cau-green);
  font-size: 13px;
  font-weight: 700;
}

.cms-heading h1 {
  margin: 3px 0 0;
  color: var(--color-deep-green);
  font-size: 24px;
  font-weight: 650;
  line-height: 1.2;
}

.heading-actions {
  display: flex;
  align-items: center;
  flex: 0 0 auto;
  gap: 12px;
}

.cms-stat-strip {
  display: flex;
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
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 10px 14px 16px;
  background: #fff;
  box-shadow: none;
}

.cms-tabs :deep(.el-tabs__header) {
  margin-bottom: 12px;
}

.cms-tabs :deep(.el-tabs__nav-wrap::after) {
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
  grid-template-columns: repeat(2, minmax(0, 1fr));
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
  padding: 18px 20px;
  box-shadow: none;
}

.site-form-panel {
  min-height: 100%;
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

.list-panel :deep(.list-toolbar) {
  align-items: flex-start;
  border-bottom: 1px solid var(--color-line);
  margin-bottom: 12px;
  min-height: 58px;
  padding-bottom: 12px;
}

.list-panel :deep(.list-toolbar strong),
.list-panel :deep(.list-toolbar span) {
  display: block;
}

.list-panel :deep(.list-toolbar > div) {
  min-width: 0;
}

.list-panel :deep(.list-toolbar strong) {
  color: var(--color-deep-green);
  font-size: 19px;
  font-weight: 650;
}

.list-panel :deep(.list-toolbar span) {
  margin-top: 2px;
  color: var(--color-muted);
  font-size: 12px;
}

.list-panel :deep(.list-toolbar .el-button) {
  --el-button-size: 32px;
  flex: 0 0 auto;
  min-height: 32px;
  padding: 7px 12px;
  color: #fff !important;
}

.cms-page :deep(.el-button--primary),
.cms-page :deep(.el-button--primary span) {
  color: #fff !important;
}

.panel-heading h2 {
  margin: 0;
  color: var(--color-deep-green);
  font-size: 19px;
  font-weight: 650;
}

.list-panel :deep(.list-search) {
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

.list-panel :deep(.list-search:focus) {
  border-color: rgba(0, 135, 60, 0.35);
  outline: none;
  box-shadow: 0 0 0 3px rgba(0, 135, 60, 0.08);
}

.list-panel :deep(.content-list-scroll) {
  min-height: 0;
  overflow-y: auto;
  overflow-x: hidden;
  padding-right: 6px;
}

.list-panel :deep(.content-row) {
  display: block;
  width: 100%;
  border: 1px solid var(--color-line);
  border-radius: 8px;
  margin-bottom: 10px;
  padding: 12px 13px;
  background: #fff;
  cursor: pointer;
  text-align: left;
}

.list-panel :deep(.content-row:hover),
.list-panel :deep(.content-row.active) {
  border-color: rgba(0, 135, 60, 0.14);
  background: var(--color-eco-green);
}

.list-panel :deep(.content-row:hover strong),
.list-panel :deep(.content-row.active strong) {
  color: var(--color-cau-green);
}

.list-panel :deep(.content-row strong),
.list-panel :deep(.content-row span),
.form-panel small {
  display: block;
}

.list-panel :deep(.content-row strong) {
  display: block;
  overflow: hidden;
  color: var(--color-text);
  font-size: 14px;
  line-height: 1.45;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.list-panel :deep(.content-row span),
.form-panel small,
.empty-list {
  color: var(--color-muted);
  font-size: 13px;
}

.list-panel :deep(.content-row span) {
  margin-top: 7px;
  overflow: hidden;
  line-height: 1.4;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.list-panel :deep(.empty-list) {
  border-top: 1px solid var(--color-line);
  padding-top: 16px;
}

.list-panel :deep(.list-pager) {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  border-top: 1px solid var(--color-line);
  margin-top: 10px;
  padding-top: 10px;
  background: #fff;
}

.list-panel :deep(.list-pager button) {
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

.list-panel :deep(.list-pager button:disabled) {
  border-color: var(--color-border);
  color: var(--color-muted);
  cursor: not-allowed;
  opacity: 0.6;
}

.list-panel :deep(.list-pager span) {
  color: var(--color-muted);
  font-size: 13px;
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

.import-strip span {
  min-width: 0;
  overflow: hidden;
  color: var(--color-muted);
  font-size: 12px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.import-strip input {
  flex: 0 0 210px;
  color: var(--color-muted);
  font-size: 12px;
}

.import-strip a {
  flex: 0 0 auto;
  border: 1px solid rgba(0, 135, 60, 0.22);
  border-radius: 999px;
  padding: 5px 12px;
  color: var(--color-primary);
  font-size: 12px;
  font-weight: 700;
  text-decoration: none;
  white-space: nowrap;
}

.import-strip a:hover {
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

.form-panel :deep(.el-form-item) {
  margin-bottom: 14px;
}

.form-panel :deep(.el-textarea__inner) {
  line-height: 1.7;
}

.form-two-col {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.external-link-editor {
  display: grid;
  gap: 8px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  margin-bottom: 14px;
  padding: 14px;
  background: var(--color-soft-gray);
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
  .gallery-upload {
    grid-template-columns: 1fr;
  }

  .cms-heading {
    align-items: flex-start;
    flex-direction: column;
  }

  .list-panel {
    max-height: none;
  }

  .list-panel :deep(.content-list-scroll) {
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
    padding: 12px 14px;
  }

  .cms-heading h1 {
    font-size: 21px;
  }

  .heading-actions,
  .cms-stat-strip {
    display: grid;
    grid-template-columns: 1fr;
    width: 100%;
    justify-content: stretch;
  }

  .cms-stat-strip {
    max-height: 78px;
    overflow: auto;
  }

  .cms-stat-strip span,
  .preview-link {
    width: 100%;
    text-align: center;
  }

  .cms-tabs {
    border-radius: var(--radius-sm);
    padding: 6px;
  }

  .cms-tabs :deep(.el-tabs__header) {
    margin-bottom: 8px;
  }

  .cms-tabs :deep(.el-tabs__nav-wrap) {
    padding: 0;
  }

  .cms-tabs :deep(.el-tabs__nav-prev),
  .cms-tabs :deep(.el-tabs__nav-next),
  .cms-tabs :deep(.el-tabs__active-bar) {
    display: none;
  }

  .cms-tabs :deep(.el-tabs__nav-scroll) {
    overflow: visible;
  }

  .cms-tabs :deep(.el-tabs__nav) {
    display: grid;
    width: 100%;
    float: none;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 6px;
    transform: none !important;
    white-space: normal;
  }

  .cms-tabs :deep(.el-tabs__item) {
    justify-content: center;
    width: 100%;
    height: 36px;
    border: 1px solid var(--color-line);
    border-radius: var(--radius-sm);
    padding: 0 8px;
    background: var(--color-panel);
    font-size: 13px;
  }

  .cms-tabs :deep(.el-tabs__item.is-active) {
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

  .list-panel :deep(.list-toolbar) {
    display: grid;
    grid-template-columns: 1fr;
    gap: 9px;
    min-height: 0;
    margin-bottom: 10px;
    padding-bottom: 10px;
  }

  .list-panel :deep(.list-toolbar strong) {
    font-size: 17px;
  }

  .list-panel :deep(.list-toolbar .el-button) {
    width: 100%;
    min-height: 36px;
  }

  .list-panel :deep(.list-search) {
    min-height: 38px;
    margin-bottom: 10px;
  }

  .list-panel :deep(.content-list-scroll) {
    max-height: 48vh;
    overflow-y: auto;
    padding-right: 2px;
  }

  .list-panel :deep(.content-row) {
    margin-bottom: 8px;
    padding: 10px 11px;
  }

  .list-panel :deep(.content-row strong),
  .list-panel :deep(.content-row span) {
    white-space: normal;
  }

  .list-panel :deep(.content-row strong) {
    display: -webkit-box;
    overflow: hidden;
    line-height: 1.45;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 2;
  }

  .list-panel :deep(.content-row span) {
    display: -webkit-box;
    margin-top: 5px;
    overflow: hidden;
    line-height: 1.45;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 2;
  }

  .list-panel :deep(.list-pager) {
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    gap: 8px;
  }

  .list-panel :deep(.list-pager button) {
    min-height: 34px;
    padding: 0 8px;
  }

  .list-panel :deep(.list-pager span) {
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

  .import-strip input,
  .import-strip a {
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

  .form-actions {
    position: static;
    display: grid;
    grid-template-columns: 1fr;
    margin: 14px 0 0;
    padding: 12px 0 0;
  }

  .form-actions :deep(.el-button) {
    width: 100%;
    margin: 0;
  }
}
</style>
